# Kasm MCP Server V2 - Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Available Tools](#available-tools)
6. [Security](#security)
7. [API Reference](#api-reference)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)
10. [Development](#development)

## Overview

The Kasm MCP Server V2 is a Model Context Protocol (MCP) server that provides programmatic access to Kasm Workspaces. It enables AI agents like Cline to manage and interact with containerized desktop infrastructure through a standardized interface.

### Key Features
- **Session Management**: Create, destroy, and monitor Kasm sessions
- **Command Execution**: Run commands inside containers with security boundaries
- **File Operations**: Read and write files within containers
- **User Management**: Create users and manage permissions
- **Resource Discovery**: List available workspaces and users

## Architecture

### Component Overview
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Agent      │────▶│   MCP Server    │────▶│ Kasm Workspaces │
│   (Cline)       │◀────│   (This Project)│◀────│   Platform      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │                        │
        │ MCP Protocol          │ HTTP+SSE              │ REST API
        └───────────────────────┴────────────────────────┘
```

### Core Components

1. **MCP Server** (`src/server.py`)
   - Handles MCP protocol communication
   - Manages tool registration and execution
   - Provides HTTP+SSE transport for remote connections

2. **Kasm API Client** (`src/kasm_api/client.py`)
   - Wraps Kasm Developer API endpoints
   - Handles authentication and request signing
   - Provides typed interfaces for API calls

3. **Security Layer** (`src/security/roots.py`)
   - Implements MCP Roots mechanism
   - Validates file paths and commands
   - Prevents unauthorized access

4. **Tools** (`src/tools/`)
   - Modular tool implementations
   - Each tool has defined schemas and validation
   - Async execution support

## Installation

### Docker Installation (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/roguedev-ai/kasm-mcp-server-v2.git
cd kasm-mcp-server-v2
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Kasm API credentials
```

3. Build and run:
```bash
docker-compose up -d
```

### Remote Installation

For automated deployment on a remote server:

```bash
curl -sSL https://raw.githubusercontent.com/roguedev-ai/kasm-mcp-server-v2/master/install.sh | sudo bash
```

### Manual Installation

1. Install Python 3.8+:
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure and run:
```bash
cp .env.example .env
# Edit .env file
python -m src
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `KASM_API_URL` | Kasm Workspaces API endpoint | - | Yes |
| `KASM_API_KEY` | API key for authentication | - | Yes |
| `KASM_API_SECRET` | API secret for authentication | - | Yes |
| `MCP_SERVER_PORT` | Port for MCP server | 8080 | No |
| `MCP_SERVER_HOST` | Host to bind to | 0.0.0.0 | No |
| `ALLOWED_ROOTS` | Comma-separated allowed directories | /home/kasm_user,/workspace | No |
| `LOG_LEVEL` | Logging level | INFO | No |

### Cline Configuration

Add to your Cline MCP settings:

```json
{
  "mcpServers": {
    "kasm": {
      "url": "http://your-server:8080",
      "transport": "http+sse"
    }
  }
}
```

## Available Tools

The server provides **21 tools** for comprehensive Kasm Workspaces management. For complete details, see the [Tool Reference](TOOL_REFERENCE.md).

**Important Note:** The `user_id` parameter is automatically obtained from the `KASM_USER_ID` environment variable and is NOT required as an input parameter for most tools.

### Session Management (8 tools)
1. **create_kasm_session** - Launch a new workspace
2. **destroy_kasm_session** - Terminate a session
3. **get_session_status** - Check session status
4. **list_user_sessions** - List your active sessions
5. **list_all_sessions** - List all system sessions (admin)
6. **pause_kasm_session** - Pause a session to free resources
7. **resume_kasm_session** - Resume a paused session
8. **get_session_screenshot** - Capture session screenshot

### Command & File Operations (3 tools)
9. **execute_kasm_command** - Execute shell commands
10. **read_kasm_file** - Read file contents
11. **write_kasm_file** - Write content to files

### User Management (6 tools)
12. **get_kasm_users** - List all users
13. **create_kasm_user** - Create new user accounts
14. **get_kasm_user** - Get specific user details
15. **update_kasm_user** - Update user information
16. **delete_kasm_user** - Remove users from system
17. **logout_kasm_user** - Logout all user sessions

### Monitoring & Performance (3 tools)
18. **get_session_frame_stats** - Frame rendering statistics
19. **get_session_bottleneck_stats** - CPU/network bottleneck analysis
20. **get_session_recordings** - Access session recordings

### System Information (1 tool)
21. **get_available_workspaces** - List available workspace images

## Security

### MCP Roots Implementation

The server implements the MCP Roots security mechanism to prevent unauthorized access:

1. **Path Validation**: All file operations are validated against allowed roots
2. **Command Filtering**: Dangerous commands are blocked (sudo, chmod, etc.)
3. **Directory Traversal Prevention**: Paths containing `../` are rejected
4. **System File Protection**: Access to /etc, /boot, /sys is blocked

### Blocked Commands
- System administration: `sudo`, `su`, `passwd`, `useradd`
- Service management: `systemctl`, `service`, `init`
- System control: `shutdown`, `reboot`, `halt`
- File permissions: `chmod`, `chown` (when targeting system files)

### API Authentication

All Kasm API calls use SHA256-based authentication:
1. Request body is combined with API key and secret
2. SHA256 hash is generated
3. Hash is included in request for verification

## API Reference

### Kasm API Endpoints Used

| Endpoint | MCP Tool | Required Permissions |
|----------|----------|---------------------|
| `/api/public/request_kasm` | create_kasm_session | Users Auth Session, User |
| `/api/public/destroy_kasm` | destroy_kasm_session | Users Auth Session, Session |
| `/api/public/get_kasm_status` | get_session_status | Users Auth Session, Session |
| `/api/public/exec_command_kasm` | execute_kasm_command, read_kasm_file, write_kasm_file | Sessions Modify |
| `/api/public/get_workspaces` | get_available_workspaces | Images View |
| `/api/public/get_users` | get_kasm_users | Users View |
| `/api/public/create_user` | create_kasm_user | User |

## Examples

### Example 1: Create Session and Run Command

```python
# AI Agent Request
"Create an Ubuntu session and install git"

# MCP Tool Calls Generated:
1. create_kasm_session:
   {
     "image_name": "kasmweb/ubuntu-focal-desktop",
     "user_id": "user123",
     "group_id": "default"
   }

2. execute_kasm_command:
   {
     "kasm_id": "returned_session_id",
     "user_id": "user123",
     "command": "sudo apt-get update && sudo apt-get install -y git"
   }
```

### Example 2: Write and Execute Python Script

```python
# AI Agent Request
"Create a Python script that prints Hello World and run it"

# MCP Tool Calls Generated:
1. write_kasm_file:
   {
     "kasm_id": "session123",
     "user_id": "user123",
     "file_path": "/home/kasm_user/hello.py",
     "content": "print('Hello World')"
   }

2. execute_kasm_command:
   {
     "kasm_id": "session123",
     "user_id": "user123",
     "command": "python3 /home/kasm_user/hello.py"
   }
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if server is running: `systemctl status kasm-mcp-server-v2`
   - Verify port is open: `netstat -tlnp | grep 8080`
   - Check firewall rules

2. **Authentication Failed**
   - Verify API credentials in .env file
   - Check Kasm API permissions
   - Ensure API endpoint URL is correct

3. **Security Violations**
   - Review ALLOWED_ROOTS configuration
   - Check command for blocked patterns
   - Ensure paths are within allowed directories

4. **Docker Issues**
   - Check logs: `docker-compose logs -f`
   - Verify environment variables are passed correctly
   - Ensure Docker daemon is running

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python -m src
```

### Health Check

Test server health:
```bash
curl http://localhost:8080/health
```

## Development

### Project Structure
```
kasm-mcp-server-v2/
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py           # Main server
│   ├── kasm_api/          # API client
│   ├── security/          # Security layer
│   └── tools/             # Tool implementations
├── tests/                 # Unit tests
├── Dockerfile            # Container definition
├── docker-compose.yml    # Compose configuration
├── requirements.txt      # Dependencies
└── install.sh           # Installation script
```

### Adding New Tools

1. Create tool class in `src/tools/`:
```python
class MyNewTool(Tool):
    name = "my_new_tool"
    description = "Tool description"
    input_schema = MyToolParams
    
    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        pass
```

2. Add to `src/tools/__init__.py`
3. Register in `src/server.py`

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_basic.py::TestRootsValidator
```

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and test
4. Submit pull request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Run black formatter: `black src/`

## License

MIT License - See LICENSE file for details.

## Support

- GitHub Issues: https://github.com/roguedev-ai/kasm-mcp-server-v2/issues
- Documentation: This file
- MCP Specification: https://modelcontextprotocol.io
