# Kasm MCP Server - Complete Tool Reference

This document provides a complete reference for all 21 tools available in the Kasm MCP Server v2.

## Important Note on Parameters

**The `user_id` parameter is NOT required for most tools** - it is automatically obtained from the `KASM_USER_ID` environment variable configured in your `.env` file.

---

## Session Management Tools

### 1. create_kasm_session
Create a new Kasm session with the specified workspace image.

**Parameters:**
- `image_name` (string, required): Name or ID of the workspace image
  - Can be a Docker image name: `"kasmweb/chrome:1.15.0"`
  - Can be an image ID (UUID): `"01366df3a03b4bccbb8c913846594826"`
- `group_id` (string, required): Group ID for the session

**Example:**
```json
{
  "image_name": "kasmweb/ubuntu-focal-desktop",
  "group_id": "68d557ac4cac42cca9f31c7c853de0f3"
}
```

### 2. destroy_kasm_session
Terminate an existing Kasm session.

**Parameters:**
- `kasm_id` (string, required): ID of the session to destroy

**Example:**
```json
{
  "kasm_id": "abc123def456"
}
```

### 3. get_session_status
Get the current status of a Kasm session.

**Parameters:**
- `kasm_id` (string, required): ID of the session

**Returns:** Session status, operational status, URL, creation time, last activity

### 4. list_user_sessions
List all active sessions for the current user.

**Parameters:** None

**Returns:** List of user's active sessions with details

### 5. list_all_sessions
List all active sessions in the system (admin function).

**Parameters:** None

**Returns:** List of all active sessions across all users

### 6. pause_kasm_session
Pause a running session to free up resources.

**Parameters:**
- `kasm_id` (string, required): ID of the session to pause

### 7. resume_kasm_session
Resume a previously paused session.

**Parameters:**
- `kasm_id` (string, required): ID of the session to resume

### 8. get_session_screenshot
Capture a screenshot of a Kasm session.

**Parameters:**
- `kasm_id` (string, required): ID of the session
- `save_to_file` (string, optional): Path to save the screenshot file

**Returns:** Base64 encoded screenshot data or file path if saved

---

## Command Execution

### 9. execute_kasm_command
Execute a shell command inside a Kasm session.

**Parameters:**
- `kasm_id` (string, required): ID of the session
- `command` (string, required): Command to execute
- `working_dir` (string, optional): Working directory for command execution

**Example:**
```json
{
  "kasm_id": "abc123def456",
  "command": "ls -la",
  "working_dir": "/home/kasm-user"
}
```

**Security Notes:**
- Commands are validated against security rules
- System commands like `sudo`, `chmod` on system files are blocked
- Working directory must be within allowed roots

---

## File Operations

### 10. read_kasm_file
Read the contents of a file from a Kasm session.

**Parameters:**
- `kasm_id` (string, required): ID of the session
- `file_path` (string, required): Path to the file to read

**Example:**
```json
{
  "kasm_id": "abc123def456",
  "file_path": "/home/kasm-user/document.txt"
}
```

### 11. write_kasm_file
Write content to a file in a Kasm session.

**Parameters:**
- `kasm_id` (string, required): ID of the session
- `file_path` (string, required): Path where the file should be written
- `content` (string, required): Content to write to the file

**Example:**
```json
{
  "kasm_id": "abc123def456",
  "file_path": "/home/kasm-user/script.py",
  "content": "#!/usr/bin/env python3\nprint('Hello, World!')"
}
```

**Security Notes:**
- File paths must be within allowed roots (default: `/home/kasm-user`)
- Directory traversal attempts are blocked

---

## Workspace Management

### 12. get_available_workspaces
Get a list of all available workspace images.

**Parameters:** None

**Returns:** List of workspace configurations including:
- Image ID
- Image name
- Friendly name
- Description
- Resource requirements (cores, memory, GPU)
- Docker registry and image details

---

## User Management

### 13. get_kasm_users
Get a list of all users in the Kasm system.

**Parameters:** None

**Returns:** List of users with their details

### 14. create_kasm_user
Create a new user account.

**Parameters:**
- `username` (string, required): Username for the new user
- `password` (string, required): Password for the new user
- `first_name` (string, optional): User's first name
- `last_name` (string, optional): User's last name
- `organization` (string, optional): User's organization
- `phone` (string, optional): Phone number
- `locked` (boolean, optional): Whether to lock the account (default: false)
- `disabled` (boolean, optional): Whether to disable the account (default: false)

**Example:**
```json
{
  "username": "john.doe@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

### 15. get_kasm_user
Get details for a specific user.

**Parameters (one required):**
- `user_id` (string, optional): User ID to retrieve
- `username` (string, optional): Username to retrieve

**Example:**
```json
{
  "username": "john.doe@example.com"
}
```

### 16. update_kasm_user
Update an existing user's details.

**Parameters:**
- `user_id` (string, required): User ID to update
- `username` (string, optional): New username
- `password` (string, optional): New password
- `first_name` (string, optional): New first name
- `last_name` (string, optional): New last name
- `organization` (string, optional): New organization
- `phone` (string, optional): New phone number
- `locked` (boolean, optional): New locked status
- `disabled` (boolean, optional): New disabled status

### 17. delete_kasm_user
Delete a user from the system.

**Parameters:**
- `user_id` (string, required): User ID to delete
- `force` (boolean, optional): Force deletion even if user has active sessions (default: false)

### 18. logout_kasm_user
Logout all sessions for a specific user.

**Parameters:**
- `user_id` (string, required): User ID to logout

---

## Performance Monitoring

### 19. get_session_frame_stats
Get frame rendering statistics for performance analysis.

**Parameters:**
- `kasm_id` (string, required): ID of the session
- `client` (string, optional): Which client to retrieve stats for
  - Options: `"none"`, `"auto"`, `"all"`, or specific websocket_id
  - Default: `"auto"`

**Returns:** Frame statistics including:
- Frame timing data
- Encoding time
- Client performance metrics

### 20. get_session_bottleneck_stats
Get CPU and network bottleneck statistics.

**Parameters:**
- `kasm_id` (string, required): ID of the session

**Returns:** Bottleneck statistics showing:
- CPU constraints (0-10 scale, lower = more constrained)
- Network constraints (0-10 scale)
- Average values over time

### 21. get_session_recordings
Get recordings for a specific session.

**Parameters:**
- `kasm_id` (string, required): ID of the session
- `download_links` (boolean, optional): Include pre-authorized download links (default: false)

**Returns:** List of session recordings with:
- Recording ID
- Recording URL
- Metadata
- Optional download links

---

## Environment Variables

These are configured in your `.env` file:

| Variable | Description | Required |
|----------|-------------|----------|
| `KASM_API_URL` | Kasm Workspaces API endpoint | Yes |
| `KASM_API_KEY` | API key for authentication | Yes |
| `KASM_API_SECRET` | API secret for authentication | Yes |
| `KASM_USER_ID` | Your user ID (UUID format) | Yes |
| `KASM_ALLOWED_ROOTS` | Comma-separated allowed directories | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |

---

## Security Features

### MCP Roots Implementation
- File operations are restricted to allowed directories
- Default allowed root: `/home/kasm-user`
- Additional roots can be configured via `KASM_ALLOWED_ROOTS`

### Command Filtering
Blocked commands include:
- System administration: `sudo`, `su`, `passwd`, `useradd`
- Service management: `systemctl`, `service`, `init`
- System control: `shutdown`, `reboot`, `halt`
- File permissions on system files: `chmod`, `chown`

### Path Validation
- Directory traversal (`../`) is prevented
- System directories (`/etc`, `/boot`, `/sys`) are protected
- All paths are validated before operations

---

## Error Handling

All tools return a consistent response format:

**Success Response:**
```json
{
  "success": true,
  "data": "...",
  "message": "Operation completed successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error description",
  "error_type": "security|validation|api|..."
}
```

---

## Usage Examples

### Example 1: Complete Development Setup
```python
# 1. Create session
create_kasm_session(
  image_name="kasmweb/ubuntu-focal-desktop",
  group_id="default_group_id"
)

# 2. Install development tools
execute_kasm_command(
  kasm_id="returned_session_id",
  command="apt-get update && apt-get install -y git python3 python3-pip"
)

# 3. Clone repository
execute_kasm_command(
  kasm_id="session_id",
  command="git clone https://github.com/user/repo.git",
  working_dir="/home/kasm-user"
)

# 4. Create Python script
write_kasm_file(
  kasm_id="session_id",
  file_path="/home/kasm-user/app.py",
  content="print('Hello from Kasm!')"
)

# 5. Run the script
execute_kasm_command(
  kasm_id="session_id",
  command="python3 app.py",
  working_dir="/home/kasm-user"
)
```

### Example 2: User Management
```python
# 1. List all users
get_kasm_users()

# 2. Create new user
create_kasm_user(
  username="test.user@example.com",
  password="SecurePass123!",
  first_name="Test",
  last_name="User"
)

# 3. Get user details
get_kasm_user(username="test.user@example.com")

# 4. Update user
update_kasm_user(
  user_id="returned_user_id",
  locked=true
)
```

### Example 3: Performance Monitoring
```python
# 1. Get session status
get_session_status(kasm_id="session_id")

# 2. Check performance
get_session_frame_stats(
  kasm_id="session_id",
  client="auto"
)

# 3. Check bottlenecks
get_session_bottleneck_stats(kasm_id="session_id")

# 4. Get recordings
get_session_recordings(
  kasm_id="session_id",
  download_links=true
)
```

---

## Troubleshooting

If tools fail:

1. **Check session exists**: Use `list_user_sessions()` to verify
2. **Verify permissions**: Ensure paths are within allowed roots
3. **Check logs**: Set `LOG_LEVEL=DEBUG` for detailed information
4. **Test diagnostics**: Run `python diagnose_session_issue.py`
5. **Validate credentials**: Ensure `.env` has correct API credentials

For session creation issues specifically:
- The server automatically tries different parameter formats
- Image IDs are tried with and without hyphens
- Both `image_id` and `image_name` parameters are attempted
