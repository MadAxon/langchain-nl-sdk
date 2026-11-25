"""
Mock Service API for User Management.
Provides persistent state using a local JSON file (db.json).
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.json")

INITIAL_DATA = [
    {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "status": "active",
        "created_at": "2026-11-20T10:00:00"
    },
    {
        "id": 2,
        "name": "Bob",
        "email": "bob@example.com",
        "status": "inactive",
        "created_at": "2026-11-21T12:30:00"
    }
]


class MockUserService:
    """Mock API service providing CRUD operations over Users stored in db.json."""

    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self) -> None:
        if not os.path.exists(self.db_path):
            self._save_data(INITIAL_DATA)

    def _load_data(self) -> List[Dict[str, Any]]:
        self._ensure_db()
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return INITIAL_DATA.copy()

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_user(self, name: str, email: str = "", status: str = "active") -> Dict[str, Any]:
        """Create a new user entity."""
        if not name or not name.strip():
            return {"success": False, "error": "Name is required to create a user."}

        users = self._load_data()
        next_id = max((u["id"] for u in users), default=0) + 1
        new_user = {
            "id": next_id,
            "name": name.strip(),
            "email": email.strip() if email else f"{name.strip().lower()}@example.com",
            "status": status.strip().lower(),
            "created_at": datetime.now().isoformat()
        }
        users.append(new_user)
        self._save_data(users)
        return {"success": True, "data": new_user, "message": f"User '{new_user['name']}' created successfully."}

    def get_user(self, user_id: Optional[int] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve user by user_id or name."""
        if user_id is None and not name:
            return {"success": False, "error": "Either user_id or name must be specified to find a user."}

        users = self._load_data()
        for u in users:
            if user_id is not None and u["id"] == user_id:
                return {"success": True, "data": u}
            if name and u["name"].lower() == name.strip().lower():
                return {"success": True, "data": u}

        identifier = f"ID={user_id}" if user_id is not None else f"name='{name}'"
        return {"success": False, "error": f"User with {identifier} not found."}

    def update_user_status(self, new_status: str, user_id: Optional[int] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """Update status of a user (e.g. active, suspended, inactive)."""
        if not new_status:
            return {"success": False, "error": "new_status is required."}

        users = self._load_data()
        target_user = None
        for u in users:
            if user_id is not None and u["id"] == user_id:
                target_user = u
                break
            if name and u["name"].lower() == name.strip().lower():
                target_user = u
                break

        if not target_user:
            identifier = f"ID={user_id}" if user_id is not None else f"name='{name}'"
            return {"success": False, "error": f"User with {identifier} not found."}

        old_status = target_user["status"]
        target_user["status"] = new_status.strip().lower()
        self._save_data(users)
        return {
            "success": True,
            "data": target_user,
            "message": f"Status of user '{target_user['name']}' updated from '{old_status}' to '{new_status}'."
        }

    def list_users(self, status: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """List users with optional status filtering and limit."""
        users = self._load_data()
        if status:
            filtered = [u for u in users if u["status"] == status.strip().lower()]
        else:
            filtered = users

        paginated = filtered[:limit]
        return {
            "success": True,
            "data": paginated,
            "total_matched": len(filtered),
            "total_system_users": len(users)
        }


# Global instance of service
service = MockUserService()
