# app/database/mock_db2.py
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class ProjectsDB:
    def __init__(self):
        self.projects = [
            {"id": 1, "name": "Website Redesign", "status": "active", "budget": 50000, "manager": "John Doe"},
            {"id": 2, "name": "Mobile App", "status": "completed", "budget": 75000, "manager": "Jane Smith"},
            {"id": 3, "name": "AI Integration", "status": "planning", "budget": 100000, "manager": "Bob Johnson"}
        ]
        self.next_id = 4

    def get_all_projects(self) -> List[Dict[str, Any]]:
        return self.projects

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        return next((project for project in self.projects if project["id"] == project_id), None)

    def get_projects_by_status(self, status: str) -> List[Dict[str, Any]]:
        return [project for project in self.projects if project["status"].lower() == status.lower()]

    def create_project(self, name: str, status: str, budget: float, manager: str) -> Dict[str, Any]:
        project = {
            "id": self.next_id,
            "name": name,
            "status": status,
            "budget": budget,
            "manager": manager
        }
        self.projects.append(project)
        self.next_id += 1
        return project

    def update_project(self, project_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for project in self.projects:
            if project["id"] == project_id:
                project.update(updates)
                return project
        return None

    def delete_project(self, project_id: int) -> bool:
        for i, project in enumerate(self.projects):
            if project["id"] == project_id:
                self.projects.pop(i)
                return True
        return False