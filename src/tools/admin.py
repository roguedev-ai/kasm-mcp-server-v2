"""Admin and resource tools for Kasm Workspaces."""

import logging
from typing import Any, Dict, List

from mcp_python.tools import Tool
from pydantic import BaseModel, Field

from ..kasm_api import KasmAPIClient

logger = logging.getLogger(__name__)


class GetAvailableWorkspacesParams(BaseModel):
    """Parameters for get_available_workspaces tool."""
    # No parameters needed for this tool
    pass


class GetAvailableWorkspacesTool(Tool):
    """Get list of available workspace images."""
    
    name = "get_available_workspaces"
    description = (
        "Retrieve a list of all available Kasm workspace images "
        "that can be used to create new sessions."
    )
    input_schema = GetAvailableWorkspacesParams
    
    def __init__(self, kasm_client: KasmAPIClient):
        """Initialize the tool."""
        super().__init__()
        self.kasm_client = kasm_client
        
    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get available workspaces."""
        try:
            logger.info("Retrieving available workspaces")
            
            result = self.kasm_client.get_workspaces()
            
            # Extract relevant workspace information
            workspaces = []
            for workspace in result.get("workspaces", []):
                workspaces.append({
                    "image_name": workspace.get("image_name"),
                    "friendly_name": workspace.get("friendly_name"),
                    "description": workspace.get("description"),
                    "enabled": workspace.get("enabled"),
                    "cores": workspace.get("cores"),
                    "memory": workspace.get("memory"),
                    "gpu_count": workspace.get("gpu_count", 0),
                    "categories": workspace.get("categories", [])
                })
            
            return {
                "success": True,
                "workspaces": workspaces,
                "count": len(workspaces)
            }
            
        except Exception as e:
            logger.error(f"Failed to get available workspaces: {e}")
            return {
                "success": False,
                "error": f"Failed to get workspaces: {str(e)}"
            }


class GetKasmUsersParams(BaseModel):
    """Parameters for get_kasm_users tool."""
    # No parameters needed for this tool
    pass


class GetKasmUsersTool(Tool):
    """Get list of Kasm users."""
    
    name = "get_kasm_users"
    description = "Retrieve a list of all users in the Kasm system."
    input_schema = GetKasmUsersParams
    
    def __init__(self, kasm_client: KasmAPIClient):
        """Initialize the tool."""
        super().__init__()
        self.kasm_client = kasm_client
        
    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get Kasm users."""
        try:
            logger.info("Retrieving Kasm users")
            
            result = self.kasm_client.get_users()
            
            # Extract relevant user information
            users = []
            for user in result.get("users", []):
                users.append({
                    "user_id": user.get("user_id"),
                    "username": user.get("username"),
                    "first_name": user.get("first_name"),
                    "last_name": user.get("last_name"),
                    "email": user.get("email"),
                    "enabled": user.get("enabled"),
                    "locked": user.get("locked"),
                    "last_session": user.get("last_session"),
                    "groups": user.get("groups", [])
                })
            
            return {
                "success": True,
                "users": users,
                "count": len(users)
            }
            
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return {
                "success": False,
                "error": f"Failed to get users: {str(e)}"
            }


class CreateKasmUserParams(BaseModel):
    """Parameters for create_kasm_user tool."""
    
    username: str = Field(description="Username for the new user")
    password: str = Field(description="Password for the new user")
    first_name: str = Field(default="", description="User's first name")
    last_name: str = Field(default="", description="User's last name")


class CreateKasmUserTool(Tool):
    """Create a new Kasm user."""
    
    name = "create_kasm_user"
    description = "Create a new user account in the Kasm system."
    input_schema = CreateKasmUserParams
    
    def __init__(self, kasm_client: KasmAPIClient):
        """Initialize the tool."""
        super().__init__()
        self.kasm_client = kasm_client
        
    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        try:
            params = CreateKasmUserParams(**arguments)
            
            logger.info(f"Creating new user: {params.username}")
            
            result = self.kasm_client.create_user(
                username=params.username,
                password=params.password,
                first_name=params.first_name,
                last_name=params.last_name
            )
            
            return {
                "success": True,
                "user_id": result.get("user_id"),
                "username": params.username,
                "message": f"User '{params.username}' created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return {
                "success": False,
                "error": f"Failed to create user: {str(e)}"
            }
