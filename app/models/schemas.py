# app/models/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class OperationType(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

class UserRequest(BaseModel):
    query: str
    user_id: str = "default_user"

class BotResponse(BaseModel):
    response: str
    operation_type: OperationType
    requires_approval: bool = False
    proposed_changes: Optional[Dict[str, Any]] = None
    query_results: Optional[List[Dict[str, Any]]] = None

class ApprovalRequest(BaseModel):
    request_id: str
    user_id: str
    approved: bool