# LLM Integration Guide for Kasm MCP Server

## Table of Contents
1. [Overview](#overview)
2. [Supported LLM Platforms](#supported-llm-platforms)
3. [Generic MCP Integration](#generic-mcp-integration)
4. [Platform-Specific Guides](#platform-specific-guides)
5. [API Integration](#api-integration)
6. [Tool Descriptions for LLMs](#tool-descriptions-for-llms)
7. [Custom Integrations](#custom-integrations)
8. [Performance Optimization](#performance-optimization)
9. [Security Considerations](#security-considerations)

## Overview

The Kasm MCP Server can be integrated with any LLM that supports the Model Context Protocol. This guide covers integration patterns for various AI platforms and custom implementations.

### Benefits of Integration

- **Infrastructure Automation**: LLMs can provision and manage cloud workspaces
- **Development Assistance**: AI can set up complete development environments
- **Testing & QA**: Automated testing environment creation and execution
- **Training & Education**: Dynamic lab environment provisioning
- **Security Operations**: Isolated sandbox environments for analysis

## Supported LLM Platforms

### Tier 1 - Native MCP Support
These platforms have built-in MCP support:

| Platform | MCP Support | Integration Method |
|----------|------------|-------------------|
| **Claude (Anthropic)** | Native | Direct MCP configuration |
| **Cline (VS Code)** | Native | Settings.json configuration |
| **Continue.dev** | Native | Config.json setup |
| **Zed Editor** | Native | Built-in MCP client |

### Tier 2 - Plugin/Extension Support
These platforms support MCP via plugins:

| Platform | Plugin Required | Integration Method |
|----------|----------------|-------------------|
| **ChatGPT** | Custom GPT Action | OpenAPI spec + webhook |
| **GitHub Copilot** | Extension | VS Code extension |
| **Cursor** | Extension | Custom extension |
| **JetBrains AI** | Plugin | IDE plugin |

### Tier 3 - API Integration
These require custom integration:

| Platform | Integration Type | Method |
|----------|-----------------|--------|
| **LangChain** | Python SDK | Custom chain |
| **AutoGPT** | Plugin | Custom plugin |
| **OpenAI API** | Function Calling | Custom implementation |
| **Google Gemini** | Function Calling | Custom implementation |

## Generic MCP Integration

### Standard MCP Configuration

Most MCP-compatible clients use a similar configuration structure:

```json
{
  "mcpServers": {
    "kasm-mcp-server": {
      "command": "python",
      "args": ["path/to/server.py"],
      "env": {
        "KASM_API_URL": "https://kasm.example.com",
        "KASM_API_KEY": "your_api_key",
        "KASM_API_SECRET": "your_api_secret"
      }
    }
  }
}
```

### Stdio Communication

The server communicates via standard input/output using JSON-RPC 2.0:

```python
# Example client implementation
import subprocess
import json

# Start the MCP server
process = subprocess.Popen(
    ["python", "src/server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env={
        "KASM_API_URL": "https://kasm.example.com",
        "KASM_API_KEY": "key",
        "KASM_API_SECRET": "secret"
    }
)

# Send initialization request
request = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {}
    },
    "id": 1
}
process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()

# Read response
response = json.loads(process.stdout.readline())
```

## Platform-Specific Guides

### Claude Desktop Integration

1. **Install Claude Desktop** from Anthropic

2. **Configure MCP servers** in Claude settings:
```json
{
  "mcpServers": {
    "kasm": {
      "command": "python",
      "args": ["/home/user/kasm-mcp-server-v2/src/server.py"],
      "env": {
        "KASM_API_URL": "https://kasm.example.com",
        "KASM_API_KEY": "your_key",
        "KASM_API_SECRET": "your_secret"
      }
    }
  }
}
```

3. **Restart Claude** and verify connection

### Continue.dev Integration

1. **Install Continue** extension in VS Code

2. **Edit** `~/.continue/config.json`:
```json
{
  "models": [...],
  "mcpServers": [
    {
      "name": "kasm",
      "command": "python",
      "args": ["~/kasm-mcp-server-v2/src/server.py"],
      "env": {
        "KASM_API_URL": "https://kasm.example.com",
        "KASM_API_KEY": "key",
        "KASM_API_SECRET": "secret"
      }
    }
  ]
}
```

### LangChain Integration

```python
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
import subprocess
import json

class KasmMCPTool:
    def __init__(self, server_path, env_vars):
        self.process = subprocess.Popen(
            ["python", server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            env=env_vars
        )
        self._initialize()
    
    def _initialize(self):
        # Send MCP initialization
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
            "id": 1
        }
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        response = json.loads(self.process.stdout.readline())
        self.tools = response.get("result", {}).get("tools", [])
    
    def call_tool(self, tool_name, arguments):
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 2
        }
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        response = json.loads(self.process.stdout.readline())
        return response.get("result", {})

# Create LangChain tools
kasm_mcp = KasmMCPTool(
    "path/to/server.py",
    {
        "KASM_API_URL": "https://kasm.example.com",
        "KASM_API_KEY": "key",
        "KASM_API_SECRET": "secret"
    }
)

tools = [
    Tool(
        name="create_kasm_session",
        func=lambda x: kasm_mcp.call_tool("create_kasm_session", json.loads(x)),
        description="Create a new Kasm workspace session"
    ),
    Tool(
        name="execute_kasm_command",
        func=lambda x: kasm_mcp.call_tool("execute_kasm_command", json.loads(x)),
        description="Execute a command in a Kasm workspace"
    )
]

# Initialize agent
llm = OpenAI(temperature=0)
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use the agent
result = agent.run("Create a new Ubuntu workspace and install Python")
```

### OpenAI Function Calling Integration

```python
import openai
import json
import subprocess

class KasmMCPIntegration:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        self.mcp_process = self._start_mcp_server()
        
    def _start_mcp_server(self):
        return subprocess.Popen(
            ["python", "src/server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            env={
                "KASM_API_URL": "https://kasm.example.com",
                "KASM_API_KEY": "key",
                "KASM_API_SECRET": "secret"
            }
        )
    
    def get_functions(self):
        """Convert MCP tools to OpenAI function definitions"""
        return [
            {
                "name": "create_kasm_session",
                "description": "Create a new Kasm workspace session",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_name": {
                            "type": "string",
                            "description": "Docker image for the workspace"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID for the session"
                        }
                    },
                    "required": ["image_name"]
                }
            },
            {
                "name": "execute_kasm_command",
                "description": "Execute a command in a Kasm workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "kasm_id": {
                            "type": "string",
                            "description": "Session ID"
                        },
                        "command": {
                            "type": "string",
                            "description": "Command to execute"
                        }
                    },
                    "required": ["kasm_id", "command"]
                }
            }
        ]
    
    def execute_function(self, function_name, arguments):
        """Execute MCP tool via function call"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": function_name,
                "arguments": arguments
            },
            "id": 1
        }
        self.mcp_process.stdin.write(json.dumps(request) + "\n")
        self.mcp_process.stdin.flush()
        response = json.loads(self.mcp_process.stdout.readline())
        return response.get("result", {})
    
    def chat_with_tools(self, message):
        """Chat with OpenAI using Kasm tools"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}],
            functions=self.get_functions(),
            function_call="auto"
        )
        
        # Check if function was called
        if response.choices[0].message.function_call:
            function_name = response.choices[0].message.function_call.name
            arguments = json.loads(response.choices[0].message.function_call.arguments)
            
            # Execute the function
            result = self.execute_function(function_name, arguments)
            
            # Return result to GPT for final response
            return self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": message},
                    response.choices[0].message,
                    {
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(result)
                    }
                ]
            )
        
        return response

# Usage
integration = KasmMCPIntegration("sk-...")
result = integration.chat_with_tools("Create an Ubuntu workspace and install Docker")
print(result.choices[0].message.content)
```

## API Integration

### REST API Wrapper

For platforms that don't support MCP, create a REST API wrapper:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json

app = FastAPI()

class ToolRequest(BaseModel):
    tool_name: str
    arguments: dict

class MCPServer:
    def __init__(self):
        self.process = subprocess.Popen(
            ["python", "src/server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            env={
                "KASM_API_URL": "https://kasm.example.com",
                "KASM_API_KEY": "key",
                "KASM_API_SECRET": "secret"
            }
        )
        self._initialize()
    
    def call_tool(self, tool_name: str, arguments: dict):
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        response = json.loads(self.process.stdout.readline())
        return response.get("result", {})

mcp_server = MCPServer()

@app.post("/tools/call")
async def call_tool(request: ToolRequest):
    try:
        result = mcp_server.call_tool(request.tool_name, request.arguments)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/list")
async def list_tools():
    return {
        "tools": [
            "create_kasm_session",
            "destroy_kasm_session",
            "execute_kasm_command",
            "read_kasm_file",
            "write_kasm_file"
        ]
    }
```

## Tool Descriptions for LLMs

### Optimized Prompts for Each Tool

When integrating with LLMs, provide clear tool descriptions:

```yaml
create_kasm_session:
  description: |
    Creates a new isolated workspace container in Kasm.
    Use this when you need a fresh environment for development,
    testing, or running applications.
  examples:
    - "Create an Ubuntu workspace for Python development"
    - "Launch a desktop with Firefox for web testing"
  parameters:
    image_name: "Docker image name (e.g., 'kasmweb/ubuntu-focal-desktop')"
    user_id: "Optional user identifier"

execute_kasm_command:
  description: |
    Runs shell commands inside an existing Kasm workspace.
    Use this for installing software, running scripts, or
    performing system operations.
  examples:
    - "Install Node.js in workspace abc123"
    - "Run Python script in the active session"
  parameters:
    kasm_id: "The workspace session ID"
    command: "Shell command to execute"
    working_dir: "Optional working directory"

read_kasm_file:
  description: |
    Reads and returns the contents of a file from a workspace.
    Use this to inspect configuration files, logs, or code.
  examples:
    - "Read the nginx.conf file from workspace"
    - "Show the contents of /var/log/app.log"
  parameters:
    kasm_id: "The workspace session ID"
    file_path: "Full path to the file"

write_kasm_file:
  description: |
    Creates or overwrites a file in the workspace.
    Use this to create configuration files, scripts, or data files.
  examples:
    - "Create a Python script in the workspace"
    - "Write configuration to /etc/app/config.yaml"
  parameters:
    kasm_id: "The workspace session ID"
    file_path: "Full path to the file"
    content: "File contents to write"
```

## Custom Integrations

### Building a Custom MCP Client

```python
import asyncio
import json
from typing import Any, Dict, Optional

class CustomMCPClient:
    """Custom MCP client for integration with any LLM"""
    
    def __init__(self, server_command: list, env_vars: dict):
        self.server_command = server_command
        self.env_vars = env_vars
        self.process = None
        self.reader = None
        self.writer = None
        
    async def connect(self):
        """Start the MCP server and establish connection"""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=self.env_vars
        )
        
        # Initialize the connection
        await self._send_request({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            },
            "id": 1
        })
        
        response = await self._read_response()
        self.capabilities = response.get("result", {})
        return self.capabilities
    
    async def list_tools(self) -> list:
        """Get available tools from the server"""
        await self._send_request({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 2
        })
        
        response = await self._read_response()
        return response.get("result", {}).get("tools", [])
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a specific tool with arguments"""
        await self._send_request({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 3
        })
        
        response = await self._read_response()
        return response.get("result")
    
    async def _send_request(self, request: dict):
        """Send a JSON-RPC request to the server"""
        message = json.dumps(request) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
    
    async def _read_response(self) -> dict:
        """Read a JSON-RPC response from the server"""
        line = await self.process.stdout.readline()
        return json.loads(line.decode())
    
    async def close(self):
        """Close the connection and terminate the server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()

# Usage example
async def main():
    client = CustomMCPClient(
        server_command=["python", "src/server.py"],
        env_vars={
            "KASM_API_URL": "https://kasm.example.com",
            "KASM_API_KEY": "key",
            "KASM_API_SECRET": "secret"
        }
    )
    
    # Connect to the server
    await client.connect()
    
    # List available tools
    tools = await client.list_tools()
    print(f"Available tools: {tools}")
    
    # Create a workspace
    result = await client.call_tool(
        "create_kasm_session",
        {"image_name": "kasmweb/ubuntu-focal-desktop"}
    )
    print(f"Created workspace: {result}")
    
    # Clean up
    await client.close()

# Run the example
asyncio.run(main())
```

## Performance Optimization

### Connection Pooling

For high-volume applications, implement connection pooling:

```python
import asyncio
from contextlib import asynccontextmanager

class MCPConnectionPool:
    """Manages a pool of MCP server connections"""
    
    def __init__(self, size: int = 5):
        self.size = size
        self.connections = asyncio.Queue(maxsize=size)
        self._initialized = False
    
    async def initialize(self):
        """Create initial connections"""
        for _ in range(self.size):
            client = CustomMCPClient(
                server_command=["python", "src/server.py"],
                env_vars={...}
            )
            await client.connect()
            await self.connections.put(client)
        self._initialized = True
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self._initialized:
            await self.initialize()
        
        connection = await self.connections.get()
        try:
            yield connection
        finally:
            await self.connections.put(connection)
    
    async def close_all(self):
        """Close all connections"""
        while not self.connections.empty():
            connection = await self.connections.get()
            await connection.close()

# Usage
pool = MCPConnectionPool(size=10)

async def handle_request(tool_name: str, arguments: dict):
    async with pool.get_connection() as client:
        return await client.call_tool(tool_name, arguments)
```

### Caching Strategies

Implement caching for frequently accessed data:

```python
from functools import lru_cache
import hashlib
import json

class CachedMCPClient(CustomMCPClient):
    """MCP client with result caching"""
    
    def __init__(self, *args, cache_ttl: int = 300, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = {}
        self.cache_ttl = cache_ttl
    
    def _cache_key(self, tool_name: str, arguments: dict) -> str:
        """Generate cache key for tool call"""
        data = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call tool with caching"""
        # Check cache for read operations
        if tool_name in ["get_session_status", "read_kasm_file"]:
            cache_key = self._cache_key(tool_name, arguments)
            if cache_key in self.cache:
                return self.cache[cache_key]
        
        # Call the actual tool
        result = await super().call_tool(tool_name, arguments)
        
        # Cache the result
        if tool_name in ["get_session_status", "read_kasm_file"]:
            self.cache[cache_key] = result
        
        return result
```

## Security Considerations

### API Key Management

Never hardcode API keys. Use secure methods:

```python
import os
from cryptography.fernet import Fernet

class SecureMCPConfig:
    """Secure configuration management"""
    
    def __init__(self, key_file: str = "~/.mcp/key"):
        self.key_file = os.path.expanduser(key_file)
        self.cipher = self._get_cipher()
    
    def _get_cipher(self) -> Fernet:
        """Load or create encryption key"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)
        return Fernet(key)
    
    def encrypt_config(self, config: dict) -> bytes:
        """Encrypt configuration"""
        data = json.dumps(config).encode()
        return self.cipher.encrypt(data)
    
    def decrypt_config(self, encrypted: bytes) -> dict:
        """Decrypt configuration"""
        data = self.cipher.decrypt(encrypted)
        return json.loads(data.decode())
```

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
import time
from collections import defaultdict

class RateLimitedMCPClient(CustomMCPClient):
    """MCP client with rate limiting"""
    
    def __init__(self, *args, max_calls_per_minute: int = 60, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_calls = max_calls_per_minute
        self.call_times = defaultdict(list)
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call tool with rate limiting"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old entries
        self.call_times[tool_name] = [
            t for t in self.call_times[tool_name] 
            if t > minute_ago
        ]
        
        # Check rate limit
        if len(self.call_times[tool_name]) >= self.max_calls:
            wait_time = 60 - (current_time - self.call_times[tool_name][0])
            await asyncio.sleep(wait_time)
        
        # Record call time
        self.call_times[tool_name].append(current_time)
        
        # Make the actual call
        return await super().call_tool(tool_name, arguments)
```

### Audit Logging

Log all tool calls for security auditing:

```python
import logging
from datetime import datetime

class AuditedMCPClient(CustomMCPClient):
    """MCP client with audit logging"""
    
    def __init__(self, *args, audit_log: str = "mcp_audit.log", **kwargs):
        super().__init__(*args, **kwargs)
        self.audit_logger = logging.getLogger("mcp_audit")
        handler = logging.FileHandler(audit_log)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(message)s')
        )
        self.audit_logger.addHandler(handler)
        self.audit_logger.setLevel(logging.INFO)
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call tool with audit logging"""
        # Log the request
        self.audit_logger.info(
            f"CALL: {tool_name} | Args: {json.dumps(arguments)} | "
            f"User: {os.getenv('USER', 'unknown')}"
        )
        
        try:
            result = await super().call_tool(tool_name, arguments)
            # Log success
            self.audit_logger.info(
                f"SUCCESS: {tool_name} | Result: {len(str(result))} bytes"
            )
            return result
        except Exception as e:
            # Log failure
            self.audit_logger.error(
                f"FAILURE: {tool_name} | Error: {str(e)}"
            )
            raise
```

## Next Steps

- [Installation Guide](INSTALLATION_GUIDE.md) - Complete setup instructions
- [Cline Integration](CLINE_INTEGRATION_GUIDE.md) - VS Code/Cline specific setup
- [API Documentation](DOCUMENTATION.md) - Complete API reference
- [Security Guide](SECURITY.md) - Security best practices

## Support

For integration assistance:
- **GitHub Issues**: [https://github.com/roguedev-ai/kasm-mcp-server-v2/issues](https://github.com/roguedev-ai/kasm-mcp-server-v2/issues)
- **Discussions**: [https://github.com/roguedev-ai/kasm-mcp-server-v2/discussions](https://github.com/roguedev-ai/kasm-mcp-server-v2/discussions)
- **Examples**: [https://github.com/roguedev-ai/kasm-mcp-server-v2/tree/main/examples](https://github.com/roguedev-ai/kasm-mcp-server-v2/tree/main/examples)
