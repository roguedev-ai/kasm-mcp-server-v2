# Kasm MCP Server - Suggested Prompts Guide

This guide provides example prompts to help you effectively utilize the Kasm MCP Server through Cline or other AI assistants.

## Table of Contents
- [Session Management](#session-management)
- [Command Execution](#command-execution)
- [File Operations](#file-operations)
- [Development Tasks](#development-tasks)
- [User Management](#user-management)
- [Monitoring & Performance](#monitoring--performance)
- [Troubleshooting](#troubleshooting)

---

## Session Management

### Create a New Session
```
"Create a new Ubuntu desktop session"
"Launch a Chrome browser workspace"
"Start a new development environment with VS Code"
"Create a Kasm session with image ID 01366df3a03b4bccbb8c913846594826"
```

### List and Monitor Sessions
```
"Show me all my active Kasm sessions"
"List all sessions in the system" (admin)
"Check the status of session [kasm_id]"
"Show me which workspaces are currently running"
```

### Session Control
```
"Pause my current Kasm session to free up resources"
"Resume the paused session [kasm_id]"
"Destroy all my active sessions"
"Terminate session [kasm_id]"
```

### Session Screenshots
```
"Take a screenshot of my current Kasm session"
"Capture and save a screenshot of session [kasm_id] to /tmp/screenshot.png"
"Show me what's happening in my Ubuntu session"
```

---

## Command Execution

### Basic Commands
```
"Run 'ls -la' in my Kasm session"
"Execute 'pwd' to show the current directory"
"Check the system information with 'uname -a'"
"Show me the running processes with 'ps aux'"
```

### Software Installation
```
"Install git in my Ubuntu session"
"Set up Node.js and npm in the workspace"
"Install Python 3 and pip"
"Install Docker in the Kasm session"
```

### Development Environment Setup
```
"Clone my GitHub repository https://github.com/user/repo into the session"
"Install VS Code extensions for Python development"
"Set up a React development environment"
"Configure git with my name and email"
```

---

## File Operations

### Reading Files
```
"Read the contents of /home/kasm-user/README.md"
"Show me what's in the config.json file"
"Display the Python script at /workspace/main.py"
"Check the logs in /var/log/application.log"
```

### Writing Files
```
"Create a Python hello world script at /home/kasm-user/hello.py"
"Write a configuration file with the following JSON content..."
"Create a bash script that backs up my documents"
"Save this code snippet to /workspace/app.js"
```

### File Management
```
"Create a project structure for a Node.js application"
"Set up a basic HTML/CSS/JS website structure"
"Create a .gitignore file for a Python project"
"Initialize a new npm project with package.json"
```

---

## Development Tasks

### Web Development
```
"Create a simple HTML page with a contact form"
"Build a React component for a todo list"
"Set up an Express.js server with basic routes"
"Create a responsive CSS layout with flexbox"
```

### Python Development
```
"Write a Python script to process CSV files"
"Create a Flask API with CRUD operations"
"Set up a virtual environment and install requirements"
"Write unit tests for the calculator module"
```

### Database Operations
```
"Connect to PostgreSQL and create a new database"
"Write a SQL script to create user tables"
"Back up the MySQL database to a file"
"Run database migrations"
```

### Docker Operations
```
"Build a Docker image from the Dockerfile"
"Run a containerized application"
"Create a docker-compose.yml for my services"
"List all running Docker containers"
```

---

## User Management

### User Creation
```
"Create a new user account for john.doe@example.com"
"Set up a test user with username 'testuser' and password 'Test123!'"
"Create multiple user accounts from this CSV list"
```

### User Information
```
"List all users in the Kasm system"
"Show me details for user [user_id]"
"Find the user with username 'johndoe'"
"Check which groups this user belongs to"
```

### User Modifications
```
"Update the password for user [user_id]"
"Change the email address for username 'johndoe'"
"Lock the account for user [user_id]"
"Enable/disable user account [user_id]"
```

### User Sessions
```
"Logout all sessions for user [user_id]"
"Delete user [user_id] and all their sessions"
"Show me all active sessions for each user"
```

---

## Monitoring & Performance

### Performance Metrics
```
"Get frame rendering statistics for my session"
"Show CPU and network bottleneck stats for session [kasm_id]"
"Monitor the performance of all active sessions"
"Check which sessions are consuming the most resources"
```

### Session Recordings
```
"Get all recordings for session [kasm_id]"
"Download the session recording with pre-authorized link"
"List all available session recordings"
"Show me recordings for multiple sessions"
```

### System Overview
```
"Give me an overview of all available workspaces"
"Show the current system utilization"
"List workspaces sorted by resource requirements"
"Check which workspace images are enabled"
```

---

## Troubleshooting

### Diagnostic Commands
```
"Run the diagnostic script to check session creation"
"Test the connection to the Kasm API"
"Verify my user permissions"
"Check if there are any existing sessions blocking new ones"
```

### Log Analysis
```
"Show me the last 50 lines of the application log"
"Search for errors in the system logs"
"Check the Kasm API response for the last request"
"Display debug information for session creation"
```

### Cleanup Operations
```
"Clean up all orphaned sessions"
"Remove temporary files from /tmp"
"Clear the session cache"
"Destroy all sessions older than 24 hours"
```

---

## Complex Workflows

### Full Development Setup
```
"Set up a complete Python development environment with:
1. Install Python 3.10, pip, and virtualenv
2. Clone my repository from GitHub
3. Create a virtual environment and activate it
4. Install all requirements
5. Run the test suite
6. Start the development server"
```

### CI/CD Pipeline
```
"Create a CI/CD pipeline that:
1. Pulls the latest code from git
2. Runs linting and tests
3. Builds a Docker image
4. Deploys to a test environment
5. Runs integration tests"
```

### Data Processing
```
"Process data files by:
1. Reading all CSV files from /data/input
2. Cleaning and validating the data
3. Merging files based on common keys
4. Generating summary statistics
5. Exporting results to /data/output"
```

### Security Audit
```
"Perform a security check:
1. List all users and their permissions
2. Check for inactive sessions
3. Review system logs for anomalies
4. Verify file permissions in critical directories
5. Generate a security report"
```

---

## Tips for Effective Prompts

### Be Specific
- Include exact file paths when referring to files
- Specify the workspace image name or ID
- Provide complete configuration details

### Chain Operations
- Break complex tasks into steps
- Ask for confirmation between critical operations
- Save outputs for reference

### Error Handling
- Ask to check command success before proceeding
- Request error logs when operations fail
- Have fallback plans for common issues

### Best Practices
- Always destroy sessions when done to free resources
- Use session pausing for temporary breaks
- Regularly check session status
- Clean up temporary files after use

---

## Environment Variables Reference

When working with sessions, these environment variables are automatically available:
- `KASM_USER_ID`: Your user ID (automatically set from .env)
- `KASM_API_URL`: The Kasm API endpoint
- `KASM_ALLOWED_ROOTS`: Directories where file operations are permitted

---

## Security Notes

The MCP server enforces security restrictions:
- File operations are limited to allowed directories (default: `/home/kasm-user`)
- System commands like `sudo`, `chmod` on system files are blocked
- Directory traversal attempts (`../`) are prevented
- Access to system directories (`/etc`, `/boot`, `/sys`) is restricted

---

## Need Help?

If a prompt doesn't work as expected:
1. Check that you have an active session
2. Verify the session ID is correct
3. Ensure file paths are within allowed roots
4. Review the error message for specific issues
5. Run the diagnostic tool: `python diagnose_session_issue.py`
