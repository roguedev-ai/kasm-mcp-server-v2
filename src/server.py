"""Main MCP server implementation for Kasm Workspaces."""

import asyncio
import logging
import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
from mcp_python import Server
from mcp_python.server import NotificationOptions
from mcp_python.server.models import InitializationOptions
from mcp_python.server.stdio import stdio_server
from mcp_python.types import Tool, Resource

from .kasm_api import KasmAPIClient
from .security import RootsValidator
from .tools import (
    ExecuteKasmCommandTool,
    CreateKasmSessionTool,
    DestroyKasmSessionTool,
    GetSessionStatusTool,
    ReadKasmFileTool,
    WriteKasmFileTool,
    GetAvailableWorkspacesTool,
    GetKasmUsersTool,
    CreateKasmUserTool
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class KasmMCPServer:
    """MCP Server for Kasm Workspaces integration."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("kasm-mcp-server-v2")
        
        # Load configuration from environment
        self.kasm_api_url = os.getenv("KASM_API_URL")
        self.kasm_api_key = os.getenv("KASM_API_KEY")
        self.kasm_api_secret = os.getenv("KASM_API_SECRET")
        
        if not all([self.kasm_api_url, self.kasm_api_key, self.kasm_api_secret]):
            raise ValueError(
                "Missing required environment variables: "
                "KASM_API_URL, KASM_API_KEY, KASM_API_SECRET"
            )
        
        # Parse allowed roots
        allowed_roots_str = os.getenv("ALLOWED_ROOTS", "/home/kasm_user,/workspace")
        self.allowed_roots = [
            root.strip() for root in allowed_roots_str.split(",") if root.strip()
        ]
        
        # Initialize components
        self.kasm_client = KasmAPIClient(
            api_url=self.kasm_api_url,
            api_key=self.kasm_api_key,
            api_secret=self.kasm_api_secret
        )
        
        self.roots_validator = RootsValidator(self.allowed_roots)
        
        # Initialize tools
        self._init_tools()
        
        # Set up server handlers
        self._setup_handlers()
        
    def _init_tools(self):
        """Initialize all available tools."""
        # Phase 1: Core command execution
        self.execute_command_tool = ExecuteKasmCommandTool(
            self.kasm_client,
            self.roots_validator
        )
        
        # Phase 2: Session management
        self.create_session_tool = CreateKasmSessionTool(self.kasm_client)
        self.destroy_session_tool = DestroyKasmSessionTool(self.kasm_client)
        self.get_session_status_tool = GetSessionStatusTool(self.kasm_client)
        
        # Phase 2: File operations
        self.read_file_tool = ReadKasmFileTool(
            self.kasm_client,
            self.roots_validator
        )
        self.write_file_tool = WriteKasmFileTool(
            self.kasm_client,
            self.roots_validator
        )
        
        # Phase 3: Admin and resources
        self.get_workspaces_tool = GetAvailableWorkspacesTool(self.kasm_client)
        self.get_users_tool = GetKasmUsersTool(self.kasm_client)
        self.create_user_tool = CreateKasmUserTool(self.kasm_client)
        
        # Store all tools
        self.tools = [
            self.execute_command_tool,
            self.create_session_tool,
            self.destroy_session_tool,
            self.get_session_status_tool,
            self.read_file_tool,
            self.write_file_tool,
            self.get_workspaces_tool,
            self.get_users_tool,
            self.create_user_tool
        ]
        
    def _setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools."""
            return [
                Tool(
                    name=tool.name,
                    description=tool.description,
                    inputSchema=tool.input_schema.schema() if tool.input_schema else {}
                )
                for tool in self.tools
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[dict]:
            """Handle tool execution requests."""
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            # Find the requested tool
            tool = next((t for t in self.tools if t.name == name), None)
            if not tool:
                raise ValueError(f"Unknown tool: {name}")
            
            # Execute the tool
            result = await tool.run(arguments)
            
            return [result]
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources."""
            # For now, we don't have resources, but this can be expanded
            return []
        
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting Kasm MCP Server v2.0.0")
        logger.info(f"Kasm API URL: {self.kasm_api_url}")
        logger.info(f"Allowed roots: {', '.join(self.allowed_roots)}")
        
        # Run the server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            init_options = InitializationOptions(
                server_name="kasm-mcp-server-v2",
                server_version="2.0.0",
                capabilities=self.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
            
            await self.server.run(
                read_stream,
                write_stream,
                init_options
            )


def main():
    """Main entry point."""
    try:
        server = KasmMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
