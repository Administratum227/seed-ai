#!/bin/bash

# SEED AI Framework Installer
# Zero-dependency installation script for macOS and Linux

# Enable strict error handling
set -euo pipefail
IFS=$'\n\t'

# Style definitions for clear user feedback
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"  # No Color

# Logging utilities for consistent user communication
log_info() { echo -e "${BLUE}${BOLD}==>${NC} $1"; }
log_success() { echo -e "${GREEN}${BOLD}✓${NC} $1"; }
log_error() { echo -e "${RED}${BOLD}Error:${NC} $1" >&2; }

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

# Ensure Python is installed and properly configured
setup_python() {
    if ! command -v python3 &>/dev/null; then
        log_info "Installing Python..."
        
        case $(detect_os) in
            macos)
                if ! command -v brew &>/dev/null; then
                    log_info "Installing Homebrew..."
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
                        log_error "Homebrew installation failed"
                        exit 1
                    }
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                fi
                brew install python@3.9 || {
                    log_error "Python installation failed"
                    exit 1
                }
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
    
    # Verify Python installation
    python3 --version || {
        log_error "Python installation verification failed"
        exit 1
    }
    
    log_success "Python is installed and configured"
}

# Set up isolated virtual environment
setup_venv() {
    log_info "Creating virtual environment"
    
    # Create virtual environment
    python3 -m venv "$HOME/.seed/env" || {
        log_error "Virtual environment creation failed"
        exit 1
    }
    
    # Activate virtual environment
    # shellcheck disable=SC1091
    source "$HOME/.seed/env/bin/activate" || {
        log_error "Virtual environment activation failed"
        exit 1
    }
    
    # Update pip to latest version
    pip install --upgrade pip || {
        log_error "Pip upgrade failed"
        exit 1
    }
    
    log_success "Virtual environment created and activated"
}

# Install SEED framework and dependencies
install_seed() {
    log_info "Installing SEED AI Framework"
    
    # Install core framework
    pip install seed-ai-framework || {
        log_error "SEED framework installation failed"
        exit 1
    }
    
    log_success "SEED AI Framework installed successfully"
}

# Create system launcher and configure PATH
create_launcher() {
    log_info "Creating launcher script"
    
    # Create bin directory
    mkdir -p "$HOME/.local/bin"
    
    # Create launcher script
    cat > "$HOME/.local/bin/seed" << 'EOL'
#!/bin/bash

# Activate SEED environment
SOURCE_ENV="$HOME/.seed/env/bin/activate"
if [ ! -f "$SOURCE_ENV" ]; then
    echo "Error: SEED environment not found at $HOME/.seed/env"
    echo "Try reinstalling with: curl -sSL https://raw.githubusercontent.com/Administratum227/seed-ai/main/scripts/install.sh | bash"
    exit 1
fi

source "$SOURCE_ENV"
exec seed "$@"
EOL

    # Make launcher executable
    chmod +x "$HOME/.local/bin/seed" || {
        log_error "Failed to make launcher executable"
        exit 1
    }
    
    # Update PATH in shell configurations
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
            if [ -f "$rc" ]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
            fi
        done
    fi
    
    log_success "Launcher script created and configured"
}

# Main installation process
main() {
    echo -e "\n${BOLD}SEED AI Framework Installer${NC}\n"
    
    # Create directory structure
    mkdir -p "$HOME/.seed/"{config,data,cache,logs,agents} || {
        log_error "Failed to create directory structure"
        exit 1
    }
    
    # Run installation steps
    setup_python
    setup_venv
    install_seed
    create_launcher
    
    # Show success message and next steps
    echo -e "\n${GREEN}${BOLD}Installation Complete!${NC}"
    echo -e "\nTo get started:"
    echo -e "1. Close and reopen your terminal, or run:"
    echo -e "   source ~/.bashrc  # for bash"
    echo -e "   source ~/.zshrc   # for zsh"
    echo -e "\n2. Then launch the dashboard:"
    echo -e "   seed dashboard"
}

# Execute main installation process
main