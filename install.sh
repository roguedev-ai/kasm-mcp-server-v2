#!/bin/bash

# Kasm MCP Server Remote Installation Script
# This script automates the deployment of the Kasm MCP Server on a Linux host

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/roguedev-ai/kasm-mcp-server.git"
INSTALL_DIR="/opt/kasm-mcp-server"
SERVICE_NAME="kasm-mcp-server"
SERVICE_USER="mcp-server"
LOG_FILE="/var/log/kasm-mcp-server-install.log"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Function to detect OS
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        print_error "Cannot detect OS"
        exit 1
    fi
    print_status "Detected OS: $OS $VER"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    case $OS in
        ubuntu|debian)
            apt-get update
            apt-get install -y \
                docker.io \
                docker-compose \
                git \
                curl \
                wget \
                python3 \
                python3-pip \
                systemd
            ;;
        centos|rhel|fedora)
            yum install -y \
                docker \
                docker-compose \
                git \
                curl \
                wget \
                python3 \
                python3-pip \
                systemd
            ;;
        *)
            print_error "Unsupported OS: $OS"
            exit 1
            ;;
    esac
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    print_success "Dependencies installed"
}

# Function to create service user
create_service_user() {
    print_status "Creating service user..."
    
    if id "$SERVICE_USER" &>/dev/null; then
        print_warning "User $SERVICE_USER already exists"
    else
        useradd -r -s /bin/false -m -d /home/$SERVICE_USER $SERVICE_USER
        usermod -aG docker $SERVICE_USER
        print_success "Service user created"
    fi
}

# Function to clone repository
clone_repository() {
    print_status "Cloning repository..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        print_warning "Installation directory already exists. Backing up..."
        mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    git clone "$REPO_URL" "$INSTALL_DIR"
    chown -R $SERVICE_USER:$SERVICE_USER "$INSTALL_DIR"
    
    print_success "Repository cloned"
}

# Function to configure the server
configure_server() {
    print_status "Configuring server..."
    
    cd "$INSTALL_DIR"
    
    # Check if .env file exists
    if [[ ! -f .env ]]; then
        cp .env.example .env
        
        print_status "Please provide configuration values:"
        
        # Prompt for Kasm API URL
        read -p "Enter Kasm API URL (e.g., https://kasm.example.com): " KASM_API_URL
        
        # Prompt for API credentials
        read -p "Enter Kasm API Key: " KASM_API_KEY
        read -s -p "Enter Kasm API Secret: " KASM_API_SECRET
        echo
        
        # Update .env file
        sed -i "s|KASM_API_URL=.*|KASM_API_URL=$KASM_API_URL|" .env
        sed -i "s|KASM_API_KEY=.*|KASM_API_KEY=$KASM_API_KEY|" .env
        sed -i "s|KASM_API_SECRET=.*|KASM_API_SECRET=$KASM_API_SECRET|" .env
        
        # Set proper permissions
        chmod 600 .env
        chown $SERVICE_USER:$SERVICE_USER .env
        
        print_success "Configuration completed"
    else
        print_warning ".env file already exists, skipping configuration"
    fi
}

# Function to build Docker image
build_docker_image() {
    print_status "Building Docker image..."
    
    cd "$INSTALL_DIR"
    
    # Build the image
    docker-compose build
    
    print_success "Docker image built"
}

# Function to create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Kasm MCP Server
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/docker-compose up
ExecStop=/usr/bin/docker-compose down
Restart=always
RestartSec=10

# Environment
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    systemctl daemon-reload
    
    print_success "Systemd service created"
}

# Function to start the service
start_service() {
    print_status "Starting service..."
    
    systemctl enable ${SERVICE_NAME}.service
    systemctl start ${SERVICE_NAME}.service
    
    # Wait for service to start
    sleep 5
    
    if systemctl is-active --quiet ${SERVICE_NAME}.service; then
        print_success "Service started successfully"
    else
        print_error "Failed to start service"
        systemctl status ${SERVICE_NAME}.service
        exit 1
    fi
}

# Function to display final information
display_info() {
    print_success "Installation completed!"
    echo
    echo "=========================================="
    echo "Kasm MCP Server Installation Summary"
    echo "=========================================="
    echo "Installation directory: $INSTALL_DIR"
    echo "Service name: $SERVICE_NAME"
    echo "Service user: $SERVICE_USER"
    echo "Server URL: http://$(hostname -I | awk '{print $1}'):8080"
    echo
    echo "Useful commands:"
    echo "  - Check status: systemctl status $SERVICE_NAME"
    echo "  - View logs: journalctl -u $SERVICE_NAME -f"
    echo "  - Restart service: systemctl restart $SERVICE_NAME"
    echo "  - Stop service: systemctl stop $SERVICE_NAME"
    echo
    echo "To configure Cline, add the following to your MCP settings:"
    echo '{'
    echo '  "mcpServers": {'
    echo '    "kasm": {'
    echo '      "url": "http://'"$(hostname -I | awk '{print $1}')"':8080",'
    echo '      "transport": "http+sse"'
    echo '    }'
    echo '  }'
    echo '}'
    echo "=========================================="
}

# Function to handle errors
handle_error() {
    print_error "Installation failed. Check the log file: $LOG_FILE"
    exit 1
}

# Set up error handling
trap handle_error ERR

# Main installation flow
main() {
    print_status "Starting Kasm MCP Server installation..."
    
    # Create log file
    mkdir -p $(dirname "$LOG_FILE")
    exec > >(tee -a "$LOG_FILE")
    exec 2>&1
    
    # Run installation steps
    check_root
    detect_os
    install_dependencies
    create_service_user
    clone_repository
    configure_server
    build_docker_image
    create_systemd_service
    start_service
    display_info
}

# Run main function
main "$@"
