"""Session management tools for Kasm Workspaces."""

import base64
import logging
from typing import Any, Dict, Optional

from mcp_python.tools import Tool
from pydantic import BaseModel, Field

from ..kasm_api import KasmAPIClient
from ..security import RootsValidator, SecurityError

logger = logging.getLogger(__name__)


# Session Management Tools

class CreateKasmSessionParams(BaseModel):
    """Parameters for create_kasm_session tool."""
    
    image_name: str = Field(description="Name of the workspace image to launch")
    user_id: str = Field(description="User ID requesting the session")
    group_id: str = Field(description="Group ID for the session")


class CreateKasmSessionTool(Tool):
    """Create a new Kasm session with the specified workspace image."""
    
    name = "create_kasm_session"
    description = (
        "Launch a new Kasm session with a specified workspace image. "
        "Returns the session ID and connection details."
    )
    input_schema = CreateKasmSessionParams
    
    def __init__(self, kasm_client: KasmAPIClient):
        """Initialize the tool."""
        super().__init__()
        self.kasm_client = kasm_client
        
    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Kasm session."""
        try:
            params = CreateKasmSessionParams(**arguments)
            
            logger.info(f"Creating Kasm session with image: {params.image_name}")
            
            result = self.kasm_client.request_kasm(
                image_name=params.image_name,
                user_id=params.user_id,
                group_id=params.group_id
            )
            
            return {
                "success": True,
                "kasm_id": result.get("kasm_id"),
                "session_url": result.get("kasm_url"),
                "status": result.get("status", "created"),
                "image_name": params.image_name
            }
            
        except Exception as e:
            logger.error(f"Failed to create Kasm session: {e}")
            return {
                "success": False,
                "error": f"Failed to create session: {str(e)}"
            }


class DestroyKasmSessionParams(BaseModel):
    """Parameters for destroy_kasm_session tool."""
    
    kasm_id: str = Field(description="ID of the Kasm session to destroy")
    user_id: str = Field(description="User ID owning the session")


class DestroyKasmSessionTool(Tool):
    """Destroy an existing Kasm session."""
    
    name = "destroy_kasm_session"
    description = "Terminate an existing Kasm session."
    input_schema = DestroyKasmSessionParams
    
    def __init__(self, kasm_client: KasmAPIClient):
        """Initialize the tool."""
        super().__init__()
        self.kasm_client = kasm_client
        
    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Destroy a Kasm session."""
        try:
            params = DestroyKasmSessionParams(**arguments)
            
            logger.info(f"Destroying Kasm session: {params.kasm_id}")
            
            result = self.kasm_client.destroy_kasm(
                kasm_id=params.kasm_id,
                user_id=params.user_id
            )
            
            return {
                "success": True,
                "kasm_id": params.kasm_id,
                "status": "destroyed",
                "message": "Session terminated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to destroy Kasm session: {e}")
            return {
                "success": False,
                "error": f"Failed to destroy session: {str(e)}"
            }


class GetSessionStatusParams(BaseModel):
    """Parameters for get_session_status tool."""
    
    kasm_id: str = Field(description="ID of the Kasm session")
    user_id: str = Field(description="User ID owning the session")


class GetSessionStatusTool(Tool):
    """Get the status of a Kasm session."""
    
    name = "get_session_status"
    description = "Check the current status of a Kasm session."
    input_schema = GetSessionStatusParams
    
    def __init__(self, kasm_client: KasmAPIClient):
        """Initialize the tool."""
        super().__init__()
        self.kasm_client = kasm_client
        
    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get session status."""
        try:
            params = GetSessionStatusParams(**arguments)
            
            logger.info(f"Getting status for Kasm session: {params.kasm_id}")
            
            result = self.kasm_client.get_kasm_status(
                kasm_id=params.kasm_id,
                user_id=params.user_id
            )
            
            return {
                "success": True,
                "kasm_id": params.kasm_id,
                "status": result.get("status"),
                "operational_status": result.get("operational_status"),
                "session_url": result.get("kasm_url"),
                "created_time": result.get("created_time"),
                "last_activity": result.get("last_activity")
            }
            
        except Exception as e:
            logger.error(f"Failed to get session status: {e}")
            return {
                "success": False,
                "error": f"Failed to get session status: {str(e)}"
            }


# File Operation Tools (Abstractions over execute_kasm_command)

class ReadKasmFileParams(BaseModel):
    """Parameters for read_kasm_file tool."""
    
    kasm_id: str = Field(description="ID of the Kasm session")
    user_id: str = Field(description="User ID owning the session")
    file_path: str = Field(description="Path to the file to read")


class ReadKasmFileTool(Tool):
    """Read a file from a Kasm session."""
    
    name = "read_kasm_file"
    description = (
        "Read the contents of a file from a Kasm session. "
        "The file path must be within allowed security boundaries."
    )
    input_schema = ReadKasmFileParams
    
    def __init__(self, kasm_client: KasmAPIClient, roots_validator: RootsValidator):
        """Initialize the tool."""
        super().__init__()
        self.kasm_client = kasm_client
        self.roots_validator = roots_validator
        
    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Read file from Kasm session."""
        try:
            params = ReadKasmFileParams(**arguments)
            
            # Validate file path
            self.roots_validator.validate_file_operation(
                params.file_path, 
                operation="read"
            )
            
            logger.info(f"Reading file from Kasm session {params.kasm_id}: {params.file_path}")
            
            # Use cat command to read file
            command = f"cat '{params.file_path}'"
            
            result = self.kasm_client.exec_command(
                kasm_id=params.kasm_id,
                user_id=params.user_id,
                command=command
            )
            
            if result.get("exit_code") == 0:
                return {
                    "success": True,
                    "file_path": params.file_path,
                    "content": result.get("output", ""),
                    "size": len(result.get("output", ""))
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to read file: {result.get('error', 'Unknown error')}"
                }
                
        except SecurityError as e:
            logger.warning(f"Security violation reading file: {e}")
            return {
                "success": False,
                "error": f"Security violation: {str(e)}",
                "error_type": "security"
            }
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}"
            }


class WriteKasmFileParams(BaseModel):
    """Parameters for write_kasm_file tool."""
    
    kasm_id: str = Field(description="ID of the Kasm session")
    user_id: str = Field(description="User ID owning the session")
    file_path: str = Field(description="Path where the file should be written")
    content: str = Field(description="Content to write to the file")


class WriteKasmFileTool(Tool):
    """Write content to a file in a Kasm session."""
    
    name = "write_kasm_file"
    description = (
        "Write content to a file in a Kasm session. "
        "The file path must be within allowed security boundaries."
    )
    input_schema = WriteKasmFileParams
    
    def __init__(self, kasm_client: KasmAPIClient, roots_validator: RootsValidator):
        """Initialize the tool."""
        super().__init__()
        self.kasm_client = kasm_client
        self.roots_validator = roots_validator
        
    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Write file to Kasm session."""
        try:
            params = WriteKasmFileParams(**arguments)
            
            # Validate file path
            self.roots_validator.validate_file_operation(
                params.file_path,
                operation="write"
            )
            
            logger.info(f"Writing file to Kasm session {params.kasm_id}: {params.file_path}")
            
            # Encode content to base64 to handle special characters
            encoded_content = base64.b64encode(params.content.encode()).decode()
            
            # Create directory if needed and write file
            commands = [
                f"mkdir -p $(dirname '{params.file_path}')",
                f"echo '{encoded_content}' | base64 -d > '{params.file_path}'"
            ]
            
            for command in commands:
                result = self.kasm_client.exec_command(
                    kasm_id=params.kasm_id,
                    user_id=params.user_id,
                    command=command
                )
                
                if result.get("exit_code") != 0:
                    return {
                        "success": False,
                        "error": f"Failed to write file: {result.get('error', 'Unknown error')}"
                    }
            
            return {
                "success": True,
                "file_path": params.file_path,
                "size": len(params.content),
                "message": f"File written successfully to {params.file_path}"
            }
                
        except SecurityError as e:
            logger.warning(f"Security violation writing file: {e}")
            return {
                "success": False,
                "error": f"Security violation: {str(e)}",
                "error_type": "security"
            }
        except Exception as e:
            logger.error(f"Failed to write file: {e}")
            return {
                "success": False,
                "error": f"Failed to write file: {str(e)}"
            }
