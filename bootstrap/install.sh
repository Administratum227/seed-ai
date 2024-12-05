#!/bin/bash
# SEED AI Framework Bootstrap Installer
# Provides zero-dependency installation on fresh systems

set -e  # Exit on any error

# Text styling
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
NC="\033[0m"  # No Color

print_step() {
    echo -e "${BLUE}${BOLD}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}${BOLD}✓${NC} $1"
}

check_platform() {
    case "$(uname -s)" in
        Darwin*)    
            OS="macos"
            ;;
        Linux*)     
            OS="linux"
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                DISTRO=$ID
            fi
            ;;
        *)
            echo "Unsupported operating system"
            exit 1
            ;;
    esac
}

setup_macos() {
    print_step "Setting up macOS environment..."
    
    # Install Command Line Tools if needed
    if ! xcode-select -p &>/dev/null; then
        print_step "Installing Command Line Tools..."
        xcode-select --install
        # Wait for installation to complete
        until xcode-select -p &>/dev/null; do
            sleep 5
        done
        print_success "Command Line Tools installed"
    fi
    
    # Install Homebrew if needed
    if ! command -v brew &>/dev/null; then
        print_step "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(/opt/homebrew/bin/brew shellenv)"
        print_success "Homebrew installed"
    fi
    
    brew update
    
    # Install Python if needed
    if ! command -v python3 &>/dev/null; then
        print_step "Installing Python..."
        brew install python@3.9
        print_success "Python installed"
    fi
}

setup_linux() {
    print_step "Setting up Linux environment..."
    
    case $DISTRO in
        ubuntu|debian)
            # Update package lists
            sudo apt-get update
            
            # Install Python and dependencies
            sudo apt-get install -y \
                python3.9 \
                python3-pip \
                python3-venv \
                git \
                curl \
                build-essential \
                libssl-dev \
                libffi-dev \
                python3-dev
            ;;
        fedora)
            sudo dnf update -y
            sudo dnf install -y \
                python39 \
                python3-pip \
                python3-devel \
                git \
                curl \
                gcc \
                openssl-devel \
                libffi-devel
            ;;
        *)
            echo "Unsupported Linux distribution"
            exit 1
            ;;
    esac
    
    print_success "Base dependencies installed"
}

create_virtual_environment() {
    print_step "Creating virtual environment..."
    
    # Create SEED directory structure
    mkdir -p ~/.seed/{env,config,data,cache,logs,agents}
    
    # Create virtual environment
    python3 -m venv ~/.seed/env
    
    # Activate virtual environment
    source ~/.seed/env/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment created"
}

install_seed() {
    print_step "Installing SEED AI Framework..."
    
    # Install framework from PyPI
    pip install seed-ai-framework
    
    # Create default configuration if needed
    if [ ! -f ~/.seed/config/config.yaml ]; then
        seed init
    fi
    
    print_success "SEED AI Framework installed"
}

create_launcher() {
    print_step "Creating launcher..."
    
    # Create launcher script
    cat > ~/.local/bin/seed << 'EOL'
#!/bin/bash
source ~/.seed/env/bin/activate
seed "$@"
EOL
    
    # Make launcher executable
    chmod +x ~/.local/bin/seed
    
    # Add to PATH if needed
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
    fi
    
    print_success "Launcher created"
}

main() {
    echo -e "${BOLD}SEED AI Framework Installer${NC}"
    echo "This will install SEED and all required dependencies."
    echo
    
    # Check platform and setup accordingly
    check_platform
    
    case $OS in
        macos)
            setup_macos
            ;;
        linux)
            setup_linux
            ;;
    esac
    
    create_virtual_environment
    install_seed
    create_launcher
    
    echo
    echo -e "${GREEN}${BOLD}Installation Complete!${NC}"
    echo "To get started, run: seed dashboard"
    echo
    echo "Note: You may need to restart your terminal or run:"
    echo "  source ~/.bashrc  # for bash"
    echo "  source ~/.zshrc   # for zsh"
}

# Run installer
main