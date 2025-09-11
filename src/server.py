"""Kasm MCP Server - Main server implementation using official MCP SDK."""

import os
import sys
import logging
from typing import Optional
import traceback

from dotenv import load_dotenv

# Try different import paths for MCP SDK
try:
    from mcp.server.fastmcp import FastMCP
    logger = logging.getLogger(__name__)
    logger.info("Successfully imported FastMCP from mcp.server.fastmcp")
except ImportError as e:
    try:
        from mcp.server import Server as FastMCP
        logger = logging.getLogger(__name__)
        logger.info("Successfully imported Server as FastMCP from mcp.server")
    except ImportError:
        try:
            from mcp import FastMCP
            logger = logging.getLogger(__name__)
            logger.info("Successfully imported FastMCP from mcp")
        except ImportError:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to import MCP SDK: {e}")
            logger.error("Please ensure 'mcp' package is installed: pip install mcp")
            sys.exit(1)

from .kasm_api import KasmAPIClient
from .security import RootsValidator, SecurityError

# Load environment variables
load_dotenv()

# Configure logging with debug level for troubleshooting
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("=" * 60)
logger.info("Kasm MCP Server Starting...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Environment file loaded: {os.path.exists('.env')}")
logger.info("=" * 60)

# Initialize FastMCP server
try:
    mcp = FastMCP(
        name="Kasm MCP Server"
    )
    logger.info("FastMCP server instance created successfully")
except Exception as e:
    logger.error(f"Failed to create FastMCP instance: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

# Global instances (will be initialized in main)
kasm_client: Optional[KasmAPIClient] = None
roots_validator: Optional[RootsValidator] = None


def initialize_clients():
    """Initialize Kasm API client and security validator."""
    global kasm_client, roots_validator
    
    # Get configuration from environment
    api_url = os.getenv("KASM_API_URL", "https://kasm.example.com")
    api_key = os.getenv("KASM_API_KEY", "")
    api_secret = os.getenv("KASM_API_SECRET", "")
    
    if not api_key or not api_secret:
        raise ValueError("KASM_API_KEY and KASM_API_SECRET must be set")
    
    # Initialize clients
    kasm_client = KasmAPIClient(api_url, api_key, api_secret)
    
    # Initialize security validator with allowed roots
    allowed_roots = os.getenv("KASM_ALLOWED_ROOTS", "/home/kasm-user").split(",")
    roots_validator = RootsValidator(allowed_roots)
    
    logger.info(f"Initialized Kasm API client for {api_url}")
    logger.info(f"Allowed roots: {allowed_roots}")


# Command Execution Tool
@mcp.tool()
async def execute_kasm_command(
    kasm_id: str,
    command: str,
    working_dir: Optional[str] = None
) -> dict:
    """Execute a command in a Kasm session.
    
    Args:
        kasm_id: ID of the Kasm session
        command: Command to execute
        working_dir: Working directory for command execution
        
    Returns:
        Command execution result
    """
    if not kasm_client or not roots_validator:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        # Validate command for security
        roots_validator.validate_command(command, working_dir)
        
        # Execute command
        result = await kasm_client.exec_command(
            kasm_id=kasm_id,
            user_id=os.getenv("KASM_USER_ID", "default"),
            command=command,
            working_dir=working_dir
        )
        
        return {
            "success": True,
            "output": result.get("output", ""),
            "exit_code": result.get("exit_code", 0),
            "error": result.get("error", "")
        }
        
    except SecurityError as e:
        logger.warning(f"Security violation: {e}")
        return {
            "success": False,
            "error": f"Security violation: {str(e)}",
            "error_type": "security"
        }
    except Exception as e:
        logger.error(f"Failed to execute command: {e}")
        return {
            "success": False,
            "error": f"Failed to execute command: {str(e)}"
        }


# Session Management Tools
@mcp.tool()
async def create_kasm_session(
    image_name: str,
    group_id: str
) -> dict:
    """Create a new Kasm session with the specified workspace image.
    
    Args:
        image_name: Name of the workspace image to launch
        group_id: Group ID for the session
        
    Returns:
        Session creation result with session ID and connection details
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        user_id = os.getenv("KASM_USER_ID", "default")
        
        result = await kasm_client.request_kasm(
            image_name=image_name,
            user_id=user_id,
            group_id=group_id
        )
        
        return {
            "success": True,
            "kasm_id": result.get("kasm_id"),
            "session_url": result.get("kasm_url"),
            "status": result.get("status", "created"),
            "image_name": image_name
        }
        
    except Exception as e:
        logger.error(f"Failed to create Kasm session: {e}")
        return {
            "success": False,
            "error": f"Failed to create session: {str(e)}"
        }


@mcp.tool()
async def destroy_kasm_session(kasm_id: str) -> dict:
    """Destroy an existing Kasm session.
    
    Args:
        kasm_id: ID of the Kasm session to destroy
        
    Returns:
        Destruction result
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        user_id = os.getenv("KASM_USER_ID", "default")
        
        result = await kasm_client.destroy_kasm(
            kasm_id=kasm_id,
            user_id=user_id
        )
        
        return {
            "success": True,
            "kasm_id": kasm_id,
            "status": "destroyed",
            "message": "Session terminated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to destroy Kasm session: {e}")
        return {
            "success": False,
            "error": f"Failed to destroy session: {str(e)}"
        }


@mcp.tool()
async def get_session_status(kasm_id: str) -> dict:
    """Get the status of a Kasm session.
    
    Args:
        kasm_id: ID of the Kasm session
        
    Returns:
        Session status information
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        user_id = os.getenv("KASM_USER_ID", "default")
        
        result = await kasm_client.get_kasm_status(
            kasm_id=kasm_id,
            user_id=user_id
        )
        
        return {
            "success": True,
            "kasm_id": kasm_id,
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


@mcp.tool()
async def list_user_sessions() -> dict:
    """List all active sessions for the current user.
    
    Returns:
        List of user's active sessions
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        user_id = os.getenv("KASM_USER_ID", "default")
        
        result = await kasm_client.get_user_kasms(user_id=user_id)
        
        # Extract relevant session information
        sessions = []
        for session in result.get("kasms", []):
            sessions.append({
                "kasm_id": session.get("kasm_id"),
                "image_name": session.get("image_name"),
                "friendly_name": session.get("image_friendly_name"),
                "status": session.get("status"),
                "operational_status": session.get("operational_status"),
                "session_url": session.get("kasm_url"),
                "created_time": session.get("created_time"),
                "last_activity": session.get("last_activity"),
                "is_paused": session.get("is_paused", False)
            })
        
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Failed to list user sessions: {e}")
        return {
            "success": False,
            "error": f"Failed to list user sessions: {str(e)}"
        }


@mcp.tool()
async def list_all_sessions() -> dict:
    """List all active sessions in the system (admin).
    
    Returns:
        List of all active sessions
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        result = await kasm_client.get_kasms()
        
        # Extract relevant session information
        sessions = []
        for session in result.get("kasms", []):
            sessions.append({
                "kasm_id": session.get("kasm_id"),
                "user_id": session.get("user_id"),
                "username": session.get("username"),
                "image_name": session.get("image_name"),
                "friendly_name": session.get("image_friendly_name"),
                "status": session.get("status"),
                "operational_status": session.get("operational_status"),
                "session_url": session.get("kasm_url"),
                "created_time": session.get("created_time"),
                "last_activity": session.get("last_activity"),
                "is_paused": session.get("is_paused", False),
                "client_ip": session.get("client_ip")
            })
        
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Failed to list all sessions: {e}")
        return {
            "success": False,
            "error": f"Failed to list all sessions: {str(e)}"
        }


@mcp.tool()
async def pause_kasm_session(kasm_id: str) -> dict:
    """Pause a running Kasm session to free up resources.
    
    Args:
        kasm_id: ID of the Kasm session to pause
        
    Returns:
        Pause operation result
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        user_id = os.getenv("KASM_USER_ID", "default")
        
        result = await kasm_client.pause_kasm(
            kasm_id=kasm_id,
            user_id=user_id
        )
        
        return {
            "success": True,
            "kasm_id": kasm_id,
            "status": "paused",
            "message": "Session paused successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to pause session: {e}")
        return {
            "success": False,
            "error": f"Failed to pause session: {str(e)}"
        }


@mcp.tool()
async def resume_kasm_session(kasm_id: str) -> dict:
    """Resume a paused Kasm session.
    
    Args:
        kasm_id: ID of the Kasm session to resume
        
    Returns:
        Resume operation result
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        user_id = os.getenv("KASM_USER_ID", "default")
        
        result = await kasm_client.resume_kasm(
            kasm_id=kasm_id,
            user_id=user_id
        )
        
        return {
            "success": True,
            "kasm_id": kasm_id,
            "status": "running",
            "message": "Session resumed successfully",
            "session_url": result.get("kasm_url")
        }
        
    except Exception as e:
        logger.error(f"Failed to resume session: {e}")
        return {
            "success": False,
            "error": f"Failed to resume session: {str(e)}"
        }


@mcp.tool()
async def get_session_screenshot(
    kasm_id: str,
    save_to_file: Optional[str] = None
) -> dict:
    """Get a screenshot of a Kasm session.
    
    Args:
        kasm_id: ID of the Kasm session
        save_to_file: Optional path to save the screenshot
        
    Returns:
        Screenshot data or file path
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        user_id = os.getenv("KASM_USER_ID", "default")
        
        result = await kasm_client.get_kasm_screenshot(
            kasm_id=kasm_id,
            user_id=user_id
        )
        
        screenshot_data = result.get("screenshot", "")
        
        if save_to_file and screenshot_data:
            # Save screenshot to file if path provided
            import base64
            with open(save_to_file, "wb") as f:
                f.write(base64.b64decode(screenshot_data))
            
            return {
                "success": True,
                "kasm_id": kasm_id,
                "file_path": save_to_file,
                "message": f"Screenshot saved to {save_to_file}"
            }
        else:
            return {
                "success": True,
                "kasm_id": kasm_id,
                "screenshot_data": screenshot_data,
                "format": "base64",
                "message": "Screenshot captured successfully"
            }
        
    except Exception as e:
        logger.error(f"Failed to get screenshot: {e}")
        return {
            "success": False,
            "error": f"Failed to get screenshot: {str(e)}"
        }


# File Operation Tools
@mcp.tool()
async def read_kasm_file(
    kasm_id: str,
    file_path: str
) -> dict:
    """Read a file from a Kasm session.
    
    Args:
        kasm_id: ID of the Kasm session
        file_path: Path to the file to read
        
    Returns:
        File content
    """
    if not kasm_client or not roots_validator:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        # Validate file path
        roots_validator.validate_file_operation(file_path, operation="read")
        
        # Use cat command to read file
        command = f"cat '{file_path}'"
        user_id = os.getenv("KASM_USER_ID", "default")
        
        result = await kasm_client.exec_command(
            kasm_id=kasm_id,
            user_id=user_id,
            command=command
        )
        
        if result.get("exit_code") == 0:
            return {
                "success": True,
                "file_path": file_path,
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


@mcp.tool()
async def write_kasm_file(
    kasm_id: str,
    file_path: str,
    content: str
) -> dict:
    """Write content to a file in a Kasm session.
    
    Args:
        kasm_id: ID of the Kasm session
        file_path: Path where the file should be written
        content: Content to write to the file
        
    Returns:
        Write operation result
    """
    if not kasm_client or not roots_validator:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        # Validate file path
        roots_validator.validate_file_operation(file_path, operation="write")
        
        # Encode content to base64 to handle special characters
        import base64
        encoded_content = base64.b64encode(content.encode()).decode()
        
        # Create directory if needed and write file
        commands = [
            f"mkdir -p $(dirname '{file_path}')",
            f"echo '{encoded_content}' | base64 -d > '{file_path}'"
        ]
        
        user_id = os.getenv("KASM_USER_ID", "default")
        
        for command in commands:
            result = await kasm_client.exec_command(
                kasm_id=kasm_id,
                user_id=user_id,
                command=command
            )
            
            if result.get("exit_code") != 0:
                return {
                    "success": False,
                    "error": f"Failed to write file: {result.get('error', 'Unknown error')}"
                }
        
        return {
            "success": True,
            "file_path": file_path,
            "size": len(content),
            "message": f"File written successfully to {file_path}"
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


# Admin Tools
@mcp.tool()
async def get_available_workspaces() -> dict:
    """Get list of available workspace images.
    
    Returns:
        List of available workspace configurations
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        result = await kasm_client.get_images()
        
        # Extract relevant workspace information from images response
        workspaces = []
        for image in result.get("images", []):
            workspaces.append({
                "image_id": image.get("image_id"),
                "image_name": image.get("name", image.get("image_name")),
                "friendly_name": image.get("friendly_name"),
                "description": image.get("description"),
                "enabled": image.get("enabled", True),
                "cores": image.get("cores"),
                "memory": image.get("memory"),
                "gpu_count": image.get("gpu_count", 0),
                "categories": image.get("categories", []),
                "docker_registry": image.get("docker_registry"),
                "docker_image": image.get("docker_image")
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


@mcp.tool()
async def get_kasm_users() -> dict:
    """Get list of Kasm users.
    
    Returns:
        List of users in the Kasm system
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        result = await kasm_client.get_users()
        
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


@mcp.tool()
async def create_kasm_user(
    username: str,
    password: str,
    first_name: str = "",
    last_name: str = ""
) -> dict:
    """Create a new user account in the Kasm system.
    
    Args:
        username: Username for the new user
        password: Password for the new user
        first_name: User's first name (optional)
        last_name: User's last name (optional)
        
    Returns:
        User creation result
    """
    if not kasm_client:
        return {"success": False, "error": "Server not initialized"}
    
    try:
        result = await kasm_client.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        return {
            "success": True,
            "user_id": result.get("user_id"),
            "username": username,
            "message": f"User '{username}' created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        return {
            "success": False,
            "error": f"Failed to create user: {str(e)}"
        }


def main():
    """Main entry point for the MCP server."""
    try:
        # Initialize clients
        initialize_clients()
        
        # Run the FastMCP server (it manages its own event loop)
        mcp.run()
        
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
