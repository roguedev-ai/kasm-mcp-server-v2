#!/bin/bash

# Setup script for creating GitHub repository for kasm-mcp-server-v2

echo "==================================="
echo "Kasm MCP Server V2 GitHub Setup"
echo "==================================="
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "src" ]; then
    echo "Error: This script must be run from the kasm-mcp-server-v2 directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git branch -m main
    git add .
    git commit -m "Initial commit: Kasm MCP Server v2 with 9 tools and comprehensive documentation"
fi

echo "Current git status:"
git status --short

echo ""
echo "==================================="
echo "Next Steps:"
echo "==================================="
echo ""
echo "1. Create a new repository on GitHub:"
echo "   - Go to: https://github.com/new"
echo "   - Repository name: kasm-mcp-server-v2"
echo "   - Description: Model Context Protocol (MCP) server for Kasm Workspaces automation"
echo "   - DO NOT initialize with README, .gitignore, or license"
echo ""
echo "2. After creating the repository, run these commands:"
echo ""
echo "   # Replace YOUR_USERNAME with your GitHub username"
echo "   git remote add origin https://github.com/YOUR_USERNAME/kasm-mcp-server-v2.git"
echo "   git push -u origin main"
echo ""
echo "3. Update the install.sh script with your repository URL"
echo ""
echo "==================================="
echo ""

# Offer to check if gh CLI is available
if command -v gh &> /dev/null; then
    echo "GitHub CLI detected! You can create the repository automatically:"
    echo ""
    echo "Run this command to create and push:"
    echo "gh repo create kasm-mcp-server-v2 --public --source=. --remote=origin --push"
    echo ""
else
    echo "Tip: Install GitHub CLI (gh) for easier repository creation:"
    echo "https://cli.github.com/"
fi

echo ""
echo "Repository is ready to be pushed to GitHub!"
