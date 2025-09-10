#!/bin/bash

# Kasm MCP Server Prerequisites Setup Script
# This script sets up all prerequisites for either NPM/Python or Docker installation
# Author: RogueDev AI
# Version: 1.0.0

set -e  # Exit on error

# ============================================================================
# Configuration and Constants
# ============================================================================

SCRIPT_VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/setup-prerequisites.log"
VENV_DIR="$SCRIPT_DIR/venv"
MIN_PYTHON_VERSION="3.8"
MIN_NODE_VERSION="14"
REPO_URL="https://github.com/roguedev-ai/kasm-mcp-server-v2.git"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

# Print functions with colors
print_header() {
    echo -e "\n${MAGENTA}============================================${NC}"
    echo -e "${MAGENTA}  $1${NC}"
    echo -e "${MAGENTA}============================================${NC}\n"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Compare version numbers
version_compare() {
    # Returns 0 if $1 >= $2
    printf '%s\n%s' "$2" "$1" | sort -V -C
}

# Detect OS and distribution
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        OS_FAMILY=$ID_LIKE
        VER=$VERSION_ID
        OS_NAME=$PRETTY_NAME
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        OS_FAMILY="macos"
        VER=$(sw_vers -productVersion)
        OS_NAME="macOS $VER"
    else
        print_error "Cannot detect operating system"
        exit 1
    fi
    
    # Determine package manager
    if command_exists apt-get; then
        PKG_MANAGER="apt"
    elif command_exists yum; then
        PKG_MANAGER="yum"
    elif command_exists dnf; then
        PKG_MANAGER="dnf"
    elif command_exists brew; then
        PKG_MANAGER="brew"
    else
        print_error "No supported package manager found"
        exit 1
    fi
    
    print_success "Detected: $OS_NAME"
    print_status "Package manager: $PKG_MANAGER"
}

# Check if running with sudo when needed
check_sudo() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. This is not recommended for development setup."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    elif [[ "$1" == "required" ]] && ! sudo -n true 2>/dev/null; then
        print_warning "This operation requires sudo privileges."
        sudo -v
    fi
}

# ============================================================================
# Installation Functions
# ============================================================================

# Install system dependencies
install_system_deps() {
    print_step "Installing system dependencies..."
    
    case $PKG_MANAGER in
        apt)
            sudo apt-get update
            sudo apt-get install -y \
                curl \
                wget \
                git \
                build-essential \
                libssl-dev \
                libffi-dev \
                python3-dev \
                ca-certificates \
                gnupg \
                lsb-release
            ;;
        yum|dnf)
            sudo $PKG_MANAGER install -y \
                curl \
                wget \
                git \
                gcc \
                gcc-c++ \
                make \
                openssl-devel \
                python3-devel \
                ca-certificates
            ;;
        brew)
            brew install \
                curl \
                wget \
                git \
                openssl \
                libffi
            ;;
    esac
    
    print_success "System dependencies installed"
}

# Install Python and pip
install_python() {
    print_step "Setting up Python environment..."
    
    # Check if Python is installed
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if version_compare "$PYTHON_VERSION" "$MIN_PYTHON_VERSION"; then
            print_success "Python $PYTHON_VERSION is already installed"
        else
            print_warning "Python $PYTHON_VERSION is installed but version $MIN_PYTHON_VERSION+ is required"
            install_python_version
        fi
    else
        install_python_version
    fi
    
    # Install pip
    if ! command_exists pip3; then
        print_status "Installing pip..."
        case $PKG_MANAGER in
            apt)
                sudo apt-get install -y python3-pip python3-venv
                ;;
            yum|dnf)
                sudo $PKG_MANAGER install -y python3-pip
                ;;
            brew)
                # pip comes with Python on macOS
                :
                ;;
        esac
    fi
    
    print_success "Python environment ready"
}

# Install specific Python version if needed
install_python_version() {
    print_status "Installing Python $MIN_PYTHON_VERSION+..."
    
    case $PKG_MANAGER in
        apt)
            # Add deadsnakes PPA for newer Python versions on older Ubuntu
            if [[ "$OS" == "ubuntu" ]]; then
                sudo apt-get install -y software-properties-common
                sudo add-apt-repository -y ppa:deadsnakes/ppa
                sudo apt-get update
            fi
            sudo apt-get install -y python3.8 python3.8-venv python3.8-dev
            ;;
        yum|dnf)
            sudo $PKG_MANAGER install -y python38 python38-devel
            ;;
        brew)
            brew install python@3.8
            ;;
    esac
}

# Install Node.js and npm
install_nodejs() {
    print_step "Setting up Node.js and npm..."
    
    if command_exists node; then
        NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [[ $NODE_VERSION -ge $MIN_NODE_VERSION ]]; then
            print_success "Node.js $(node -v) is already installed"
            return
        else
            print_warning "Node.js version is too old, installing newer version..."
        fi
    fi
    
    case $PKG_MANAGER in
        apt)
            # Install Node.js from NodeSource repository
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        yum|dnf)
            curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
            sudo $PKG_MANAGER install -y nodejs
            ;;
        brew)
            brew install node
            ;;
    esac
    
    # Verify installation
    if command_exists node && command_exists npm; then
        print_success "Node.js $(node -v) and npm $(npm -v) installed"
    else
        print_error "Failed to install Node.js/npm"
        exit 1
    fi
}

# Setup Python virtual environment and install dependencies
setup_python_env() {
    print_step "Setting up Python virtual environment..."
    
    cd "$SCRIPT_DIR"
    
    # Create virtual environment
    if [[ -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment already exists. Recreating..."
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install requirements
    if [[ -f "requirements.txt" ]]; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found"
    fi
    
    # Verify MCP installation
    if python -c "import mcp" 2>/dev/null; then
        print_success "MCP SDK is installed"
    else
        print_warning "MCP SDK not found, attempting to install..."
        pip install mcp
    fi
    
    print_success "Python environment configured"
    print_status "Virtual environment location: $VENV_DIR"
}

# Install Docker
install_docker() {
    print_step "Installing Docker..."
    
    if command_exists docker; then
        print_success "Docker is already installed: $(docker --version)"
        return
    fi
    
    case $PKG_MANAGER in
        apt)
            # Add Docker's official GPG key
            sudo mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            
            # Add Docker repository
            echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
                $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # Install Docker
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
            
        yum|dnf)
            # Add Docker repository
            sudo $PKG_MANAGER config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            
            # Install Docker
            sudo $PKG_MANAGER install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
            
        brew)
            brew install --cask docker
            print_warning "Please start Docker Desktop from Applications"
            ;;
    esac
    
    # Start and enable Docker service (Linux only)
    if [[ "$OS" != "macos" ]]; then
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Add current user to docker group
        if [[ $EUID -ne 0 ]]; then
            sudo usermod -aG docker $USER
            print_warning "You've been added to the docker group. Please log out and back in for this to take effect."
        fi
    fi
    
    print_success "Docker installed successfully"
}

# Install Docker Compose
install_docker_compose() {
    print_step "Installing Docker Compose..."
    
    if command_exists docker-compose; then
        print_success "Docker Compose is already installed: $(docker-compose --version)"
        return
    fi
    
    # Check if docker compose (v2) is available
    if docker compose version &>/dev/null; then
        print_success "Docker Compose v2 is available"
        return
    fi
    
    # Install Docker Compose v2 as a Docker plugin (if not already installed)
    case $PKG_MANAGER in
        apt|yum|dnf)
            if [[ ! -f /usr/local/lib/docker/cli-plugins/docker-compose ]]; then
                sudo mkdir -p /usr/local/lib/docker/cli-plugins
                sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) \
                    -o /usr/local/lib/docker/cli-plugins/docker-compose
                sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
            fi
            ;;
        brew)
            # Docker Desktop for Mac includes Docker Compose
            :
            ;;
    esac
    
    print_success "Docker Compose installed"
}

# ============================================================================
# Configuration Functions
# ============================================================================

# Setup environment configuration
setup_env_config() {
    print_step "Setting up environment configuration..."
    
    cd "$SCRIPT_DIR"
    
    if [[ -f ".env" ]]; then
        print_warning ".env file already exists"
        read -p "Do you want to reconfigure it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        print_status "Existing .env backed up"
    fi
    
    if [[ ! -f ".env.example" ]]; then
        print_warning ".env.example not found, creating template..."
        cat > .env.example << 'EOF'
# Kasm API Configuration
KASM_API_URL=https://kasm.example.com
KASM_API_KEY=your_api_key_here
KASM_API_SECRET=your_api_secret_here

# Optional Configuration
KASM_USER_ID=default
KASM_ALLOWED_ROOTS=/home/kasm-user
LOG_LEVEL=INFO

# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080
EOF
    fi
    
    cp .env.example .env
    
    print_status "Please provide your Kasm configuration:"
    echo
    
    read -p "Kasm API URL (e.g., https://kasm.example.com): " KASM_API_URL
    read -p "Kasm API Key: " KASM_API_KEY
    read -s -p "Kasm API Secret: " KASM_API_SECRET
    echo
    
    # Update .env file
    sed -i.bak "s|KASM_API_URL=.*|KASM_API_URL=$KASM_API_URL|" .env
    sed -i.bak "s|KASM_API_KEY=.*|KASM_API_KEY=$KASM_API_KEY|" .env
    sed -i.bak "s|KASM_API_SECRET=.*|KASM_API_SECRET=$KASM_API_SECRET|" .env
    
    # Set proper permissions
    chmod 600 .env
    
    print_success "Environment configuration complete"
}

# ============================================================================
# Testing Functions
# ============================================================================

# Run diagnostic tests
run_diagnostics() {
    print_step "Running diagnostic tests..."
    
    cd "$SCRIPT_DIR"
    
    if [[ -f "test_server.py" ]]; then
        if [[ -d "$VENV_DIR" ]]; then
            source "$VENV_DIR/bin/activate"
        fi
        
        print_status "Running server diagnostics..."
        python test_server.py || true
    else
        print_warning "test_server.py not found, skipping diagnostics"
    fi
}

# Test Docker installation
test_docker() {
    print_step "Testing Docker installation..."
    
    if docker run --rm hello-world &>/dev/null; then
        print_success "Docker is working correctly"
    else
        print_warning "Docker test failed. You may need to restart or check permissions."
    fi
    
    if docker compose version &>/dev/null || docker-compose --version &>/dev/null; then
        print_success "Docker Compose is working correctly"
    else
        print_warning "Docker Compose test failed"
    fi
}

# ============================================================================
# Main Installation Flows
# ============================================================================

# NPM/Python installation flow
install_npm_python_mode() {
    print_header "NPM/Python Installation Mode"
    
    check_sudo required
    install_system_deps
    install_python
    install_nodejs
    setup_python_env
    setup_env_config
    run_diagnostics
    
    print_success "NPM/Python prerequisites installed successfully!"
}

# Docker installation flow
install_docker_mode() {
    print_header "Docker Installation Mode"
    
    check_sudo required
    install_system_deps
    install_docker
    install_docker_compose
    setup_env_config
    test_docker
    
    print_success "Docker prerequisites installed successfully!"
}

# Both modes installation flow
install_both_modes() {
    print_header "Complete Installation (NPM/Python + Docker)"
    
    check_sudo required
    install_system_deps
    install_python
    install_nodejs
    setup_python_env
    install_docker
    install_docker_compose
    setup_env_config
    run_diagnostics
    test_docker
    
    print_success "All prerequisites installed successfully!"
}

# ============================================================================
# Interactive Menu
# ============================================================================

show_menu() {
    print_header "Kasm MCP Server Prerequisites Setup v$SCRIPT_VERSION"
    
    echo "This script will help you set up the prerequisites for running"
    echo "the Kasm MCP Server. Please select your installation mode:"
    echo
    echo -e "${CYAN}1)${NC} NPM/Python Mode - Direct Python execution with npm support"
    echo -e "${CYAN}2)${NC} Docker Mode - Containerized deployment with Docker"
    echo -e "${CYAN}3)${NC} Both - Install prerequisites for both modes"
    echo -e "${CYAN}4)${NC} Configuration Only - Set up .env file only"
    echo -e "${CYAN}5)${NC} Run Diagnostics - Test existing installation"
    echo -e "${CYAN}6)${NC} Exit"
    echo
    read -p "Enter your choice [1-6]: " choice
    
    case $choice in
        1)
            install_npm_python_mode
            ;;
        2)
            install_docker_mode
            ;;
        3)
            install_both_modes
            ;;
        4)
            setup_env_config
            ;;
        5)
            run_diagnostics
            ;;
        6)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            show_menu
            ;;
    esac
}

# ============================================================================
# Display Final Information
# ============================================================================

display_completion_info() {
    echo
    print_header "Installation Complete!"
    
    echo -e "${GREEN}Prerequisites have been successfully installed!${NC}"
    echo
    echo "Next steps:"
    echo
    
    if [[ -d "$VENV_DIR" ]]; then
        echo "For Python/NPM mode:"
        echo "  1. Activate the virtual environment:"
        echo "     source $VENV_DIR/bin/activate"
        echo "  2. Run the server:"
        echo "     python -m src"
        echo "  3. Or run with debug logging:"
        echo "     LOG_LEVEL=DEBUG python -m src"
        echo
    fi
    
    if command_exists docker; then
        echo "For Docker mode:"
        echo "  1. Build the Docker image:"
        echo "     docker-compose build"
        echo "  2. Start the server:"
        echo "     docker-compose up -d"
        echo "  3. View logs:"
        echo "     docker-compose logs -f"
        echo
    fi
    
    echo "Configuration:"
    echo "  - Environment file: $SCRIPT_DIR/.env"
    echo "  - Test installation: python test_server.py"
    echo
    echo "For Cline integration, use the configuration in package.json"
    echo
    print_status "Log file: $LOG_FILE"
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    # Set up logging
    exec > >(tee -a "$LOG_FILE")
    exec 2>&1
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Detect OS
    detect_os
    
    # Show interactive menu
    show_menu
    
    # Display completion information
    display_completion_info
}

# Handle errors
trap 'print_error "An error occurred. Check the log file: $LOG_FILE"' ERR

# Run main function
main "$@"
