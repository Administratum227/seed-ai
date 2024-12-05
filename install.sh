#!/bin/bash

# SEED AI Framework Installer
# Zero-dependency installation script

set -e  # Exit on error

# Style definitions
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"

# Logging utilities
log_info() { echo -e "${BLUE}${BOLD}==>${NC} $1"; }
log_success() { echo -e "${GREEN}${BOLD}✓${NC} $1"; }
log_error() { echo -e "${RED}${BOLD}Error:${NC} $1" >&2; }

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
            log_error "Unsupported operating system"
            exit 1
            ;;
    esac
}

# Check Python installation
ensure_python() {
    if ! command -v python3 &>/dev/null; then
        log_info "Installing Python..."
        case $(detect_os) in
            macos)
                if ! command -v brew &>/dev/null; then
                    log_info "Installing Homebrew..."
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                fi
                brew install python@3.9
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
    log_success "Python is installed"
}

# Set up virtual environment
setup_venv() {
    log_info "Setting up virtual environment"
    python3 -m venv "$HOME/.seed/env"
    source "$HOME/.seed/env/bin/activate"
    pip install --upgrade pip
    log_success "Virtual environment created"
}

# Install SEED framework
install_seed() {
    log_info "Installing SEED AI Framework"
    pip install seed-ai-framework
    log_success "SEED AI Framework installed"
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
    
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        if [ -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        fi
    fi
}

# Main installation flow
main() {
    echo -e "\n${BOLD}SEED AI Framework Installer${NC}\n"
    
    # Create SEED directory structure
    mkdir -p "$HOME/.seed/"{config,data,cache,logs,agents}
    
    # Ensure dependencies
    ensure_python
    setup_venv
    install_seed
    create_launcher
    
    log_success "Installation complete!"
    echo -e "\nTo get started:"
    echo -e "1. Close and reopen your terminal, or run:"
    echo -e "   source ~/.bashrc  # for bash"
    echo -e "   source ~/.zshrc   # for zsh"
    echo -e "\n2. Then launch the dashboard:"
    echo -e "   seed dashboard"
}

# Run installation
main