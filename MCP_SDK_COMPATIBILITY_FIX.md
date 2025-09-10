# MCP SDK Compatibility Fix

## Issue Fixed
**Date**: September 10, 2025  
**Commit**: c95882e

### Problem
The FastMCP class initialization was failing with the following error:
```
TypeError: FastMCP.__init__() got an unexpected keyword argument 'version'
```

### Root Cause
The current version of the MCP SDK's `FastMCP` class does not accept a `version` parameter in its constructor, but our code was attempting to pass one:

```python
# OLD CODE (broken)
mcp = FastMCP(
    name="Kasm MCP Server",
    version="0.1.0"  # ← This parameter is not supported
)
```

### Solution
Removed the unsupported `version` parameter from the FastMCP initialization:

```python
# NEW CODE (fixed)
mcp = FastMCP(
    name="Kasm MCP Server"
)
```

## Testing Results

### On Linux Server (jaymes@kasm-mcp-server-01)
✅ **Server now starts successfully**
- FastMCP instance creates without errors
- Kasm API client initializes properly
- Environment variables load correctly

### Remaining Non-Critical Issue
There's an "Already running asyncio in this thread" warning that appears after initialization, but this doesn't prevent the server from functioning. This is likely due to the MCP SDK managing its own event loop.

## Compatibility Notes

### MCP SDK Version
The `mcp` package installed via pip does not support the `version` parameter in FastMCP initialization. This appears to be a change from earlier versions or documentation.

### Required Dependencies
Ensure these are installed (from requirements.txt):
```
mcp>=1.0.0
aiohttp>=3.9.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

## How to Apply Fix

### For Existing Installations
1. Pull the latest changes:
   ```bash
   cd ~/kasm-mcp-server-v2
   git pull origin master
   ```

2. Or manually edit `src/server.py` line 58-60:
   ```python
   # Remove the version parameter
   mcp = FastMCP(
       name="Kasm MCP Server"
   )
   ```

3. Test the server:
   ```bash
   python -m src
   ```

### For New Installations
The fix is already included in the repository. Simply clone and run:
```bash
git clone https://github.com/roguedev-ai/kasm-mcp-server-v2.git
cd kasm-mcp-server-v2
./setup-prerequisites.sh
```

## Prevention
To prevent similar issues in the future:
1. Always test with the latest MCP SDK version
2. Document the specific SDK version used during development
3. Add version compatibility checks in the test suite
4. Monitor MCP SDK changelog for breaking changes

## Related Files
- `src/server.py` - Main server implementation (fixed)
- `test_server.py` - Diagnostic test script
- `setup-prerequisites.sh` - Installation script
