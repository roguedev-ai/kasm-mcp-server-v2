#!/bin/bash

# Deploy API Authentication Fix to Remote Server
# This script updates the remote Kasm MCP server with the api_key_secret fix

set -e

echo "==================================="
echo "Kasm MCP Server API Fix Deployment"
echo "==================================="
echo ""

# Configuration
REMOTE_HOST="10.1.10.180"
REMOTE_USER="devops"
REMOTE_DIR="/home/devops/kasm-mcp-server"

echo "Target server: ${REMOTE_USER}@${REMOTE_HOST}"
echo "Remote directory: ${REMOTE_DIR}"
echo ""

# First, commit and push the changes locally
echo "Step 1: Committing changes locally..."
cd /home/kasm-user/my-projects-agent/projects/kasm-mcp-server-v2

# Check if there are changes to commit
if git diff --quiet && git diff --cached --quiet; then
    echo "No changes to commit"
else
    git add src/kasm_api/client.py API_AUTH_FIX.md
    git commit -m "Fix: Use correct api_key_secret parameter for Kasm API authentication

- Changed 'api_secret' to 'api_key_secret' in auth_data
- This fixes the 401 Unauthorized errors when calling Kasm API
- Validated with testing that api_key_secret is the correct parameter"
    echo "Changes committed"
fi

echo ""
echo "Step 2: Pushing to GitHub..."
git push origin master || {
    echo "Note: If push fails, you may need to pull first with:"
    echo "git pull origin master --rebase"
    echo "Then run this script again"
}

echo ""
echo "Step 3: Updating remote server..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
    set -e
    echo "Connected to remote server"
    
    # Navigate to the project directory
    cd /home/devops/kasm-mcp-server
    
    # Pull the latest changes
    echo "Pulling latest changes from GitHub..."
    git pull origin master
    
    # Find and kill the existing server process
    echo "Stopping existing MCP server..."
    pkill -f "python3 -m src.server" || true
    sleep 2
    
    # Start the server again
    echo "Starting MCP server with the fix..."
    nohup python3 -m src.server > mcp-server.log 2>&1 &
    
    echo "Server restarted with PID: $!"
    echo ""
    
    # Verify the server is running
    sleep 3
    if pgrep -f "python3 -m src.server" > /dev/null; then
        echo "✅ MCP server is running with the API fix applied"
        echo ""
        echo "Recent log output:"
        tail -n 10 mcp-server.log
    else
        echo "❌ Failed to start MCP server"
        echo "Check the logs:"
        tail -n 20 mcp-server.log
        exit 1
    fi
EOF

echo ""
echo "===================================="
echo "Deployment Complete!"
echo "===================================="
echo ""
echo "The API authentication fix has been deployed."
echo ""
echo "You can now test the connection from Cline:"
echo "1. In VSCode, open Cline settings"
echo "2. The MCP server should connect successfully"
echo "3. Try using 'get_available_workspaces' tool to verify API calls work"
echo ""
echo "To monitor the server logs on the remote host:"
echo "ssh ${REMOTE_USER}@${REMOTE_HOST} 'tail -f /home/devops/kasm-mcp-server/mcp-server.log'"
