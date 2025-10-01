# app/agents/tools.py
from langchain.tools import BaseTool
from typing import Optional, Type, List, Dict, Any
from pydantic import BaseModel, Field
from app.database.mock_db1 import UsersDB
from app.database.mock_db2 import ProjectsDB
from app.models.schemas import OperationType

# Initialize databases
users_db = UsersDB()
projects_db = ProjectsDB()

class UserQueryInput(BaseModel):
    query_type: str = Field(description="Type of query: 'all_users', 'user_by_id', or 'users_by_department'")
    user_id: Optional[int] = Field(default=None, description="User ID for specific query")
    department: Optional[str] = Field(default=None, description="Department name for filtering")

class ProjectQueryInput(BaseModel):
    query_type: str = Field(description="Type of query: 'all_projects', 'project_by_id', or 'projects_by_status'")
    project_id: Optional[int] = Field(default=None, description="Project ID for specific query")
    status: Optional[str] = Field(default=None, description="Project status for filtering")

class UserManagementInput(BaseModel):
    operation: str = Field(description="Operation: 'create_user', 'update_user', or 'delete_user'")
    user_id: Optional[int] = Field(default=None, description="User ID for update/delete")
    name: Optional[str] = Field(default=None, description="User name for creation")
    email: Optional[str] = Field(default=None, description="User email for creation")
    department: Optional[str] = Field(default=None, description="User department for creation")
    updates: Optional[Dict[str, Any]] = Field(default=None, description="Updates for user")

class ProjectManagementInput(BaseModel):
    operation: str = Field(description="Operation: 'create_project', 'update_project', or 'delete_project'")
    project_id: Optional[int] = Field(default=None, description="Project ID for update/delete")
    name: Optional[str] = Field(default=None, description="Project name for creation")
    status: Optional[str] = Field(default=None, description="Project status for creation")
    budget: Optional[float] = Field(default=None, description="Project budget for creation")
    manager: Optional[str] = Field(default=None, description="Project manager for creation")
    updates: Optional[Dict[str, Any]] = Field(default=None, description="Updates for project")

class UserQueryTool(BaseTool):
    name = "user_query_tool"
    description = "Query user information from the users database. Use for read operations only."
    args_schema: Type[BaseModel] = UserQueryInput

    def _run(self, query_type: str, user_id: Optional[int] = None, department: Optional[str] = None) -> str:
        try:
            if query_type == "all_users":
                results = users_db.get_all_users()
            elif query_type == "user_by_id" and user_id:
                result = users_db.get_user_by_id(user_id)
                results = [result] if result else []
            elif query_type == "users_by_department" and department:
                results = users_db.get_users_by_department(department)
            else:
                return "Invalid query parameters for user query"
            
            return f"User query results: {results}" if results else "No users found matching the criteria"
        except Exception as e:
            return f"Error querying users: {str(e)}"

class ProjectQueryTool(BaseTool):
    name = "project_query_tool"
    description = "Query project information from the projects database. Use for read operations only."
    args_schema: Type[BaseModel] = ProjectQueryInput

    def _run(self, query_type: str, project_id: Optional[int] = None, status: Optional[str] = None) -> str:
        try:
            if query_type == "all_projects":
                results = projects_db.get_all_projects()
            elif query_type == "project_by_id" and project_id:
                result = projects_db.get_project_by_id(project_id)
                results = [result] if result else []
            elif query_type == "projects_by_status" and status:
                results = projects_db.get_projects_by_status(status)
            else:
                return "Invalid query parameters for project query"
            
            return f"Project query results: {results}" if results else "No projects found matching the criteria"
        except Exception as e:
            return f"Error querying projects: {str(e)}"

class UserManagementTool(BaseTool):
    name = "user_management_tool"
    description = "Manage users (create_user, update_user, delete_user) - requires approval for all operations"
    args_schema: Type[BaseModel] = UserManagementInput

    def _run(self, operation: str, user_id: Optional[int] = None, name: Optional[str] = None, 
             email: Optional[str] = None, department: Optional[str] = None, updates: Optional[Dict[str, Any]] = None) -> str:
        try:
            if operation == "create_user":
                if not all([name, email, department]):
                    return "Missing required fields for user creation: name, email, department"
                result = users_db.create_user(name, email, department)
                return f"User created successfully: {result}"
            elif operation == "update_user" and user_id and updates:
                result = users_db.update_user(user_id, updates)
                return f"User updated successfully: {result}" if result else "User not found"
            elif operation == "delete_user" and user_id:
                success = users_db.delete_user(user_id)
                return "User deleted successfully" if success else "User not found"
            else:
                return "Invalid operation or missing parameters for user management"
        except Exception as e:
            return f"Error managing user: {str(e)}"

class ProjectManagementTool(BaseTool):
    name = "project_management_tool"
    description = "Manage projects (create_project, update_project, delete_project) - requires approval for all operations"
    args_schema: Type[BaseModel] = ProjectManagementInput

    def _run(self, operation: str, project_id: Optional[int] = None, name: Optional[str] = None,
             status: Optional[str] = None, budget: Optional[float] = None, manager: Optional[str] = None,
             updates: Optional[Dict[str, Any]] = None) -> str:
        try:
            if operation == "create_project":
                if not all([name, status, budget, manager]):
                    return "Missing required fields for project creation: name, status, budget, manager"
                result = projects_db.create_project(name, status, budget, manager)
                return f"Project created successfully: {result}"
            elif operation == "update_project" and project_id and updates:
                result = projects_db.update_project(project_id, updates)
                return f"Project updated successfully: {result}" if result else "Project not found"
            elif operation == "delete_project" and project_id:
                success = projects_db.delete_project(project_id)
                return "Project deleted successfully" if success else "Project not found"
            else:
                return "Invalid operation or missing parameters for project management"
        except Exception as e:
            return f"Error managing project: {str(e)}"