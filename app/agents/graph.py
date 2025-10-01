# app/agents/graph.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List, TypedDict
import json
import uuid
from app.agents.tools import UserQueryTool, ProjectQueryTool, UserManagementTool, ProjectManagementTool
from app.models.schemas import OperationType
from app.config import settings

# Initialize tools and executor
tools = [UserQueryTool(), ProjectQueryTool(), UserManagementTool(), ProjectManagementTool()]
tool_executor = ToolExecutor(tools)

# Define state
class AgentState(TypedDict):
    messages: List
    current_tool: str
    tool_input: Dict[str, Any]
    requires_approval: bool
    operation_type: str
    proposed_changes: Dict[str, Any]
    query_results: List[Dict[str, Any]]

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=settings.google_api_key
)
llm_with_tools = llm.bind_tools(tools)

def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    last_message = messages[-1]
    
    # If there's a function call, continue to tools
    if getattr(last_message, 'tool_calls', None):
        return "continue"
    # If human response is needed for approval
    elif state.get("requires_approval", False):
        return "human_approval"
    else:
        return "end"

def call_model(state: AgentState) -> AgentState:
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    
    # Check if this is a CUD operation that requires approval
    requires_approval = False
    operation_type = OperationType.READ
    proposed_changes = {}
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_name = response.tool_calls[0]['name']
        if any(op in tool_name for op in ['create', 'update', 'delete', 'management']):
            requires_approval = True
            if 'create' in tool_name:
                operation_type = OperationType.CREATE
            elif 'update' in tool_name:
                operation_type = OperationType.UPDATE
            elif 'delete' in tool_name:
                operation_type = OperationType.DELETE
            
            # Extract proposed changes
            if response.tool_calls[0].get('args'):
                proposed_changes = response.tool_calls[0]['args']
    
    return {
        "messages": [response],
        "requires_approval": requires_approval,
        "operation_type": operation_type,
        "proposed_changes": proposed_changes
    }

def call_tool(state: AgentState) -> AgentState:
    messages = state["messages"]
    last_message = messages[-1]
    
    tool_calls = last_message.tool_calls
    results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call['name']
        tool_input = tool_call['args']
        result = tool_executor.invoke(
            {"tool": tool_name, "tool_input": tool_input}
        )
        results.append(f"{tool_name} result: {result}")
    
    # For read operations, store results
    query_results = []
    if state.get("operation_type") == OperationType.READ:
        query_results = [{"result": str(result)} for result in results]
    
    return {
        "messages": [AIMessage(content="\n".join(results))],
        "query_results": query_results
    }

def human_approval_step(state: AgentState) -> AgentState:
    # This would typically interface with a human approval system
    # For now, we'll simulate approval for demo purposes
    messages = state["messages"]
    
    approval_message = "This operation requires human approval. Would you like to proceed? (yes/no)"
    
    return {
        "messages": [HumanMessage(content=approval_message)],
        "requires_approval": True
    }

def process_approval(state: AgentState, approved: bool) -> AgentState:
    if approved:
        # Execute the approved operation
        messages = state["messages"]
        last_ai_message = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None)
        
        if last_ai_message and hasattr(last_ai_message, 'tool_calls'):
            return call_tool({"messages": [last_ai_message], "operation_type": state["operation_type"]})
        else:
            return {
                "messages": [AIMessage(content="Approved but no operation to execute")],
                "requires_approval": False
            }
    else:
        return {
            "messages": [AIMessage(content="Operation cancelled by user")],
            "requires_approval": False
        }

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tool)
workflow.add_node("human_approval", human_approval_step)

# Add edges
workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "human_approval": "human_approval",
        "end": END
    }
)

workflow.add_edge("tools", END)
workflow.add_conditional_edges(
    "human_approval",
    lambda state: "process_approval",  # This would connect to approval processing
    {"process_approval": "tools"}
)

# Compile the graph
graph = workflow.compile()