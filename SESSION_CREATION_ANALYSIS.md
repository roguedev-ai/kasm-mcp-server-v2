# Kasm MCP Server - Session Creation Issue Analysis

## Problem Summary
The Kasm API is returning HTML error pages (500 status) instead of JSON when attempting to create sessions via `/api/public/request_kasm`.

## Key Observations

1. **Working Endpoints:**
   - `/api/public/get_users` ✅
   - `/api/public/get_images` ✅
   - `/api/public/get_kasms` ✅
   - User management operations ✅

2. **Failing Endpoints:**
   - `/api/public/request_kasm` ❌ (Returns HTML instead of JSON)
   - `/api/public/get_kasm_status` ❌ (Returns HTML instead of JSON)

3. **Error Pattern:**
   ```
   Failed to create session: 500, message='Attempt to decode JSON with unexpected mimetype: text/html'
   ```

## Root Cause Analysis

### Hypothesis 1: Parameter Format Issues
The Kasm API might be expecting specific parameter formats for session creation that differ from other endpoints.

**Evidence:**
- User ID format inconsistency (with/without hyphens)
- Image ID vs Image Name confusion
- Group ID requirements

### Hypothesis 2: Authentication Scope
Session creation might require additional permissions or different authentication handling.

**Evidence:**
- User management works (admin operations)
- Session creation fails (user-specific operations)
- HTML responses typically indicate authentication/authorization errors

### Hypothesis 3: API Version Mismatch
The API might have changed its expected parameters for session creation.

**Evidence:**
- Other endpoints work correctly
- Only session-specific endpoints fail
- HTML error pages often indicate malformed requests

## Solution Approach

### 1. Enhanced Error Handling
- Detect HTML responses and extract meaningful error messages
- Log full request/response details for debugging
- Provide clear error messages to users

### 2. Parameter Validation
- Ensure UUIDs are formatted correctly (with hyphens)
- Auto-detect image_id vs image_name
- Validate all required parameters before making requests

### 3. Request Format Options
- Try both `image_id` and `image_name` parameters
- Support multiple UUID formats
- Add request retry with different parameter combinations

### 4. Debug Capabilities
- Create comprehensive debug script
- Test various parameter combinations
- Log all API interactions

## Testing Strategy

1. **Direct API Testing:**
   - Test raw API calls with curl/httpie
   - Compare successful vs failing requests
   - Identify exact parameter requirements

2. **Parameter Variations:**
   - UUID with/without hyphens
   - image_id vs image_name
   - With/without optional parameters

3. **Authentication Testing:**
   - Verify API key permissions
   - Test with different user contexts
   - Check session limits/quotas

## Implementation Plan

1. ✅ Create debug script to test various API call patterns
2. ✅ Update .env.example with required variables
3. ⏳ Fix client.py to handle HTML responses better
4. ⏳ Add parameter format detection and normalization
5. ⏳ Create comprehensive documentation
6. ⏳ Test and validate fixes
7. ⏳ Deploy to repository

## Known Working Configuration

Based on user feedback:
- Chrome image_id: `01366df3a03b4bccbb8c913846594826`
- User ID: `7e74b81f-4486-469d-b3ad-d8604d78aa2c` (with hyphens)
- Group ID: `68d557ac-4cac-42cc-a9f3-1c7c853de0f3` (with hyphens)

## Next Steps

1. Run the debug script to identify exact failure point
2. Implement fixes based on debug results
3. Test with known working configuration
4. Update documentation with findings
