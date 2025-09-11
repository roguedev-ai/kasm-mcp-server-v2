# User Management API Fix

## Issue Summary
The Kasm MCP Server was experiencing 500 errors when attempting to create users and perform other user management operations. The root cause was a structural mismatch between what the MCP server was sending and what the Kasm API expected.

## Root Cause
The Kasm API requires user data to be wrapped in specific objects (e.g., `target_user`) for user operations, but the MCP server was sending the data directly in the request body.

### Incorrect Structure (Before Fix):
```json
{
    "api_key": "...",
    "api_key_secret": "...",
    "username": "test",
    "password": "pass",
    "first_name": "John",
    "last_name": "Doe"
}
```

### Correct Structure (After Fix):
```json
{
    "api_key": "...",
    "api_key_secret": "...",
    "target_user": {
        "username": "test",
        "password": "pass",
        "first_name": "John",
        "last_name": "Doe",
        "locked": false,
        "disabled": false
    }
}
```

## Files Modified

### 1. `src/kasm_api/client.py`
- Fixed `create_user` method to wrap data in `target_user` object
- Added new user management methods:
  - `get_user()` - Get specific user details
  - `update_user()` - Update user properties
  - `delete_user()` - Delete a user
  - `logout_user()` - Logout user sessions
  - `get_user_attributes()` - Get user preferences
  - `update_user_attributes()` - Update user preferences
- Added proper parameter handling for optional fields

### 2. `src/server.py`
- Updated `create_kasm_user` tool with additional parameters
- Fixed response parsing to extract data from nested `user` object
- Added new MCP tools:
  - `get_kasm_user` - Get user details
  - `update_kasm_user` - Update user info
  - `delete_kasm_user` - Delete a user
  - `logout_kasm_user` - Logout user sessions
- Added comprehensive error logging with traceback

### 3. `test_api_endpoints.py` (New File)
- Created comprehensive test script for all API endpoints
- Tests user creation, retrieval, update, and deletion
- Tests workspace/image management
- Provides clear success/failure indicators

## Testing
Run the test script to validate all endpoints:
```bash
cd projects/kasm-mcp-server-v2
python test_api_endpoints.py
```

## Deployment Instructions

1. **Pull the latest changes on your remote server:**
```bash
ssh devops@10.1.10.180
cd /home/devops/kasm-mcp-server
git pull origin master
```

2. **Restart the MCP server:**
```bash
# Stop the existing server
pkill -f "python3 -m src.server"

# Start the server with the fixes
nohup python3 -m src.server > mcp-server.log 2>&1 &

# Check the logs
tail -f mcp-server.log
```

3. **Test in VSCode with Cline:**
- Open VSCode
- Ensure Cline extension is connected to the MCP server
- Try creating users or managing workspaces
- The 500 errors should now be resolved

## Verification
After deployment, verify the fixes work by:

1. Testing user creation through Cline
2. Running the test script against your production API
3. Checking server logs for any errors

## New Capabilities
With these fixes, the MCP server now supports:
- Complete user lifecycle management (create, read, update, delete)
- User session management (logout all sessions)
- User attribute/preference management
- Proper error handling and logging
- Nested response parsing

## Date Fixed
January 11, 2025
