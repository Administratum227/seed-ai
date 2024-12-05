#!/bin/bash

# SEED AI Framework Installer
# Provides zero-dependency installation with comprehensive error handling

# Strict error handling
set -o errexit  # Exit on error
set -o pipefail # Exit if any command in a pipe fails
set -o nounset  # Exit on undefined variables

# Global error trap
trap 'handle_error "$LINENO" "$BASH_COMMAND"' ERR

# Style definitions
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m"

# Logging functions
log_info() { echo -e "${BLUE}${BOLD}==>${NC} $1"; }
log_success() { echo -e "${GREEN}${BOLD}✓${NC} $1"; }
log_error() { echo -e "${RED}${BOLD}Error:${NC} $1" >&2; }
log_warning() { echo -e "${YELLOW}${BOLD}Warning:${NC} $1" >&2; }

# Error handler
handle_error() {
    local line=$1
    local command=$2
    log_error "Command '$command' failed at line $line"
    
    # Check specific error conditions
    case $command in
        *brew*)
            log_error "Homebrew operation failed. Checking common issues..."
            check_homebrew_issues
            ;;
        *pip*)
            log_error "Python package installation failed. Checking environment..."
            check_python_environment
            ;;
        *python*)
            log_error "Python operation failed. Verifying installation..."
            check_python_installation
            ;;
    esac
    
    cleanup_and_exit 1
}

# Environment verification
verify_environment() {
    log_info "Verifying system environment"
    
    # Check disk space
    local required_space=500  # MB
    local available_space
    case "$(uname)" in
        Darwin)
            available_space=$(df -m "$HOME" | awk 'NR==2 {print $4}')
            ;;
        Linux)
            available_space=$(df -m "$HOME" | awk 'NR==2 {print $4}')
            ;;
    esac
    
    if [ "${available_space:-0}" -lt "$required_space" ]; then
        log_error "Insufficient disk space. Need at least ${required_space}MB, have ${available_space}MB"
        cleanup_and_exit 1
    fi
    
    # Check internet connectivity
    if ! curl -s -m 5 https://github.com > /dev/null; then
        log_error "No internet connection available"
        cleanup_and_exit 1
    fi
    
    # Check required commands
    local required_commands=("curl" "git")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            install_required_command "$cmd"
        fi
    done
}

# Install required command
install_required_command() {
    local cmd=$1
    log_info "Installing required command: $cmd"
    
    case "$(uname)" in
        Darwin)
            if ! command -v brew >/dev/null 2>&1; then
                log_info "Installing Homebrew first..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" ||
                    { log_error "Homebrew installation failed"; cleanup_and_exit 1; }
            fi
            brew install "$cmd" ||
                { log_error "Failed to install $cmd"; cleanup_and_exit 1; }
            ;;
        Linux)
            if command -v apt-get >/dev/null 2>&1; then
                sudo apt-get update && sudo apt-get install -y "$cmd" ||
                    { log_error "Failed to install $cmd"; cleanup_and_exit 1; }
            elif command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y "$cmd" ||
                    { log_error "Failed to install $cmd"; cleanup_and_exit 1; }
            else
                log_error "Unsupported Linux distribution"
                cleanup_and_exit 1
            fi
            ;;
    esac
}

# Homebrew issue checker
check_homebrew_issues() {
    if [ -d "/usr/local/Homebrew" ] && [ ! -w "/usr/local/Homebrew" ]; then
        log_error "Homebrew directory permissions issue detected"
        log_info "Try running: sudo chown -R $(whoami) /usr/local/Homebrew"
    fi
    
    if ! xcode-select -p >/dev/null 2>&1; then
        log_error "Xcode Command Line Tools not found"
        log_info "Install them with: xcode-select --install"
    fi
}

# Python environment checker
check_python_environment() {
    local venv_dir="$HOME/.seed/env"
    
    if [ ! -f "$venv_dir/bin/python" ]; then
        log_error "Virtual environment not properly created"
        log_info "Try removing $venv_dir and running the installer again"
        return 1
    fi
    
    if ! "$venv_dir/bin/python" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
        log_error "Python version requirement not met (need >= 3.9)"
        log_info "Current version: $($venv_dir/bin/python --version)"
        return 1
    fi
}

# Python installation checker
check_python_installation() {
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python 3 not found"
        case "$(uname)" in
            Darwin)
                log_info "Install Python with: brew install python@3.9"
                ;;
            Linux)
                if command -v apt-get >/dev/null 2>&1; then
                    log_info "Install Python with: sudo apt-get install python3.9"
                elif command -v dnf >/dev/null 2>&1; then
                    log_info "Install Python with: sudo dnf install python39"
                fi
                ;;
        esac
        return 1
    fi
}

# Cleanup function
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

# Installation steps with recovery
install_seed() {
    # Create temporary directory for downloads
    local tmp_dir="$HOME/.seed/tmp"
    mkdir -p "$tmp_dir"
    
    # Verify environment first
    verify_environment
    
    # Setup Python virtual environment
    log_info "Creating virtual environment"
    python3 -m venv "$HOME/.seed/env" ||
        { log_error "Failed to create virtual environment"; cleanup_and_exit 1; }
    
    # Activate virtual environment
    source "$HOME/.seed/env/bin/activate" ||
        { log_error "Failed to activate virtual environment"; cleanup_and_exit 1; }
    
    # Upgrade pip
    log_info "Upgrading pip"
    pip install --upgrade pip ||
        { log_error "Failed to upgrade pip"; cleanup_and_exit 1; }
    
    # Install SEED framework
    log_info "Installing SEED AI Framework"
    pip install seed-ai-framework ||
        { log_error "Failed to install SEED framework"; cleanup_and_exit 1; }
    
    # Create launcher
    create_launcher ||
        { log_error "Failed to create launcher"; cleanup_and_exit 1; }
    
    # Cleanup
    rm -rf "$tmp_dir"
    
    log_success "Installation completed successfully!"
}

# Main execution
main() {
    echo -e "\n${BOLD}SEED AI Framework Installer${NC}\n"
    
    # Create SEED directory structure
    mkdir -p "$HOME/.seed/"{config,data,cache,logs,agents} ||
        { log_error "Failed to create directory structure"; exit 1; }
    
    # Run installation
    install_seed
    
    # Show post-installation instructions
    echo -e "\n${GREEN}${BOLD}Next Steps:${NC}"
    echo -e "1. Close and reopen your terminal, or run:"
    echo -e "   source ~/.bashrc  # for bash"
    echo -e "   source ~/.zshrc   # for zsh"
    echo -e "\n2. Start the dashboard:"
    echo -e "   seed dashboard"
    echo -e "\nFor help, run: seed --help"
}

# Start installation
main