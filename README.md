# Kasm MCP Server v2

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-1.0%2B-green.svg)](https://github.com/anthropics/model-context-protocol)

A Model Context Protocol (MCP) server that enables AI agents to manage and interact with Kasm Workspaces containerized desktop infrastructure. This server provides a standardized interface for LLMs to create, manage, and execute commands within Kasm sessions.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/roguedev-ai/kasm-mcp-server-v2.git
cd kasm-mcp-server-v2

# Run the automated setup script
./setup-prerequisites.sh

# Choose option 1 for NPM/Python mode (recommended for Cline)
# Configure your Kasm API credentials when prompted

# Start the server
source venv/bin/activate
python -m src
```

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Installation Guide](INSTALLATION_GUIDE.md)** - Detailed installation instructions
- **[Tool Reference](TOOL_REFERENCE.md)** - Complete reference for all 21 available tools
- **[Suggested Prompts](PROMPTS.md)** - Example prompts for effective usage
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
- **[Cline Integration Guide](CLINE_INTEGRATION_GUIDE.md)** - Configure Cline to use this MCP server
- **[LLM Integration Guide](LLM_INTEGRATION_GUIDE.md)** - Integrate with any MCP-compatible LLM
- **[Architecture Documentation](ARCHITECTURE.md)** - System design and components
- **[Security Documentation](SECURITY.md)** - Security features and best practices

## ✨ Features

- **🔧 Session Management** - Create, destroy, and monitor Kasm workspace sessions
- **💻 Command Execution** - Execute commands inside Kasm containers with security boundaries
- **📁 File Operations** - Read and write files within Kasm sessions
- **👥 User Management** - Create and manage Kasm users
- **🔒 Security** - MCP Roots security mechanism for safe file operations
- **🔌 Multiple Deployment Options** - NPM/Python or Docker deployment

## 🛠️ Available Tools

The server provides **21 tools** organized into categories:

### Session Management (8 tools)
- `create_kasm_session` - Launch a new Kasm workspace
- `destroy_kasm_session` - Terminate a session
- `get_session_status` - Check session status
- `list_user_sessions` - List your active sessions
- `list_all_sessions` - List all system sessions (admin)
- `pause_kasm_session` - Pause a session to free resources
- `resume_kasm_session` - Resume a paused session
- `get_session_screenshot` - Capture session screenshot

### Command & File Operations (3 tools)
- `execute_kasm_command` - Execute shell commands in sessions
- `read_kasm_file` - Read file contents from sessions
- `write_kasm_file` - Write content to files in sessions

### User Management (6 tools)
- `get_kasm_users` - List all users
- `create_kasm_user` - Create new user accounts
- `get_kasm_user` - Get specific user details
- `update_kasm_user` - Update user information
- `delete_kasm_user` - Remove users from system
- `logout_kasm_user` - Logout all user sessions

### Monitoring & Performance (3 tools)
- `get_session_frame_stats` - Frame rendering statistics
- `get_session_bottleneck_stats` - CPU/network bottleneck analysis
- `get_session_recordings` - Access session recordings

### System Information (1 tool)
- `get_available_workspaces` - List available workspace images

See the [Tool Reference](TOOL_REFERENCE.md) for complete details on all tools.

## 📦 Installation Options

### Option 1: Automated Setup (Recommended)

Use the `setup-prerequisites.sh` script for automated installation:

```bash
./setup-prerequisites.sh
```

Choose from:
1. **NPM/Python Mode** - Direct execution with npm support (best for Cline)
2. **Docker Mode** - Containerized deployment
3. **Both** - Install prerequisites for both modes

### Option 2: Manual Installation

See the [Installation Guide](INSTALLATION_GUIDE.md) for manual setup instructions.

## 🔧 Configuration

Create a `.env` file with your Kasm credentials:

```env
KASM_API_URL=https://your-kasm-instance.com
KASM_API_KEY=your_api_key_here
KASM_API_SECRET=your_api_secret_here
KASM_USER_ID=default
KASM_ALLOWED_ROOTS=/home/kasm-user
LOG_LEVEL=INFO
```

## 🧪 Testing

Run the diagnostic test to verify your installation:

```bash
python test_server.py
```

## 🐛 Troubleshooting

### Recent Fixes

- **FastMCP Initialization Error** - Fixed in commit c95882e (see [MCP_SDK_COMPATIBILITY_FIX.md](MCP_SDK_COMPATIBILITY_FIX.md))
- **Import Issues** - Resolved with official MCP SDK migration

### Common Issues

1. **"No module named 'mcp'"** - Install the MCP SDK: `pip install mcp`
2. **Environment variables not set** - Check your `.env` file configuration
3. **Server won't start** - Run `python test_server.py` for diagnostics

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to the repository.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [Kasm Workspaces Documentation](https://kasmweb.com/docs/)
- [Model Context Protocol Documentation](https://github.com/anthropics/model-context-protocol)
- [Cline (Claude Dev) Extension](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)

## 📧 Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/roguedev-ai/kasm-mcp-server-v2/issues)
- Check existing documentation in the `/docs` folder
- Review the troubleshooting section above

---

**Current Version**: 2.0.1  
**Last Updated**: September 10, 2025  
**Status**: ✅ Production Ready
