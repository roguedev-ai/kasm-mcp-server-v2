# GitHub Repository Setup for Kasm MCP Server

## Creating the Repository

1. Go to https://github.com/new or click the "+" icon in GitHub and select "New repository"

2. Configure the repository:
   - **Repository name**: `kasm-mcp-server`
   - **Description**: "Model Context Protocol (MCP) server for Kasm Workspaces automation - enables AI agents to manage containerized desktop infrastructure"
   - **Visibility**: Choose Public or Private based on your preference
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)

3. Click "Create repository"

## Connecting Your Local Repository

After creating the repository on GitHub, run these commands in your terminal:

```bash
cd projects/kasm-mcp-server

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/kasm-mcp-server.git

# Push the code to GitHub
git push -u origin main
```

## Alternative: Using GitHub CLI

If you have GitHub CLI installed, you can create the repository directly:

```bash
cd projects/kasm-mcp-server

# Create the repository and push
gh repo create kasm-mcp-server --public --source=. --remote=origin --push
```

## Verifying the Setup

After pushing, your repository should be available at:
`https://github.com/YOUR_USERNAME/kasm-mcp-server`

## Updating the Install Script

Once the repository is created, update the `install.sh` script to use your repository URL:

1. Edit `install.sh`
2. Find the line with `REPO_URL`
3. Update it to: `REPO_URL="https://github.com/YOUR_USERNAME/kasm-mcp-server.git"`

## For MCP Tools Listing

To get your server listed on mcp.tools:
1. Ensure your repository is public
2. Submit your repository URL to the MCP tools registry
3. The package.json and mcp.json files are already configured correctly
