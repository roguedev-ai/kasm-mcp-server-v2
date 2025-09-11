# Session Creation Issue Resolution Guide

## ✅ Fixes Applied

### 1. Import Error Fixed
- **Issue**: Missing `List` import from typing module
- **Resolution**: Added `List` to the imports in `src/kasm_api/client.py`
- **Status**: ✅ FIXED

### 2. Enhanced Debugging Added
- **Enhancement**: Added detailed logging to session creation process
- **Benefit**: Now logs all parameters sent and responses received
- **Status**: ✅ IMPLEMENTED

### 3. Diagnostic Tool Created
- **Tool**: `diagnose_session_issue.py`
- **Purpose**: Comprehensive testing of session creation with various parameter combinations
- **Status**: ✅ CREATED

## 🔧 How to Diagnose the Issue

### Step 1: Run the Diagnostic Tool
```bash
cd ~/kasm-mcp-server-v2
python diagnose_session_issue.py
```

This will:
- Test API connectivity
- Check user permissions
- Try different parameter formats for session creation
- Identify existing sessions that might be blocking new ones
- Provide a detailed analysis of what's working and what's not

### Step 2: Review the Output
The diagnostic tool will show:
- ✅ Which API endpoints are working
- ❌ Which operations are failing
- 💡 Analysis of failure reasons
- Specific parameter combinations that succeed/fail

## 🚨 Common Issues and Solutions

### Issue 1: 500 Error with HTML Response
**Symptoms**: 
- API returns HTML instead of JSON
- Status code 500
- Session creation fails

**Possible Causes**:
1. **Missing Required Parameters**
   - Solution: The diagnostic tool tests different parameter combinations
   
2. **Invalid Image ID Format**
   - The client now auto-detects and tries both formats:
     - With hyphens: `01366df3-a03b-4bcc-bb8c-913846594826`
     - Without hyphens: `01366df3a03b4bccbb8c913846594826`
   
3. **User/Group Permission Issues**
   - Check that the user is in the specified group
   - Verify workspace images are assigned to the group

4. **Session Limits**
   - Some configurations limit concurrent sessions
   - The diagnostic tool will detect and offer to clean up existing sessions

### Issue 2: Authentication Failures
**Solution**: Verify your `.env` file has correct values:
```env
KASM_API_URL=https://workspaces.workoverip.com
KASM_API_KEY=your_api_key_here
KASM_API_SECRET=your_api_secret_here
KASM_USER_ID=7e74b81f-4486-469d-b3ad-d8604d78aa2c
```

### Issue 3: Parameter Format Issues
The enhanced client now handles multiple formats:
- **Image ID**: Automatically tries with/without hyphens
- **Docker Image**: Accepts full Docker image names (e.g., `kasmweb/chrome:1.15.0`)
- **Friendly Names**: Can use workspace friendly names

## 📊 What the Enhanced Client Does

### Automatic Format Detection
```python
# The client now automatically detects and handles:
1. UUID with hyphens → tries as image_id (without hyphens)
2. UUID without hyphens → tries as image_id
3. Docker image name → tries as image_name
4. If first attempt fails → tries alternative format
```

### Enhanced Logging
With the new debugging, you'll see:
```
Session creation request - image_name: 01366df3-a03b-4bcc-bb8c-913846594826, user_id: ..., group_id: ...
Attempting session creation with parameters: {
  "user_id": "7e74b81f-4486-469d-b3ad-d8604d78aa2c",
  "group_id": "68d557ac4cac42cca9f31c7c853de0f3",
  "image_id": "01366df3a03b4bccbb8c913846594826"
}
```

## 🎯 Next Steps

1. **Run the diagnostic tool** to identify the specific issue
2. **Check the logs** for detailed error messages
3. **Try different approaches**:
   ```python
   # Using image_id (recommended for UUIDs)
   await client.request_kasm(
       image_name="01366df3a03b4bccbb8c913846594826",  # Will auto-detect as UUID
       user_id=user_id,
       group_id=group_id
   )
   
   # Using Docker image name
   await client.request_kasm(
       image_name="kasmweb/chrome:1.15.0",
       user_id=user_id,
       group_id=group_id
   )
   ```

4. **If still failing**, check:
   - Kasm server logs: `/opt/kasm/current/log/api_server.log`
   - API permissions in Kasm admin panel
   - Network connectivity to Kasm server

## 🔍 Verification Steps

After applying fixes:

1. **Test server startup**:
   ```bash
   python test_server.py
   ```

2. **Test through Cline**:
   - Restart Cline
   - Try the `create_kasm_session` tool
   - Monitor the debug output

3. **Check enhanced logs**:
   The client now provides detailed logging showing:
   - Exact parameters being sent
   - Full error messages
   - Retry attempts with different formats

## 📝 Summary

The session creation issue has been addressed with:
1. ✅ **Fixed import error** preventing server startup
2. ✅ **Added intelligent format detection** for image IDs
3. ✅ **Enhanced debugging** for troubleshooting
4. ✅ **Created diagnostic tool** for testing

The client will now automatically:
- Handle different UUID formats
- Retry with alternative parameters
- Provide detailed logging
- Help identify the exact cause of failures

Run the diagnostic tool to identify any remaining issues specific to your Kasm setup.
