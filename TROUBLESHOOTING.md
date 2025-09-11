# Kasm MCP Server - Troubleshooting Guide

## Common Issues and Solutions

### 1. Session Creation Fails with HTML Response (500 Error)

**Symptoms:**
- Error message: `Failed to create session: 500, message='Attempt to decode JSON with unexpected mimetype: text/html'`
- User management operations work fine
- Session creation returns HTML error pages instead of JSON

**Possible Causes:**

#### A. Missing or Invalid User ID
- The server requires a valid UUID for `KASM_USER_ID`
- Ensure it's not set to "default" or empty
- Format should be: `7e74b81f-4486-469d-b3ad-d8604d78aa2c` (with hyphens)

**Solution:**
```bash
# Check your .env file
KASM_USER_ID=7e74b81f-4486-469d-b3ad-d8604d78aa2c  # Use your actual user UUID
KASM_GROUP_ID=68d557ac-4cac-42cc-a9f3-1c7c853de0f3  # Use your actual group UUID
```

#### B. Image ID vs Image Name Confusion
- The API expects different parameters depending on whether you're using an image ID or name
- Image IDs should be 32 hex characters without hyphens
- Image names should be in Docker format (e.g., `kasmweb/chrome:1.16.0`)

**Solution:**
The updated client automatically detects and handles both formats:
- UUIDs are treated as image_id (hyphens removed)
- Docker-style names are treated as image_name

#### C. Authentication/Permission Issues
- API key might not have session creation permissions
- User might not be in the specified group
- Session limits might be reached

**Solution:**
Run the diagnostic script to identify the exact issue:
```bash
cd projects/kasm-mcp-server-v2
./test_kasm_api_direct.sh
```

### 2. Debugging Session Creation Issues

#### Step 1: Test Direct API Access
Use the provided test script to make direct API calls:
```bash
cd projects/kasm-mcp-server-v2
./test_kasm_api_direct.sh
```

This will test:
- User list retrieval (baseline test)
- Image list retrieval
- Session creation with various parameter combinations
- Active session queries

#### Step 2: Run Python Debug Script
For more detailed debugging with the Python client:
```bash
cd projects/kasm-mcp-server-v2
python debug_session_creation.py
```

This script tests multiple variations and provides detailed error messages.

#### Step 3: Check API Response Details
If you're getting HTML responses, check for:
- Authentication errors (401/403)
- Server errors (500)
- Invalid parameters (400)

The HTML title often contains useful error information.

### 3. UUID Format Issues

**Problem:** Inconsistent UUID formats (with/without hyphens)

**Solution:** The updated implementation handles this automatically:
- User IDs: Keep original format (typically with hyphens)
- Group IDs: Keep original format (typically with hyphens)  
- Image IDs: Automatically converted to no-hyphen format

### 4. Environment Variable Issues

**Problem:** Missing or incorrect environment variables

**Required Variables:**
```bash
KASM_API_URL=https://workspaces.workoverip.com
KASM_API_KEY=your-api-key
KASM_API_SECRET=your-api-secret
KASM_USER_ID=7e74b81f-4486-469d-b3ad-d8604d78aa2c
KASM_GROUP_ID=68d557ac-4cac-42cc-a9f3-1c7c853de0f3
```

**How to Get These Values:**
1. **API Key & Secret**: Generated in Kasm Admin UI → Settings → API
2. **User ID**: Found in Kasm Admin UI → Users → Select User → Copy UUID
3. **Group ID**: Found in Kasm Admin UI → Groups → Select Group → Copy UUID

### 5. Testing Session Creation

After fixing configuration issues, test session creation:

```python
# Using MCP tool (from Cline)
{
  "image_name": "01366df3a03b4bccbb8c913846594826",  # Chrome image ID
  "group_id": "68d557ac-4cac-42cc-a9f3-1c7c853de0f3"
}

# Or with Docker image name
{
  "image_name": "kasmweb/chrome:1.16.0",
  "group_id": "68d557ac-4cac-42cc-a9f3-1c7c853de0f3"
}
```

### 6. Known Working Configurations

Based on testing, these configurations are known to work:

**Chrome Session:**
- Image ID: `01366df3a03b4bccbb8c913846594826`
- Image Name: `kasmweb/chrome:1.16.0`

**Firefox Session:**
- Image Name: `kasmweb/firefox:1.16.0`

**Ubuntu Desktop:**
- Image Name: `kasmweb/ubuntu-noble-desktop:1.16.0`

### 7. Quick Fixes Applied

The following fixes have been implemented:

1. **Removed "default" fallbacks** for KASM_USER_ID
2. **Added startup validation** to ensure valid UUID is provided
3. **Improved error handling** for HTML responses
4. **Auto-detection** of image_id vs image_name
5. **Retry logic** with different parameter formats

### 8. If Issues Persist

If you're still experiencing issues after applying these fixes:

1. **Check Kasm Server Logs:**
   ```bash
   docker logs kasm_api
   ```

2. **Verify Network Connectivity:**
   ```bash
   curl -X POST https://your-kasm-instance.com/api/public/get_users \
     -H "Content-Type: application/json" \
     -d '{"api_key":"your-key","api_key_secret":"your-secret"}'
   ```

3. **Contact Support:**
   - Include the output from `test_kasm_api_direct.sh`
   - Include your Kasm server version
   - Include any error messages from Kasm server logs

## Useful Commands

### Check Server Status
```bash
cd projects/kasm-mcp-server-v2
python -c "from src.server import main; import asyncio; asyncio.run(main())"
```

### Test API Connection
```bash
cd projects/kasm-mcp-server-v2
python test_api_endpoints.py
```

### Validate Environment
```bash
cd projects/kasm-mcp-server-v2
python -c "import os; print('User ID:', os.getenv('KASM_USER_ID')); print('Valid:', len(os.getenv('KASM_USER_ID', '').replace('-', '')) == 32)"
```

## Additional Resources

- [SESSION_CREATION_ANALYSIS.md](SESSION_CREATION_ANALYSIS.md) - Detailed analysis of the issue
- [test_kasm_api_direct.sh](test_kasm_api_direct.sh) - Direct API testing script
- [debug_session_creation.py](debug_session_creation.py) - Python debug script
- [DOCUMENTATION.md](DOCUMENTATION.md) - Full API documentation
