# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import uuid
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import aiofiles
import os

# Import from your project structure
from app.models.schemas import UserRequest, BotResponse, ApprovalRequest, OperationType
from app.database.mock_db1 import UsersDB
from app.database.mock_db2 import ProjectsDB

app = FastAPI(title="Mini Agentic Bot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize databases
users_db = UsersDB()
projects_db = ProjectsDB()

# Store pending approvals
pending_approvals: Dict[str, Dict[str, Any]] = {}

# Add after app initialization
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Add these new routes before the existing API routes
@app.get("/")
async def read_root(request: Request):
    """Main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat")
async def chat_interface(request: Request):
    """Alternative chat interface"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/approvals")
async def approvals_interface(request: Request):
    """Approvals management interface"""
    return templates.TemplateResponse("approvals.html", {"request": request})

@app.get("/data")
async def data_interface(request: Request):
    """Data viewing interface"""
    return templates.TemplateResponse("index.html", {"request": request})


def process_natural_language_query(query: str) -> BotResponse:
    """Process natural language queries using the agentic workflow"""
    query_lower = query.lower()
    
    # Read operations (no approval needed)
    if any(term in query_lower for term in ["show", "list", "get", "find", "display"]):
        if "user" in query_lower:
            if "engineering" in query_lower:
                results = users_db.get_users_by_department("Engineering")
                return BotResponse(
                    response=f"Found {len(results)} users in Engineering department: {results}",
                    operation_type=OperationType.READ,
                    query_results=results
                )
            elif "all" in query_lower or "every" in query_lower:
                results = users_db.get_all_users()
                return BotResponse(
                    response=f"Found {len(results)} users: {results}",
                    operation_type=OperationType.READ,
                    query_results=results
                )
            else:
                results = users_db.get_all_users()
                return BotResponse(
                    response=f"Here are all users: {results}",
                    operation_type=OperationType.READ,
                    query_results=results
                )
        
        elif "project" in query_lower:
            if "active" in query_lower:
                results = projects_db.get_projects_by_status("active")
                return BotResponse(
                    response=f"Found {len(results)} active projects: {results}",
                    operation_type=OperationType.READ,
                    query_results=results
                )
            elif "all" in query_lower or "every" in query_lower:
                results = projects_db.get_all_projects()
                return BotResponse(
                    response=f"Found {len(results)} projects: {results}",
                    operation_type=OperationType.READ,
                    query_results=results
                )
            else:
                results = projects_db.get_all_projects()
                return BotResponse(
                    response=f"Here are all projects: {results}",
                    operation_type=OperationType.READ,
                    query_results=results
                )
    
    # Create operations (require approval)
    elif any(term in query_lower for term in ["create", "add", "new", "make"]):
        request_id = str(uuid.uuid4())
        
        if "user" in query_lower:
            proposed_changes = {
                "operation": "create_user",
                "entity": "user",
                "details": "New user creation based on query analysis"
            }
            pending_approvals[request_id] = {
                "operation": "create_user",
                "query": query,
                "proposed_changes": proposed_changes
            }
            
            return BotResponse(
                response=f"Approval required to create new user. Request ID: {request_id}",
                operation_type=OperationType.CREATE,
                requires_approval=True,
                proposed_changes=proposed_changes
            )
        
        elif "project" in query_lower:
            proposed_changes = {
                "operation": "create_project",
                "entity": "project", 
                "details": "New project creation based on query analysis"
            }
            pending_approvals[request_id] = {
                "operation": "create_project",
                "query": query,
                "proposed_changes": proposed_changes
            }
            
            return BotResponse(
                response=f"Approval required to create new project. Request ID: {request_id}",
                operation_type=OperationType.CREATE,
                requires_approval=True,
                proposed_changes=proposed_changes
            )
    
    # Update operations (require approval)
    elif any(term in query_lower for term in ["update", "modify", "change", "edit"]):
        request_id = str(uuid.uuid4())
        proposed_changes = {
            "operation": "update",
            "entity": "unknown",
            "details": "Update operation based on query analysis"
        }
        pending_approvals[request_id] = {
            "operation": "update",
            "query": query,
            "proposed_changes": proposed_changes
        }
        
        return BotResponse(
            response=f"Approval required for update operation. Request ID: {request_id}",
            operation_type=OperationType.UPDATE,
            requires_approval=True,
            proposed_changes=proposed_changes
        )
    
    # Delete operations (require approval)
    elif any(term in query_lower for term in ["delete", "remove", "destroy"]):
        request_id = str(uuid.uuid4())
        proposed_changes = {
            "operation": "delete",
            "entity": "unknown",
            "details": "Delete operation based on query analysis"
        }
        pending_approvals[request_id] = {
            "operation": "delete",
            "query": query,
            "proposed_changes": proposed_changes
        }
        
        return BotResponse(
            response=f"Approval required for delete operation. Request ID: {request_id}",
            operation_type=OperationType.DELETE,
            requires_approval=True,
            proposed_changes=proposed_changes
        )
    
    # Default response
    else:
        return BotResponse(
            response="I can help you with: \n- Showing users/projects (READ)\n- Creating new users/projects (CREATE)\n- Updating existing data (UPDATE)\n- Removing data (DELETE)\n\nTry: 'Show all users' or 'Create a new project'",
            operation_type=OperationType.READ
        )

@app.post("/query", response_model=BotResponse)
async def process_query(user_request: UserRequest):
    try:
        return process_natural_language_query(user_request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/approve")
async def approve_operation(approval_request: ApprovalRequest):
    try:
        pending_request = pending_approvals.get(approval_request.request_id)
        
        if not pending_request:
            raise HTTPException(status_code=404, detail="Approval request not found")
        
        if approval_request.approved:
            operation = pending_request["operation"]
            
            # Execute the approved operation
            if operation == "create_user":
                result = users_db.create_user("New User", "new@example.com", "General")
                message = f"User created successfully: {result}"
            elif operation == "create_project":
                result = projects_db.create_project("New Project", "planning", 10000, "Manager")
                message = f"Project created successfully: {result}"
            else:
                message = f"Operation '{operation}' executed successfully"
            
            del pending_approvals[approval_request.request_id]
            
            return {
                "status": "approved",
                "message": message,
                "request_id": approval_request.request_id
            }
        else:
            del pending_approvals[approval_request.request_id]
            
            return {
                "status": "rejected",
                "message": "Operation was rejected by user",
                "request_id": approval_request.request_id
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing approval: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "Mini Agentic Bot",
        "users_count": len(users_db.users),
        "projects_count": len(projects_db.projects)
    }

@app.get("/pending-approvals")
async def get_pending_approvals():
    return {
        "pending_approvals": {
            request_id: {
                "operation": data["operation"],
                "query": data["query"]
            } 
            for request_id, data in pending_approvals.items()
        }
    }

@app.get("/data/users")
async def get_all_users():
    return {"users": users_db.get_all_users()}

@app.get("/data/projects")
async def get_all_projects():
    return {"projects": projects_db.get_all_projects()}

@app.get("/")
async def root():
    return {
        "message": "Mini Agentic Bot API is running!",
        "endpoints": {
            "POST /query": "Process natural language queries",
            "POST /approve": "Approve pending operations", 
            "GET /health": "Service health check",
            "GET /pending-approvals": "List pending approvals",
            "GET /data/users": "Get all users",
            "GET /data/projects": "Get all projects"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)