#!/bin/bash

# SEED AI Framework Installer
# Zero-dependency installation script for macOS and Linux

# Enable strict error handling
set -euo pipefail
IFS=$'\n\t'

# Style definitions
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"  # No Color

# Logging utilities
log_info() { echo -e "${BLUE}${BOLD}==>${NC} $1"; }
log_success() { echo -e "${GREEN}${BOLD}✓${NC} $1"; }
log_error() { echo -e "${RED}${BOLD}Error:${NC} $1" >&2; }

# Verify git installation
if ! command -v git &> /dev/null; then
    log_error "Git is required but not installed. Please install git first."
    exit 1
fi

# Create directories
log_info "Setting up SEED environment..."
mkdir -p "$HOME/.seed/"{config,data,cache,logs,agents}

# Setup Python virtual environment
log_info "Creating virtual environment..."
python3 -m venv "$HOME/.seed/env"
source "$HOME/.seed/env/bin/activate"

# Install SEED directly from GitHub
log_info "Installing SEED framework..."
pip install --upgrade pip
pip install git+https://github.com/Administratum227/seed-ai.git@main || {
    log_error "Failed to install from GitHub"
    exit 1
}

# Create launcher
log_info "Creating launcher..."
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/seed" << 'EOL'
#!/bin/bash
source "$HOME/.seed/env/bin/activate"
exec seed "$@"
EOL
chmod +x "$HOME/.local/bin/seed"

# Update PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    [ -f "$HOME/.zshrc" ] && echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
fi

log_success "Installation complete!"
echo -e "\nTo get started:"
echo -e "1. Close and reopen your terminal, or run:"
echo -e "   source ~/.bashrc  # for bash"
echo -e "   source ~/.zshrc   # for zsh"
echo -e "\n2. Then launch the dashboard:"
echo -e "   seed"