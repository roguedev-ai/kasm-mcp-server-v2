#!/bin/bash

# Update Remote Server Script for Kasm MCP Server
# This script helps update the remote server with the latest code

echo "========================================="
echo "Kasm MCP Server - Remote Update Helper"
echo "========================================="
echo ""

# Configuration
REMOTE_HOST="jaymes@10.1.10.180"
REMOTE_DIR="/home/jaymes/kasm-mcp-server-v2"
LOCAL_DIR="projects/kasm-mcp-server-v2"

echo "Configuration:"
echo "  Remote: $REMOTE_HOST:$REMOTE_DIR"
echo "  Local:  $LOCAL_DIR"
echo ""

# Function to update via git
update_via_git() {
    echo "Option 1: Update via Git (Recommended)"
    echo "---------------------------------------"
    echo ""
    echo "1. First, commit and push your local changes:"
    echo ""
    echo "   cd $LOCAL_DIR"
    echo "   git add ."
    echo "   git commit -m 'Fix asyncio conflict in server.py'"
    echo "   git push origin main"
    echo ""
    echo "2. Then, pull changes on the remote server:"
    echo ""
    echo "   ssh $REMOTE_HOST 'cd $REMOTE_DIR && git pull origin main'"
    echo ""
}

# Function to update specific file
update_file_directly() {
    echo "Option 2: Copy file directly via SCP"
    echo "-------------------------------------"
    echo ""
    echo "Run this command to copy the fixed server.py:"
    echo ""
    echo "   scp $LOCAL_DIR/src/server.py $REMOTE_HOST:$REMOTE_DIR/src/server.py"
    echo ""
}

# Function to test the fix
test_fix() {
    echo "Testing the Fix"
    echo "---------------"
    echo ""
    echo "After updating, test the server:"
    echo ""
    echo "   ssh $REMOTE_HOST 'cd $REMOTE_DIR && source venv/bin/activate && python3 -m src.server'"
    echo ""
    echo "It should hang without errors (that's good!). Press Ctrl+C to exit."
    echo ""
}

# Main menu
echo "Choose your update method:"
echo ""
update_via_git
update_file_directly
echo ""
test_fix
echo ""
echo "========================================="
echo "After updating, configure Cline:"
echo "========================================="
echo ""
echo "Add to your cline_mcp_settings.json:"
echo ""
cat << 'EOF'
{
  "mcpServers": {
    "kasm-mcp-server": {
      "command": "ssh",
      "args": [
        "jaymes@10.1.10.180",
        "cd /home/jaymes/kasm-mcp-server-v2 && source venv/bin/activate && python3 -m src.server"
      ]
    }
  }
}
EOF
echo ""
echo "Then restart VS Code to apply the changes!"
