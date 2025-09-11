# Kasm MCP Server - Session Creation Fix

## Issue Summary
The Kasm MCP server was failing to create sessions with a 500 error returning HTML instead of JSON. The root cause was incorrect API parameter usage and missing support for image IDs.

## Problems Identified

### 1. Image ID vs Image Name
- **Issue**: The API was only sending `image_name` parameter, but Kasm API expects different parameters based on input type
- **Fix**: Added intelligent detection to use `image_id` for UUIDs and `image_name` for Docker image names

### 2. Command Execution Structure
- **Issue**: The `exec_command` API was using flat parameters instead of the required `exec_config` structure
- **Fix**: Restructured to use proper `exec_config` object with all supported parameters

### 3. Missing API Features
- **Issue**: Several Kasm API endpoints were not implemented
- **Fix**: Added support for frame stats, bottleneck stats, and session recordings

### 4. Poor Error Handling
- **Issue**: HTML error responses were not handled properly
- **Fix**: Added detection and parsing of HTML responses with meaningful error messages

## Changes Made

### 1. KasmAPIClient (`src/kasm_api/client.py`)

#### Session Creation Fix
```python
# Now automatically detects UUID vs Docker image name
async def request_kasm(self, image_name: str, user_id: str, group_id: str):
    uuid_pattern = re.compile(r'^[a-f0-9]{32}$|^[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}$', re.IGNORECASE)
    
    data = {"user_id": user_id, "group_id": group_id}
    
    if uuid_pattern.match(image_name):
        data["image_id"] = image_name.replace('-', '')  # Remove hyphens for consistency
    else:
        data["image_name"] = image_name  # Docker image name
```

#### Command Execution Fix
```python
# Now uses proper exec_config structure
async def exec_command(self, kasm_id: str, user_id: str, command: str, ...):
    exec_config = {
        "cmd": command,
        "workdir": working_dir,
        "environment": environment,
        "privileged": privileged,
        "user": user
    }
    data = {
        "kasm_id": kasm_id,
        "user_id": user_id,
        "exec_config": exec_config
    }
```

#### Enhanced Error Handling
```python
# Better handling of HTML responses
if 'text/html' in content_type:
    error_msg = f"Received HTML response instead of JSON (status {response.status})"
    # Extract error from HTML if possible
    raise Exception(error_msg)
```

### 2. New API Methods Added

- `get_kasm_frame_stats()` - Get frame rendering performance metrics
- `get_kasm_bottleneck_stats()` - Get CPU/network bottleneck statistics  
- `get_session_recordings()` - Get session recording data
- Enhanced `get_kasm_screenshot()` with width/height parameters

### 3. Server Tools (`src/server.py`)

- Updated `create_kasm_session()` to support both image IDs and names
- Added new performance monitoring tools
- Improved error messages for better debugging

## Usage Examples

### Creating a Session with Image ID
```python
# Using image ID (UUID)
result = await create_kasm_session(
    image_name="01366df3a03b4bccbb8c913846594826",  # Chrome image ID
    group_id="68d557ac4cac42cca9f31c7c853de0f3"
)
```

### Creating a Session with Docker Image Name
```python
# Using Docker image name
result = await create_kasm_session(
    image_name="kasmweb/chrome:1.8.0",
    group_id="68d557ac4cac42cca9f31c7c853de0f3"
)
```

### Executing Commands with Full Config
```python
result = await execute_kasm_command(
    kasm_id="session_id",
    command="ls -la",
    working_dir="/home/kasm-user",
    environment={"MY_VAR": "value"},
    privileged=False,
    user="kasm-user"
)
```

### Getting Performance Metrics
```python
# Frame statistics
frame_stats = await get_session_frame_stats(
    kasm_id="session_id",
    client="auto"
)

# Bottleneck statistics
bottleneck_stats = await get_session_bottleneck_stats(
    kasm_id="session_id"
)
```

## Testing the Fix

1. **Test with Image ID**:
   ```json
   {
     "image_name": "01366df3a03b4bccbb8c913846594826",
     "group_id": "68d557ac4cac42cca9f31c7c853de0f3"
   }
   ```

2. **Test with Docker Image Name**:
   ```json
   {
     "image_name": "kasmweb/chrome:1.8.0",
     "group_id": "68d557ac4cac42cca9f31c7c853de0f3"
   }
   ```

3. **Verify Error Handling**:
   - Test with invalid credentials
   - Test with non-existent image IDs
   - Test with malformed requests

## Deployment

After applying these fixes:

1. Restart the MCP server
2. Verify the `.env` file has correct API credentials
3. Test session creation with both image IDs and names
4. Monitor logs for any HTML response errors

## Date Fixed
January 11, 2025

## Files Modified
- `src/kasm_api/client.py` - Core API client fixes
- `src/server.py` - Updated tools and error handling
- Documentation updates
