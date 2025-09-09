"""Command execution tool for Kasm sessions."""

import logging
from typing import Any, Dict, Optional

from mcp_python.tools import Tool
from pydantic import BaseModel, Field

from ..kasm_api import KasmAPIClient
from ..security import RootsValidator, SecurityError

logger = logging.getLogger(__name__)


class ExecuteKasmCommandParams(BaseModel):
    """Parameters for execute_kasm_command tool."""
    
    kasm_id: str = Field(description="ID of the Kasm session")
    user_id: str = Field(description="User ID owning the session")
    command: str = Field(description="Command to execute in the session")
    working_dir: Optional[str] = Field(
        default=None,
        description="Working directory for command execution"
    )


class ExecuteKasmCommandTool(Tool):
    """
    Execute a command inside a Kasm session with security boundaries.
    
    This is the most powerful tool, providing direct command execution
    within a containerized environment while enforcing security through
    the MCP Roots mechanism.
    """
    
    name = "execute_kasm_command"
    description = (
        "Execute a shell command inside a Kasm session. "
        "Commands are validated against security boundaries to prevent "
        "unauthorized access outside allowed directories."
    )
    input_schema = ExecuteKasmCommandParams
    
    def __init__(self, kasm_client: KasmAPIClient, roots_validator: RootsValidator):
        """
        Initialize the tool.
        
        Args:
            kasm_client: Kasm API client instance
            roots_validator: Security validator for paths and commands
        """
        super().__init__()
        self.kasm_client = kasm_client
        self.roots_validator = roots_validator
        
    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the command in the Kasm session.
        
        Args:
            arguments: Tool arguments containing kasm_id, user_id, command, and optional working_dir
            
        Returns:
            Command execution results
        """
        try:
            # Parse and validate arguments
            params = ExecuteKasmCommandParams(**arguments)
            
            # Validate command against security rules
            self.roots_validator.validate_command(
                params.command,
                params.working_dir
            )
            
            logger.info(
                f"Executing command in Kasm session {params.kasm_id}: {params.command}"
            )
            
            # Execute command via Kasm API
            result = self.kasm_client.exec_command(
                kasm_id=params.kasm_id,
                user_id=params.user_id,
                command=params.command,
                working_dir=params.working_dir
            )
            
            # Format response
            return {
                "success": True,
                "kasm_id": params.kasm_id,
                "command": params.command,
                "output": result.get("output", ""),
                "exit_code": result.get("exit_code", 0),
                "error": result.get("error", None)
            }
            
        except SecurityError as e:
            logger.warning(f"Security violation: {e}")
            return {
                "success": False,
                "error": f"Security violation: {str(e)}",
                "error_type": "security"
            }
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "success": False,
                "error": f"Command execution failed: {str(e)}",
                "error_type": "execution"
            }
