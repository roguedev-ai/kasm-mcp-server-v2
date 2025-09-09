# Manual Push Instructions for kasm-mcp-server-v2

Due to authentication issues with the Personal Access Token, you'll need to push the changes manually.

## Current Status
- Repository cloned successfully: ✓
- Local changes committed: ✓
- File updated: `install.sh` (repository URL changed to kasm-mcp-server-v2)

## Pending Changes to Push
```
commit 8539a6b (HEAD -> master)
Author: roguedevd <roguedevd@users.noreply.github.com>
Date:   [current date]

    fix: Update repository URL to kasm-mcp-server-v2 in install script
```

## Manual Push Options

### Option 1: Using GitHub Desktop
1. Open GitHub Desktop
2. Add the local repository: `projects/kasm-mcp-server-v2`
3. Push the changes through the GUI

### Option 2: Using Command Line with New PAT
1. Create a new Personal Access Token on GitHub with `repo` scope
2. Run:
   ```bash
   cd projects/kasm-mcp-server-v2
   git push https://YOUR_USERNAME:YOUR_NEW_PAT@github.com/roguedev-ai/kasm-mcp-server-v2.git master
   ```

### Option 3: Using SSH
1. Set up SSH keys if not already done
2. Change remote to SSH:
   ```bash
   cd projects/kasm-mcp-server-v2
   git remote set-url origin git@github.com:roguedev-ai/kasm-mcp-server-v2.git
   git push origin master
   ```

## Verifying PAT Permissions
Your PAT should have at least these permissions:
- [x] repo (Full control of private repositories)
  - [x] repo:status
  - [x] repo_deployment
  - [x] public_repo
  - [x] repo:invite

## Next Steps
Once you've successfully pushed:
1. The install.sh script will be updated in the remote repository
2. Future clones will use the correct repository URL
3. I can continue making changes locally and you can push them as needed
