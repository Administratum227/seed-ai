#!/bin/bash

# SEED AI Framework Installer
# This script provides zero-dependency installation of the SEED framework

set -e  # Exit on any error

# Text styling
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"  # No Color

echo_step() {
    echo -e "${BLUE}${BOLD}==>${NC} $1"
}

echo_success() {
    echo -e "${GREEN}${BOLD}✓${NC} $1"
}

echo_error() {
    echo -e "${RED}${BOLD}Error:${NC} $1"
}

# Detect operating system
detect_os() {
    case "$(uname -s)" in
        Darwin*)
            echo "macos"
            ;;
        Linux*)
            echo "linux"
            ;;
        *)
            echo_error "Unsupported operating system"
            exit 1
            ;;
    esac
}

# Install Python if not present
ensure_python() {
    if ! command -v python3 &>/dev/null; then
        case $(detect_os) in
            macos)
                echo_step "Installing Python..."
                if ! command -v brew &>/dev/null; then
                    echo_step "Installing Homebrew first..."
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                fi
                brew install python@3.9
                ;;
            linux)
                echo_step "Installing Python..."
                if command -v apt-get &>/dev/null; then
                    sudo apt-get update
                    sudo apt-get install -y python3.9 python3-pip python3-venv
                elif command -v dnf &>/dev/null; then
                    sudo dnf install -y python39 python3-pip
                else
                    echo_error "Unsupported Linux distribution"
                    exit 1
                fi
                ;;
        esac
    fi
    echo_success "Python is installed"
}

# Set up virtual environment
setup_venv() {
    echo_step "Setting up virtual environment"
    python3 -m venv "$HOME/.seed/env"
    source "$HOME/.seed/env/bin/activate"
    pip install --upgrade pip
    echo_success "Virtual environment created"
}

# Install SEED framework
install_seed() {
    echo_step "Installing SEED AI Framework"
    pip install seed-ai-framework
    echo_success "SEED AI Framework installed"
}

# Create launcher script
create_launcher() {
    mkdir -p "$HOME/.local/bin"
    cat > "$HOME/.local/bin/seed" << 'EOL'
#!/bin/bash
source "$HOME/.seed/env/bin/activate"
exec seed "$@"
EOL
    chmod +x "$HOME/.local/bin/seed"
    
    # Add to PATH if needed
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        # Also add to zsh config if it exists
        if [ -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        fi
    fi
    
    echo_success "Launcher script created"
}

# Main installation flow
main() {
    echo -e "\n${BOLD}SEED AI Framework Installer${NC}\n"
    
    # Create SEED directory structure
    mkdir -p "$HOME/.seed/"{config,data,cache,logs,agents}
    
    # Ensure required tools are installed
    ensure_python
    setup_venv
    install_seed
    create_launcher
    
    echo -e "\n${GREEN}${BOLD}Installation Complete!${NC}"
    echo -e "\nTo get started:"
    echo -e "1. Close and reopen your terminal, or run:"
    echo -e "   source ~/.bashrc  # for bash"
    echo -e "   source ~/.zshrc   # for zsh"
    echo -e "\n2. Then launch the dashboard:"
    echo -e "   seed dashboard"
    echo -e "\nFor help, run: seed --help"
}

# Run the installer
main