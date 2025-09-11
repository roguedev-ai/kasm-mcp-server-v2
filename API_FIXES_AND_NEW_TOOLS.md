# Kasm MCP Server - API Fixes and New Tools

## Summary of Changes

This document contains all the changes made to fix the Kasm API endpoints and add new high-priority tools to the MCP server.

## 1. Fixed API Endpoints

### Issue
- The server was using `/api/public/get_workspaces` which doesn't exist in Kasm API
- This was causing 404 errors when trying to list available workspaces

### Solution
- Changed to use `/api/public/get_images` which is the correct endpoint
- Updated method from GET to POST as required by Kasm API

## 2. Files Modified

### A. `src/kasm_api/client.py`

**Changes:**
1. Renamed `get_workspaces()` to `get_images()` 
2. Changed from GET to POST method
3. Added new API methods for high-priority tools:
   - `get_user_kasms()` - List user's active sessions
   - `get_kasms()` - List all active sessions (admin)
   - `pause_kasm()` - Pause a session
   - `resume_kasm()` - Resume a paused session
   - `get_kasm_screenshot()` - Get session screenshot

### B. `src/server.py`

**Changes:**
1. Updated `get_available_workspaces()` tool to use `get_images()` API
2. Fixed response parsing to handle "images" array instead of "workspaces"
3. Added new MCP tools:
   - `list_user_sessions()` - List all sessions for current user
   - `list_all_sessions()` - List all sessions in system (admin)
   - `pause_kasm_session()` - Pause a running session
   - `resume_kasm_session()` - Resume a paused session
   - `get_session_screenshot()` - Capture session screenshot

## 3. New Tools Added

### Session Management Tools

1. **list_user_sessions**
   - Lists all active sessions for the current user
   - No parameters required
   - Returns session details including ID, status, URL

2. **list_all_sessions** (Admin)
   - Lists all active sessions in the system
   - Requires admin permissions
   - Returns detailed session info including user info

3. **pause_kasm_session**
   - Pauses a running session to free resources
   - Parameters: `kasm_id`
   - Useful for resource management

4. **resume_kasm_session**
   - Resumes a paused session
   - Parameters: `kasm_id`
   - Returns session URL

5. **get_session_screenshot**
   - Captures a screenshot of the session
   - Parameters: `kasm_id`, `save_to_file` (optional)
   - Returns base64 encoded image or saves to file

## 4. Manual Deployment Instructions

Since the remote server is not reachable, follow these steps to deploy:

### Option 1: Copy Files Directly

1. Copy the updated `server.py`:
```bash
scp projects/kasm-mcp-server-v2/src/server.py jaymes@10.1.10.180:/home/jaymes/kasm-mcp-server-v2/src/server.py
```

2. Copy the updated `kasm_api/client.py`:
```bash
scp projects/kasm-mcp-server-v2/src/kasm_api/client.py jaymes@10.1.10.180:/home/jaymes/kasm-mcp-server-v2/src/kasm_api/client.py
```

### Option 2: Apply Changes via SSH

1. SSH into the server:
```bash
ssh jaymes@10.1.10.180
```

2. Navigate to the project:
```bash
cd /home/jaymes/kasm-mcp-server-v2
```

3. Make the changes manually or pull from git if you've pushed them.

### Testing After Deployment

1. Test the server starts without errors:
```bash
cd /home/jaymes/kasm-mcp-server-v2
source venv/bin/activate
python3 -m src.server
```

2. The server should hang without errors (that's good!). Press Ctrl+C to exit.

## 5. Verifying in Cline

After deployment, you should be able to:

1. Use `get_available_workspaces` to list available Kasm images
2. Use `list_user_sessions` to see your active sessions
3. Use the new pause/resume tools for resource management
4. Capture screenshots of running sessions

## 6. Next Steps

Once these changes are deployed:

1. Test the API authentication is working
2. Verify all tools are accessible through Cline
3. Consider adding medium-priority tools:
   - Update/delete user functions
   - Group management
   - Session logs retrieval
   - System statistics

## 7. API Endpoint Reference

Here's a quick reference of the corrected Kasm API endpoints now being used:

| Tool | Kasm API Endpoint | Method |
|------|-------------------|--------|
| get_available_workspaces | /api/public/get_images | POST |
| list_user_sessions | /api/public/get_user_kasms | POST |
| list_all_sessions | /api/public/get_kasms | POST |
| pause_kasm_session | /api/public/pause_kasm | POST |
| resume_kasm_session | /api/public/resume_kasm | POST |
| get_session_screenshot | /api/public/get_kasm_screenshot | POST |

## Troubleshooting

If you still get API errors after deployment:

1. **Check API credentials**: Ensure KASM_API_KEY and KASM_API_SECRET are correct in the .env file
2. **Verify API URL**: Make sure KASM_API_URL points to your Kasm instance (e.g., https://workspaces.workoverip.com)
3. **Check permissions**: Some endpoints require specific Kasm permissions
4. **Review logs**: Set LOG_LEVEL=DEBUG in .env for detailed logging

## Complete File Contents

The complete updated files are available in:
- `projects/kasm-mcp-server-v2/src/server.py`
- `projects/kasm-mcp-server-v2/src/kasm_api/client.py`

You can view these files locally and copy their contents to the remote server when you have access.
