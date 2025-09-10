# Kasm MCP Server - Complete Installation Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
4. [Detailed Installation Steps](#detailed-installation-steps)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Upgrading](#upgrading)
9. [Uninstallation](#uninstallation)

## Overview

The Kasm MCP Server can be installed in multiple ways depending on your needs:
- **Direct Python Installation**: For development and testing
- **NPM Package Installation**: For integration with Cline and Node.js applications
- **Docker Deployment**: For production environments

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+, Debian 11+, or RHEL/CentOS 8+
- **Python**: 3.8 or higher
- **Memory**: Minimum 2GB RAM
- **Network**: Internet connection for API access
- **Kasm Workspaces**: Access to a Kasm Workspaces instance

### Required Credentials
- Kasm API key and secret
- Kasm server URL
- Appropriate permissions for session management

## Installation Methods

### Method 1: Automated Setup Script (Recommended)

The easiest way to install is using our automated setup script:

```bash
# Download the repository
git clone https://github.com/roguedev-ai/kasm-mcp-server.git
cd kasm-mcp-server

# Run the setup script
chmod +x setup-prerequisites.sh
./setup-prerequisites.sh
```

The script provides an interactive menu with options for:
1. **Complete Installation** - Full setup with all components
2. **Python/NPM Setup** - For development environments
3. **Docker Setup** - For containerized deployments
4. **Check Prerequisites** - Verify system requirements
5. **Environment Setup** - Configure API credentials

### Method 2: Manual Python Installation

For direct Python installation:

```bash
# Clone the repository
git clone https://github.com/roguedev-ai/kasm-mcp-server.git
cd kasm-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Method 3: NPM Package Installation

For Node.js/Cline integration:

```bash
# Install Node.js and npm if not present
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install the MCP server package
npm install -g kasm-mcp-server

# Or install locally in your project
npm install kasm-mcp-server
```

### Method 4: Docker Installation

For containerized deployment:

```bash
# Clone the repository
git clone https://github.com/roguedev-ai/kasm-mcp-server.git
cd kasm-mcp-server

# Build the Docker image
docker build -t kasm-mcp-server:latest .

# Run with environment variables
docker run -d \
  --name kasm-mcp-server \
  -e KASM_API_URL=https://your-kasm-server.com \
  -e KASM_API_KEY=your_api_key \
  -e KASM_API_SECRET=your_api_secret \
  -p 3000:3000 \
  kasm-mcp-server:latest
```

## Detailed Installation Steps

### Step 1: System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install basic dependencies
sudo apt install -y \
  curl \
  wget \
  git \
  build-essential \
  python3-dev \
  python3-pip \
  python3-venv
```

### Step 2: Clone the Repository

```bash
# Choose installation directory
mkdir -p ~/mcp-servers
cd ~/mcp-servers

# Clone the repository
git clone https://github.com/roguedev-ai/kasm-mcp-server.git
cd kasm-mcp-server
```

### Step 3: Run Setup Script

```bash
# Make script executable
chmod +x setup-prerequisites.sh

# Run with default options
./setup-prerequisites.sh

# Or run with specific mode
./setup-prerequisites.sh --mode complete  # Full installation
./setup-prerequisites.sh --mode python    # Python/NPM only
./setup-prerequisites.sh --mode docker    # Docker only
```

### Step 4: Configure Environment

The setup script will prompt for configuration, or you can manually create `.env`:

```bash
# Create .env file
cat > .env << EOF
KASM_API_URL=https://your-kasm-server.com
KASM_API_KEY=your_api_key_here
KASM_API_SECRET=your_api_secret_here
KASM_DEFAULT_IMAGE=kasmweb/core-ubuntu-focal:1.14.0
LOG_LEVEL=INFO
EOF

# Secure the file
chmod 600 .env
```

### Step 5: Verify Installation

```bash
# Test the server
python src/server.py

# Or if installed via npm
npx kasm-mcp-server

# Check Docker container
docker ps | grep kasm-mcp-server
```

## Configuration

### Environment Variables

All configuration is done through environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `KASM_API_URL` | Kasm Workspaces server URL | Yes | - |
| `KASM_API_KEY` | API authentication key | Yes | - |
| `KASM_API_SECRET` | API authentication secret | Yes | - |
| `KASM_DEFAULT_IMAGE` | Default workspace image | No | `kasmweb/core-ubuntu-focal:1.14.0` |
| `LOG_LEVEL` | Logging verbosity | No | `INFO` |
| `MCP_PORT` | Server port (Docker only) | No | `3000` |

### Advanced Configuration

For production environments, additional configuration options:

```bash
# Production .env example
KASM_API_URL=https://kasm.example.com
KASM_API_KEY=prod_key_xxxxx
KASM_API_SECRET=prod_secret_xxxxx
KASM_DEFAULT_IMAGE=custom/workspace:latest
LOG_LEVEL=WARNING
MAX_SESSIONS=10
SESSION_TIMEOUT=3600
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Verification

### Testing the Installation

1. **Check Python Installation**:
```bash
python -c "from src.server import mcp; print('Server imported successfully')"
```

2. **Test Server Startup**:
```bash
# Start the server
python src/server.py

# In another terminal, check if it responds
echo '{"jsonrpc": "2.0", "method": "initialize", "id": 1}' | python src/server.py
```

3. **Verify API Connection**:
```bash
# Test API connectivity
python -c "
import os
from src.kasm_api.client import KasmAPIClient
client = KasmAPIClient(
    api_url=os.getenv('KASM_API_URL'),
    api_key=os.getenv('KASM_API_KEY'),
    api_secret=os.getenv('KASM_API_SECRET')
)
print('API connection successful')
"
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. API Authentication Failures
```bash
# Error: 401 Unauthorized
# Solution: Verify API credentials
echo $KASM_API_KEY
echo $KASM_API_SECRET

# Test credentials directly
curl -X POST https://your-kasm-server.com/api/public/get_user_groups \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_key", "api_secret": "your_secret"}'
```

#### 3. Permission Denied
```bash
# Error: Permission denied on script execution
# Solution: Set execute permissions
chmod +x setup-prerequisites.sh
chmod +x install.sh
```

#### 4. Docker Issues
```bash
# Error: Cannot connect to Docker daemon
# Solution: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Restart Docker service
sudo systemctl restart docker
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Set debug environment variable
export LOG_LEVEL=DEBUG

# Run server with verbose output
python src/server.py 2>&1 | tee debug.log
```

## Upgrading

### Updating to Latest Version

```bash
# Navigate to installation directory
cd ~/mcp-servers/kasm-mcp-server

# Pull latest changes
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart the server
pkill -f "python src/server.py"
python src/server.py &
```

### Docker Update

```bash
# Stop current container
docker stop kasm-mcp-server

# Pull latest image or rebuild
docker pull kasm-mcp-server:latest
# OR
docker build -t kasm-mcp-server:latest .

# Start new container
docker run -d \
  --name kasm-mcp-server \
  --env-file .env \
  -p 3000:3000 \
  kasm-mcp-server:latest
```

## Uninstallation

### Complete Removal

```bash
# Stop any running servers
pkill -f "python src/server.py"

# Remove Docker containers
docker stop kasm-mcp-server
docker rm kasm-mcp-server
docker rmi kasm-mcp-server:latest

# Remove npm package
npm uninstall -g kasm-mcp-server

# Remove installation directory
rm -rf ~/mcp-servers/kasm-mcp-server

# Remove virtual environment (if created separately)
rm -rf ~/mcp-venv
```

### Partial Removal

To keep configuration but remove the application:

```bash
# Backup configuration
cp .env ~/.env.kasm-mcp-backup

# Remove application files
rm -rf src/ tests/ *.py

# Configuration can be restored later
cp ~/.env.kasm-mcp-backup .env
```

## Next Steps

- [Cline Integration Guide](CLINE_INTEGRATION_GUIDE.md) - Set up with Cline
- [LLM Integration Guide](LLM_INTEGRATION_GUIDE.md) - Integrate with other LLMs
- [API Reference](DOCUMENTATION.md) - Complete API documentation
- [Security Guide](SECURITY.md) - Security best practices

## Support

For issues or questions:
- GitHub Issues: [https://github.com/roguedev-ai/kasm-mcp-server/issues](https://github.com/roguedev-ai/kasm-mcp-server/issues)
- Documentation: [https://github.com/roguedev-ai/kasm-mcp-server/wiki](https://github.com/roguedev-ai/kasm-mcp-server/wiki)
