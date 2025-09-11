#!/bin/bash

# Kasm MCP Server - Session Creation Fix Deployment Script
# This script helps deploy the session creation fixes to your MCP server

echo "=================================="
echo "Kasm MCP Server - Session Fix Deployment"
echo "=================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check command success
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 successful${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
}

# Step 1: Check current directory
echo -e "${YELLOW}Step 1: Checking current directory...${NC}"
if [ -d "src/kasm_api" ] && [ -f "src/server.py" ]; then
    echo -e "${GREEN}✓ In correct directory${NC}"
else
    echo -e "${RED}✗ Not in kasm-mcp-server-v2 directory${NC}"
    echo "Please cd to projects/kasm-mcp-server-v2 first"
    exit 1
fi

# Step 2: Check git status
echo -e "\n${YELLOW}Step 2: Checking git status...${NC}"
git status --short

# Step 3: Add changes
echo -e "\n${YELLOW}Step 3: Adding changes to git...${NC}"
git add src/kasm_api/client.py
git add src/server.py
git add SESSION_CREATION_FIX.md
git add deploy-session-fix.sh
check_status "Git add"

# Step 4: Commit changes
echo -e "\n${YELLOW}Step 4: Committing changes...${NC}"
git commit -m "Fix session creation: Support image_id/name, fix exec_config, add performance tools

- Auto-detect UUID vs Docker image name for session creation
- Fix exec_command to use proper exec_config structure
- Add frame stats, bottleneck stats, and recording tools
- Improve HTML error response handling
- Add width/height parameters to screenshot method"
check_status "Git commit"

# Step 5: Show what will be pushed
echo -e "\n${YELLOW}Step 5: Changes to be pushed:${NC}"
git log --oneline -1

# Step 6: Push to remote
echo -e "\n${YELLOW}Step 6: Pushing to remote repository...${NC}"
echo "Press Enter to push to origin/main (or Ctrl+C to cancel)"
read -r
git push origin main
check_status "Git push"

# Step 7: Provide deployment instructions
echo -e "\n${GREEN}=================================="
echo "✓ Changes successfully pushed!"
echo "==================================${NC}"
echo ""
echo -e "${YELLOW}Now, on your MCP server, run these commands:${NC}"
echo ""
echo "# 1. SSH into your MCP server"
echo "ssh your-server"
echo ""
echo "# 2. Navigate to the kasm-mcp-server directory"
echo "cd /path/to/kasm-mcp-server"
echo ""
echo "# 3. Pull the latest changes"
echo "git pull origin main"
echo ""
echo "# 4. Install any new dependencies"
echo "pip install -r requirements.txt --upgrade"
echo ""
echo "# 5. Restart the MCP server service"
echo "# Option A: If using systemd"
echo "sudo systemctl restart kasm-mcp-server"
echo ""
echo "# Option B: If running manually"
echo "# Stop the current server (Ctrl+C) and restart:"
echo "python -m src.server"
echo ""
echo "# 6. Test the fix with Cline"
echo "# Try creating a session with image ID:"
echo "# image_name: \"01366df3a03b4bccbb8c913846594826\""
echo "# group_id: \"68d557ac4cac42cca9f31c7c853de0f3\""
echo ""
echo -e "${GREEN}=================================="
echo "Deployment script complete!"
echo "==================================${NC}"
