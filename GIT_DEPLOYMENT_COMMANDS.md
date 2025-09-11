# Git Commands to Deploy the Session Creation Fix

## Quick Deployment (Copy & Paste)

Run these commands in your console to deploy the fixes:

### 1. Navigate to the project directory
```bash
cd projects/kasm-mcp-server-v2
```

### 2. Check the changes
```bash
git status
git diff src/kasm_api/client.py src/server.py
```

### 3. Commit and push the fixes
```bash
# Add all the fixed files
git add src/kasm_api/client.py src/server.py SESSION_CREATION_FIX.md deploy-session-fix.sh GIT_DEPLOYMENT_COMMANDS.md

# Commit with descriptive message
git commit -m "Fix session creation: Support image_id/name, fix exec_config, add performance tools

- Auto-detect UUID vs Docker image name for session creation
- Fix exec_command to use proper exec_config structure  
- Add frame stats, bottleneck stats, and recording tools
- Improve HTML error response handling
- Add width/height parameters to screenshot method"

# Push to your repository
git push origin main
```

### 4. On your MCP server (via SSH)
```bash
# SSH into your server
ssh your-server

# Navigate to kasm-mcp-server directory
cd /path/to/kasm-mcp-server-v2

# Pull the latest changes
git pull origin main

# Restart the MCP server
# If using systemd:
sudo systemctl restart kasm-mcp-server

# Or if running manually:
# Stop current server (Ctrl+C) and restart:
python -m src.server
```

## Alternative: Use the Deployment Script

We've also created an automated deployment script:

```bash
cd projects/kasm-mcp-server-v2
./deploy-session-fix.sh
```

## Testing the Fix

After deployment, test with Cline using:

### With Image ID (UUID):
```json
{
  "image_name": "01366df3a03b4bccbb8c913846594826",
  "group_id": "68d557ac4cac42cca9f31c7c853de0f3"
}
```

### With Docker Image Name:
```json
{
  "image_name": "kasmweb/chrome:1.8.0",
  "group_id": "68d557ac4cac42cca9f31c7c853de0f3"
}
```

## What Was Fixed

1. **Image ID Detection**: Now automatically detects UUIDs and uses `image_id` parameter
2. **Command Execution**: Fixed to use proper `exec_config` structure
3. **New Tools Added**: Frame stats, bottleneck stats, session recordings
4. **Better Error Handling**: HTML responses are now properly detected and reported

## Files Modified

- `src/kasm_api/client.py` - Core API client fixes
- `src/server.py` - Updated tools and error handling
- `SESSION_CREATION_FIX.md` - Complete documentation
- `deploy-session-fix.sh` - Automated deployment script

## Troubleshooting

If you still get errors after deployment:

1. **Check your .env file** has correct credentials:
   ```
   KASM_API_URL=https://workspaces.workoverip.com
   KASM_API_KEY=your_key_here
   KASM_API_SECRET=your_secret_here
   KASM_USER_ID=7e74b81f-4486-469d-b3ad-d8604d78aa2c
   ```

2. **Verify the user ID format** - remove hyphens if needed

3. **Check server logs** for detailed error messages:
   ```bash
   journalctl -u kasm-mcp-server -f
   # or
   tail -f /var/log/kasm-mcp-server.log
   ```

4. **Test API directly** with the test script:
   ```bash
   python test_api_endpoints.py
   ```

Date: January 11, 2025
