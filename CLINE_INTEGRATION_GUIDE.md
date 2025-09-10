# Cline Integration Guide for Kasm MCP Server

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Setup](#quick-setup)
4. [Detailed Configuration](#detailed-configuration)
5. [Using the Server with Cline](#using-the-server-with-cline)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Overview

This guide explains how to integrate the Kasm MCP Server with Cline, enabling your AI assistant to manage Kasm Workspaces directly from VS Code.

### What You Can Do

Once integrated, Cline can:
- 🚀 Launch new Kasm workspace sessions
- 💻 Execute commands in remote containers
- 📁 Read and write files in workspaces
- 🔧 Install software and configure environments
- 👥 Manage users and permissions
- 📊 Monitor session status

## Prerequisites

### Required Components

1. **VS Code** with Cline extension installed
2. **Node.js** version 18 or higher
3. **Kasm MCP Server** installed and configured
4. **Kasm Workspaces** instance with API access

### Verify Prerequisites

```bash
# Check Node.js version
node --version  # Should be v18.0.0 or higher

# Check npm version
npm --version  # Should be 8.0.0 or higher

# Check if Cline is installed in VS Code
code --list-extensions | grep cline
```

## Quick Setup

### 1. Install the MCP Server

```bash
# Quick installation
git clone https://github.com/roguedev-ai/kasm-mcp-server.git
cd kasm-mcp-server
./setup-prerequisites.sh --mode python
```

### 2. Configure Cline Settings

Open VS Code settings (`Ctrl+,` or `Cmd+,`) and add:

```json
{
  "cline.mcpServers": {
    "kasm-mcp-server": {
      "command": "python",
      "args": [
        "/home/user/kasm-mcp-server/src/server.py"
      ],
      "env": {
        "KASM_API_URL": "https://your-kasm-server.com",
        "KASM_API_KEY": "your_api_key",
        "KASM_API_SECRET": "your_api_secret"
      }
    }
  }
}
```

### 3. Restart VS Code

Restart VS Code to load the MCP server configuration.

## Detailed Configuration

### Step 1: Server Installation

Choose your preferred installation method:

#### Option A: Local Python Installation

```bash
# Clone repository
git clone https://github.com/roguedev-ai/kasm-mcp-server.git
cd kasm-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Create environment file
cp .env.example .env
nano .env  # Edit with your Kasm credentials
```

#### Option B: NPM Package

```bash
# Global installation
npm install -g kasm-mcp-server

# Or local installation
npm install kasm-mcp-server
```

### Step 2: Cline Configuration File

Create or update your Cline configuration file:

**Location**: `~/.config/Code/User/settings.json` (Linux/Mac) or `%APPDATA%\Code\User\settings.json` (Windows)

```json
{
  "cline.mcpServers": {
    "kasm-mcp-server": {
      "command": "python",
      "args": [
        "${env:HOME}/kasm-mcp-server/src/server.py"
      ],
      "env": {
        "KASM_API_URL": "https://kasm.example.com",
        "KASM_API_KEY": "your_api_key_here",
        "KASM_API_SECRET": "your_api_secret_here",
        "KASM_DEFAULT_IMAGE": "kasmweb/core-ubuntu-focal:1.14.0",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Step 3: Alternative Configuration Methods

#### Using NPX

```json
{
  "cline.mcpServers": {
    "kasm-mcp-server": {
      "command": "npx",
      "args": ["kasm-mcp-server"],
      "env": {
        "KASM_API_URL": "https://kasm.example.com",
        "KASM_API_KEY": "your_api_key",
        "KASM_API_SECRET": "your_api_secret"
      }
    }
  }
}
```

#### Using Docker

```json
{
  "cline.mcpServers": {
    "kasm-mcp-server": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file=/path/to/.env",
        "kasm-mcp-server:latest"
      ]
    }
  }
}
```

### Step 4: Verify Configuration

1. Open VS Code Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Run: `Cline: Show MCP Server Status`
3. Verify that `kasm-mcp-server` appears as "Connected"

## Using the Server with Cline

### Basic Commands

Once configured, you can ask Cline to perform various tasks:

#### 1. Create a New Workspace

```
"Create a new Ubuntu workspace and install Python development tools"
```

Cline will:
1. Call `create_kasm_session` with Ubuntu image
2. Wait for session to be ready
3. Use `execute_kasm_command` to install tools

#### 2. Execute Commands

```
"Run a Python script in my Kasm workspace session abc123"
```

Cline will:
1. Use `execute_kasm_command` to run the script
2. Return the output to you

#### 3. File Operations

```
"Create a configuration file in the workspace with the following content..."
```

Cline will:
1. Use `write_kasm_file` to create the file
2. Optionally use `read_kasm_file` to verify

### Advanced Examples

#### Setting Up Development Environment

```
"Set up a complete Node.js development environment in a new Kasm workspace with:
- Node.js 20
- VS Code Server
- Git configured with my credentials
- A sample Express.js project"
```

#### Batch Operations

```
"Create 5 identical workspaces for a training session, each with:
- Firefox browser
- Development tools
- Training materials from GitHub repo X"
```

#### System Administration

```
"List all active Kasm sessions and terminate any that have been idle for more than 2 hours"
```

## Advanced Features

### Custom Tool Aliases

Create shortcuts for common operations in your VS Code settings:

```json
{
  "cline.customCommands": {
    "kasm-dev": "Create a new development workspace with VS Code, Git, and Node.js",
    "kasm-cleanup": "Terminate all my Kasm sessions",
    "kasm-status": "Show status of all active Kasm workspaces"
  }
}
```

### Workspace Templates

Define reusable workspace configurations:

```json
{
  "cline.mcpServers": {
    "kasm-mcp-server": {
      "command": "python",
      "args": ["src/server.py"],
      "env": {
        "KASM_API_URL": "https://kasm.example.com",
        "KASM_API_KEY": "key",
        "KASM_API_SECRET": "secret",
        "WORKSPACE_TEMPLATES": "/path/to/templates.json"
      }
    }
  }
}
```

### Security Boundaries

Configure file system access restrictions:

```json
{
  "cline.mcpServers": {
    "kasm-mcp-server": {
      "env": {
        "MCP_ROOTS": "/home/kasm_user,/workspace",
        "ENABLE_SUDO": "false",
        "MAX_COMMAND_LENGTH": "1000"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Server Not Connecting

**Symptom**: MCP server shows as "Disconnected" in Cline

**Solutions**:
```bash
# Check if server runs standalone
python ~/kasm-mcp-server/src/server.py

# Check Python path
which python

# Verify environment variables
echo $KASM_API_URL

# Test with absolute paths in settings
"command": "/usr/bin/python3",
"args": ["/absolute/path/to/server.py"]
```

#### 2. Authentication Errors

**Symptom**: "401 Unauthorized" errors

**Solutions**:
```bash
# Test API credentials
curl -X POST https://your-kasm-server.com/api/public/get_user_groups \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_key", "api_secret": "your_secret"}'

# Check environment variables in VS Code
# Developer Tools > Console
console.log(process.env.KASM_API_KEY)
```

#### 3. Command Execution Failures

**Symptom**: Commands fail to execute in workspaces

**Solutions**:
```bash
# Verify session exists
curl -X POST https://your-kasm-server.com/api/public/get_kasm_status \
  -d '{"api_key": "key", "api_secret": "secret", "kasm_id": "session_id"}'

# Check permissions
# Ensure API key has "Sessions Modify" permission
```

#### 4. Path Issues on Windows

**Symptom**: Server fails to start on Windows

**Solutions**:
```json
// Use forward slashes or escaped backslashes
"args": ["C:/Users/user/kasm-mcp-server/src/server.py"]
// OR
"args": ["C:\\Users\\user\\kasm-mcp-server\\src\\server.py"]

// Use environment variables
"args": ["${env:USERPROFILE}/kasm-mcp-server/src/server.py"]
```

### Debug Mode

Enable detailed logging for troubleshooting:

```json
{
  "cline.mcpServers": {
    "kasm-mcp-server": {
      "env": {
        "LOG_LEVEL": "DEBUG",
        "MCP_DEBUG": "true",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

View logs:
1. Open VS Code Output panel (`View > Output`)
2. Select "Cline" from dropdown
3. Look for MCP server messages

## Best Practices

### 1. Security

- **Never hardcode credentials** in settings.json
- Use environment variables or secure credential stores
- Rotate API keys regularly
- Limit API key permissions to minimum required

### 2. Resource Management

- Set session timeouts to prevent resource waste
- Implement automatic cleanup for idle sessions
- Monitor workspace usage and costs

### 3. Error Handling

- Always check session status before executing commands
- Implement retry logic for transient failures
- Log errors for debugging

### 4. Performance

- Cache session information locally
- Batch commands when possible
- Use appropriate workspace images for tasks

### Example: Secure Configuration

```bash
# Store credentials securely
export KASM_API_KEY=$(pass show kasm/api_key)
export KASM_API_SECRET=$(pass show kasm/api_secret)

# Reference in VS Code settings
{
  "cline.mcpServers": {
    "kasm-mcp-server": {
      "command": "python",
      "args": ["src/server.py"],
      "env": {
        "KASM_API_URL": "https://kasm.example.com",
        "KASM_API_KEY": "${env:KASM_API_KEY}",
        "KASM_API_SECRET": "${env:KASM_API_SECRET}"
      }
    }
  }
}
```

## Integration Examples

### Example 1: Development Workflow

```javascript
// Ask Cline:
"Create a Python development workspace and set up a Django project with:
1. Python 3.11
2. PostgreSQL database
3. Redis cache
4. Initial Django app structure
5. Development server running on port 8000"
```

### Example 2: Testing Environment

```javascript
// Ask Cline:
"Set up a testing environment with:
- Selenium Grid hub
- 3 Chrome browser nodes
- Test data from S3 bucket
- Results uploaded to test-results bucket"
```

### Example 3: Training Lab

```javascript
// Ask Cline:
"Prepare 10 identical workspaces for Python training with:
- Jupyter notebook
- Sample datasets
- Exercise files from GitHub
- Solution checking script"
```

## Next Steps

- [LLM Integration Guide](LLM_INTEGRATION_GUIDE.md) - Integrate with other AI systems
- [API Reference](DOCUMENTATION.md) - Complete tool documentation
- [Security Guide](SECURITY.md) - Security best practices
- [Architecture Overview](ARCHITECTURE.md) - System design details

## Support

- **Documentation**: [GitHub Wiki](https://github.com/roguedev-ai/kasm-mcp-server/wiki)
- **Issues**: [GitHub Issues](https://github.com/roguedev-ai/kasm-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/roguedev-ai/kasm-mcp-server/discussions)
