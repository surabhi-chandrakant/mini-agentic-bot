# app/database/mock_db1.py
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class UsersDB:
    def __init__(self):
        self.users = [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "department": "Engineering"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "department": "Marketing"},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "department": "Sales"}
        ]
        self.next_id = 4

    def get_all_users(self) -> List[Dict[str, Any]]:
        return self.users

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        return next((user for user in self.users if user["id"] == user_id), None)

    def get_users_by_department(self, department: str) -> List[Dict[str, Any]]:
        return [user for user in self.users if user["department"].lower() == department.lower()]

    def create_user(self, name: str, email: str, department: str) -> Dict[str, Any]:
        user = {
            "id": self.next_id,
            "name": name,
            "email": email,
            "department": department
        }
        self.users.append(user)
        self.next_id += 1
        return user

    def update_user(self, user_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for user in self.users:
            if user["id"] == user_id:
                user.update(updates)
                return user
        return None

    def delete_user(self, user_id: int) -> bool:
        for i, user in enumerate(self.users):
            if user["id"] == user_id:
                self.users.pop(i)
                return True
        return False