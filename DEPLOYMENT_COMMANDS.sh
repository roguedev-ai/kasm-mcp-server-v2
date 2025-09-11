#!/bin/bash

# Deployment Commands for Kasm MCP Server V2
# Run these from: /home/kasm-user/my-projects-agent

echo "========================================="
echo "Deploying Kasm MCP Server Updates"
echo "========================================="

# Option 1: Run from the my-projects-agent directory (RECOMMENDED)
echo ""
echo "Option 1: From /home/kasm-user/my-projects-agent directory:"
echo "-------------------------------------------------------------"
echo ""
echo "1. Copy the updated server.py:"
echo "   scp projects/kasm-mcp-server-v2/src/server.py jaymes@10.1.10.180:/home/jaymes/kasm-mcp-server-v2/src/server.py"
echo ""
echo "2. Copy the updated kasm_api/client.py:"
echo "   scp projects/kasm-mcp-server-v2/src/kasm_api/client.py jaymes@10.1.10.180:/home/jaymes/kasm-mcp-server-v2/src/kasm_api/client.py"
echo ""

# Option 2: Using absolute paths (works from anywhere)
echo "Option 2: Using absolute paths (works from any directory):"
echo "-----------------------------------------------------------"
echo ""
echo "1. Copy the updated server.py:"
echo "   scp /home/kasm-user/my-projects-agent/projects/kasm-mcp-server-v2/src/server.py jaymes@10.1.10.180:/home/jaymes/kasm-mcp-server-v2/src/server.py"
echo ""
echo "2. Copy the updated kasm_api/client.py:"
echo "   scp /home/kasm-user/my-projects-agent/projects/kasm-mcp-server-v2/src/kasm_api/client.py jaymes@10.1.10.180:/home/jaymes/kasm-mcp-server-v2/src/kasm_api/client.py"
echo ""

# Option 3: Navigate first then copy
echo "Option 3: Navigate to project directory first:"
echo "-----------------------------------------------"
echo ""
echo "1. Navigate to the project:"
echo "   cd /home/kasm-user/my-projects-agent/projects/kasm-mcp-server-v2"
echo ""
echo "2. Copy the updated server.py:"
echo "   scp src/server.py jaymes@10.1.10.180:/home/jaymes/kasm-mcp-server-v2/src/server.py"
echo ""
echo "3. Copy the updated kasm_api/client.py:"
echo "   scp src/kasm_api/client.py jaymes@10.1.10.180:/home/jaymes/kasm-mcp-server-v2/src/kasm_api/client.py"
echo ""

echo "========================================="
echo "Testing After Deployment"
echo "========================================="
echo ""
echo "After copying the files, test the server:"
echo ""
echo "ssh jaymes@10.1.10.180"
echo "cd /home/jaymes/kasm-mcp-server-v2"
echo "source venv/bin/activate"
echo "python3 -m src.server"
echo ""
echo "The server should start without errors. Press Ctrl+C to exit."
echo ""
echo "========================================="
