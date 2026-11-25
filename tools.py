"""
LangChain Tools for interacting with MockUserService.
Each tool handles a specific API operation, logs debug information,
and returns a structured JSON string.
"""

import json
import logging
from typing import Any, Dict, Optional, Union
from langchain_core.tools import tool
from mock_service import service

# Configure logger for tool debugging
logger = logging.getLogger("nl_sdk.tools")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[DEBUG TOOL] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _log_tool_call(tool_name: str, args: Dict[str, Any], result_str: str) -> None:
    """Outputs tool invocation arguments and results for debugging."""
    logger.info(f"{tool_name}({args}) -> {result_str}")


@tool
def create_user(name: str, email: Optional[str] = None, status: str = "active") -> str:
    """Create a new user in the service API.
    
    Args:
        name: Name of the user (required).
        email: Email address of the user. If not provided, a default email is generated.
        status: Initial user status (default: 'active').
    """
    args = {"name": name, "email": email, "status": status}
    result = service.create_user(name=name, email=email or "", status=status or "active")
    res_str = json.dumps(result, ensure_ascii=False)
    _log_tool_call("create_user", args, res_str)
    return res_str


@tool
def get_user(user_id: Optional[Union[int, str]] = None, name: Optional[str] = None) -> str:
    """Retrieve details of a user by user_id or by name.
    
    Args:
        user_id: The ID of the user to look up.
        name: The name of the user to look up (used if ID is unknown).
    """
    parsed_id: Optional[int] = None
    if user_id is not None:
        try:
            parsed_id = int(user_id)
        except (ValueError, TypeError):
            parsed_id = None

    args = {"user_id": parsed_id, "name": name}
    result = service.get_user(user_id=parsed_id, name=name)
    res_str = json.dumps(result, ensure_ascii=False)
    _log_tool_call("get_user", args, res_str)
    return res_str


@tool
def update_user_status(new_status: str, user_id: Optional[Union[int, str]] = None, name: Optional[str] = None) -> str:
    """Update status (e.g. 'active', 'inactive', 'suspended', 'blocked') for a user.
    
    Args:
        new_status: The new status string to set.
        user_id: The ID of the user.
        name: The name of the user (used if ID is unknown).
    """
    parsed_id: Optional[int] = None
    if user_id is not None:
        try:
            parsed_id = int(user_id)
        except (ValueError, TypeError):
            parsed_id = None

    args = {"new_status": new_status, "user_id": parsed_id, "name": name}
    result = service.update_user_status(new_status=new_status, user_id=parsed_id, name=name)
    res_str = json.dumps(result, ensure_ascii=False)
    _log_tool_call("update_user_status", args, res_str)
    return res_str


@tool
def list_users(status: Optional[str] = None, limit: Optional[Union[int, str]] = 10) -> str:
    """List users from the service API with optional status filter.
    
    Args:
        status: Optional filter by status ('active', 'inactive', 'suspended', etc.).
        limit: Maximum number of users to return (default: 10).
    """
    parsed_limit = 10
    if limit is not None:
        try:
            parsed_limit = int(limit)
        except (ValueError, TypeError):
            parsed_limit = 10

    clean_status = status.strip() if isinstance(status, str) and status.strip().lower() not in ("none", "all", "") else None

    args = {"status": clean_status, "limit": parsed_limit}
    result = service.list_users(status=clean_status, limit=parsed_limit)
    res_str = json.dumps(result, ensure_ascii=False)
    _log_tool_call("list_users", args, res_str)
    return res_str


ALL_TOOLS = [create_user, get_user, update_user_status, list_users]
