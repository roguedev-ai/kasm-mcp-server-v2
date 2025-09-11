# Kasm API Authentication Fix

## Issue Discovered
The Kasm Workspaces API was failing with authentication errors because the client was using the wrong parameter name for the API secret.

## Root Cause
The `KasmAPIClient` in `src/kasm_api/client.py` was using `"api_secret"` as the authentication parameter name, but the Kasm API actually expects `"api_key_secret"`.

## Fix Applied
Changed the authentication data structure in the `_make_request` method:

### Before (INCORRECT):
```python
auth_data = {
    "api_key": self.api_key,
    "api_secret": self.api_secret  # WRONG PARAMETER NAME
}
```

### After (CORRECT):
```python
auth_data = {
    "api_key": self.api_key,
    "api_key_secret": self.api_secret  # CORRECT PARAMETER NAME
}
```

## Testing Confirmation
The fix was validated with a test script that showed:
- Using `"api_secret"` resulted in: 401 Unauthorized
- Using `"api_key_secret"` resulted in: 200 OK with 6 images returned

## Files Modified
- `src/kasm_api/client.py`: Line 63 - Changed authentication parameter name

## Deployment
After applying this fix, the server needs to be restarted for the changes to take effect.

## Date Fixed
January 11, 2025
