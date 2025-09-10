# Quick Start Guide - Kasm MCP Server

Get the Kasm MCP Server running in 5 minutes! This guide covers the fastest path to a working installation.

## Prerequisites

- Linux or macOS system
- Internet connection
- Kasm Workspaces API credentials

## 🚀 5-Minute Setup

### Step 1: Clone and Navigate

```bash
git clone https://github.com/roguedev-ai/kasm-mcp-server-v2.git
cd kasm-mcp-server-v2
```

### Step 2: Run Setup Script

```bash
./setup-prerequisites.sh
```

When prompted, select **Option 1** (NPM/Python Mode) - this is the fastest setup for Cline integration.

### Step 3: Configure Credentials

When prompted, enter your Kasm credentials:
- **Kasm API URL**: Your Kasm instance URL (e.g., `https://kasm.example.com`)
- **Kasm API Key**: Your API key
- **Kasm API Secret**: Your API secret

### Step 4: Start the Server

```bash
source venv/bin/activate
python -m src
```

You should see:
```
Kasm MCP Server Starting...
FastMCP server instance created successfully
Initialized Kasm API client for https://your-kasm-instance.com
```

## ✅ Verification

Run the diagnostic test to ensure everything is working:

```bash
python test_server.py
```

All tests should pass with green checkmarks (✅).

## 🔌 Connect to Cline

1. Open VSCode
2. Install the Cline (Claude Dev) extension
3. Open Cline settings (gear icon in Cline panel)
4. Add to MCP settings:

```json
{
  "mcpServers": {
    "kasm": {
      "command": "python",
      "args": ["-m", "src"],
      "cwd": "/path/to/kasm-mcp-server-v2",
      "env": {
        "KASM_API_URL": "https://your-kasm-instance.com",
        "KASM_API_KEY": "your_key",
        "KASM_API_SECRET": "your_secret"
      }
    }
  }
}
```

5. Restart Cline to load the MCP server

## 🎯 Test It Out

Ask Cline to:
- "List available Kasm workspaces"
- "Create a new Ubuntu session"
- "Execute a command in the Kasm session"

## 🆘 Need Help?

If something doesn't work:

1. Check the logs: `LOG_LEVEL=DEBUG python -m src`
2. Run diagnostics: `python test_server.py`
3. See [Troubleshooting](README.md#-troubleshooting)
4. Read the [full Installation Guide](INSTALLATION_GUIDE.md)

---

**That's it!** You now have a working Kasm MCP Server connected to your AI assistant. 🎉
