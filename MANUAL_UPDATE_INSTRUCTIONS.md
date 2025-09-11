# Manual Update Instructions for Remote Server

## What Was Fixed
✅ Fixed the API structure issue causing 500 errors
✅ Added complete user management capabilities
✅ Added 5 new MCP tools for user operations
✅ Enhanced error logging and response parsing

## Step-by-Step Update Instructions

### 1. SSH to Your Remote Server
```bash
ssh devops@10.1.10.180
```

### 2. Navigate to the Project Directory
```bash
cd /home/devops/kasm-mcp-server
```

### 3. Pull the Latest Changes from GitHub
```bash
git pull origin master
```

### 4. Stop the Current MCP Server
```bash
pkill -f "python3 -m src.server"
```

### 5. Start the Updated MCP Server
```bash
nohup python3 -m src.server > mcp-server.log 2>&1 &
```

### 6. Verify the Server is Running
```bash
# Check if the process is running
ps aux | grep "python3 -m src.server"

# Check the logs for any errors
tail -f mcp-server.log
```

Press `Ctrl+C` to stop following the logs.

## Testing the Fixes

### Option 1: Test with the Provided Script
```bash
# While still on the remote server
cd /home/devops/kasm-mcp-server
python3 test_api_endpoints.py
```

### Option 2: Test with Cline in VSCode
1. Open VSCode
2. Ensure Cline is connected to your MCP server
3. Try creating users or managing workspaces
4. The 500 errors should now be resolved

## New Capabilities Available in Cline

You can now use these new tools through Cline:
- `create_kasm_user` - Create new users with full control
- `get_kasm_user` - Get specific user details
- `update_kasm_user` - Update user information
- `delete_kasm_user` - Delete users
- `logout_kasm_user` - Logout all user sessions

## Troubleshooting

If you encounter any issues:

1. **Check the logs:**
   ```bash
   tail -100 mcp-server.log
   ```

2. **Verify environment variables are set:**
   ```bash
   cat .env
   ```
   Ensure `KASM_API_URL`, `KASM_API_KEY`, and `KASM_API_SECRET` are correct.

3. **Test the API directly:**
   ```bash
   python3 test_api_endpoints.py
   ```

4. **Restart the server:**
   ```bash
   pkill -f "python3 -m src.server"
   nohup python3 -m src.server > mcp-server.log 2>&1 &
   ```

## Success Indicators

You'll know the fix is working when:
- ✅ No more 500 errors in Cline
- ✅ User creation succeeds
- ✅ The test script shows all green checkmarks
- ✅ Server logs show successful API calls

## Support

If you continue to experience issues after following these steps:
1. Check the `USER_MANAGEMENT_FIX.md` file for detailed information
2. Review the server logs for specific error messages
3. Run the test script to identify which operations are failing

---
Last Updated: January 11, 2025
