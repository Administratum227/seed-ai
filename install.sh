#!/bin/bash

# SEED AI Framework Installer
# Zero-dependency installation script for macOS and Linux
#
# This script provides a robust installation process with:
# - System compatibility checks
# - Dependency management
# - Environment isolation
# - Error recovery
# - Progress feedback

# Enable strict error handling
set -euo pipefail
IFS=$'\n\t'

# Style definitions for user feedback
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m"  # No Color

# Logging utilities for consistent user communication
log_info() { echo -e "${BLUE}${BOLD}==>${NC} $1"; }
log_success() { echo -e "${GREEN}${BOLD}✓${NC} $1"; }
log_error() { echo -e "${RED}${BOLD}Error:${NC} $1" >&2; }
log_warning() { echo -e "${YELLOW}${BOLD}Warning:${NC} $1" >&2; }

# Error handler for graceful failure
handle_error() {
    local line=$1
    local command=$2
    log_error "Command '$command' failed at line $line"
    cleanup_and_exit 1
}

trap 'handle_error "$LINENO" "$BASH_COMMAND"' ERR

# Cleanup function for error recovery
cleanup_and_exit() {
    local exit_code=$1
    if [ $exit_code -ne 0 ]; then
        log_info "Cleaning up after installation failure..."
        # Remove incomplete virtual environment
        [ -d "$HOME/.seed/env" ] && rm -rf "$HOME/.seed/env"
        # Remove incomplete installation files
        [ -d "$HOME/.seed/tmp" ] && rm -rf "$HOME/.seed/tmp"
    fi
    exit "$exit_code"
}

# Detect and validate operating system
detect_os() {
    local os_name
    os_name=$(uname -s)
    
    case "${os_name}" in
        Darwin*)
            echo "macos"
            ;;
        Linux*)
            echo "linux"
            ;;
        *)
            log_error "Unsupported operating system: ${os_name}"
            exit 1
            ;;
    esac
}

# Verify system requirements
check_requirements() {
    log_info "Verifying system requirements"
    
    # Check disk space
    local required_space=500  # MB
    local available_space
    case $(detect_os) in
        macos)
            available_space=$(df -m "$HOME" | awk 'NR==2 {print $4}')
            ;;
        linux)
            available_space=$(df -m "$HOME" | awk 'NR==2 {print $4}')
            ;;
    esac
    
    if [ "${available_space:-0}" -lt "$required_space" ]; then
        log_error "Insufficient disk space. Need ${required_space}MB, have ${available_space}MB"
        exit 1
    fi
    
    # Check internet connectivity
    if ! curl -s -m 5 https://github.com > /dev/null; then
        log_error "No internet connection available"
        exit 1
    fi
    
    log_success "System requirements met"
}

# Install Python if needed
setup_python() {
    if ! command -v python3 &>/dev/null; then
        log_info "Installing Python..."
        case $(detect_os) in
            macos)
                if ! command -v brew &>/dev/null; then
                    log_info "Installing Homebrew..."
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" ||
                        { log_error "Homebrew installation failed"; exit 1; }
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                fi
                brew install python@3.9 ||
                    { log_error "Python installation failed"; exit 1; }
                ;;
            linux)
                if command -v apt-get &>/dev/null; then
                    sudo apt-get update
                    sudo apt-get install -y python3.9 python3-pip python3-venv
                elif command -v dnf &>/dev/null; then
                    sudo dnf install -y python39 python3-pip
                else
                    log_error "Unsupported Linux distribution"
                    exit 1
                fi
                ;;
        esac
    fi
    log_success "Python installed and configured"
}

# Set up virtual environment
setup_venv() {
    log_info "Creating virtual environment"
    python3 -m venv "$HOME/.seed/env" ||
        { log_error "Virtual environment creation failed"; exit 1; }
    
    source "$HOME/.seed/env/bin/activate" ||
        { log_error "Virtual environment activation failed"; exit 1; }
    
    pip install --upgrade pip ||
        { log_error "Pip upgrade failed"; exit 1; }
    
    log_success "Virtual environment ready"
}

# Install SEED framework
install_seed() {
    log_info "Installing SEED AI Framework"
    pip install seed-ai-framework ||
        { log_error "Framework installation failed"; exit 1; }
    log_success "Framework installed"
}

# Create and configure launcher
create_launcher() {
    log_info "Creating launcher"
    
    mkdir -p "$HOME/.local/bin"
    
    # Create launcher script
    cat > "$HOME/.local/bin/seed" << 'EOL'
#!/bin/bash

# Activate SEED environment
SOURCE_ENV="$HOME/.seed/env/bin/activate"
if [ ! -f "$SOURCE_ENV" ]; then
    echo "Error: SEED environment not found"
    echo "Try reinstalling with: curl -sSL https://raw.githubusercontent.com/Administratum227/seed-ai/main/install.sh | bash"
    exit 1
fi

source "$SOURCE_ENV"
exec seed "$@"
EOL

    chmod +x "$HOME/.local/bin/seed" ||
        { log_error "Failed to make launcher executable"; exit 1; }
    
    # Update PATH in shell configurations
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
            if [ -f "$rc" ]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
            fi
        done
    fi
    
    log_success "Launcher configured"
}

# Main installation process
main() {
    echo -e "\n${BOLD}SEED AI Framework Installer${NC}\n"
    
    # Pre-installation checks
    check_requirements
    
    # Create directory structure
    mkdir -p "$HOME/.seed/"{config,data,cache,logs,agents,tmp} ||
        { log_error "Failed to create directory structure"; exit 1; }
    
    # Installation steps
    setup_python
    setup_venv
    install_seed
    create_launcher
    
    # Cleanup temporary files
    rm -rf "$HOME/.seed/tmp"
    
    # Show success message
    echo -e "\n${GREEN}${BOLD}Installation Complete!${NC}"
    echo -e "\nTo get started:"
    echo -e "1. Close and reopen your terminal, or run:"
    echo -e "   source ~/.bashrc  # for bash"
    echo -e "   source ~/.zshrc   # for zsh"
    echo -e "\n2. Then launch the dashboard:"
    echo -e "   seed dashboard"
}

# Start installation
main