#!/bin/bash

# SEED Diagnostic Tool
# Helps troubleshoot installation and runtime issues

# Style definitions
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m"

# Logging utilities
log_header() { echo -e "\n${BOLD}$1${NC}"; }
log_check() { echo -e "${BLUE}${BOLD}[*]${NC} $1"; }
log_ok() { echo -e "${GREEN}${BOLD}[✓]${NC} $1"; }
log_warn() { echo -e "${YELLOW}${BOLD}[!]${NC} $1"; }
log_error() { echo -e "${RED}${BOLD}[x]${NC} $1"; }

check_path() {
    log_header "PATH Configuration"
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
        log_ok "~/.local/bin is in PATH"
    else
        log_error "~/.local/bin not in PATH"
        echo "Add the following to your shell configuration:"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
    
    # Check shell configuration files
    local shell_configs=(
        "$HOME/.bashrc"
        "$HOME/.zshrc"
        "$HOME/.bash_profile"
    )
    
    for config in "${shell_configs[@]}"; do
        if [ -f "$config" ]; then
            if grep -q ".local/bin" "$config"; then
                log_ok "PATH configured in $(basename "$config")"
            else
                log_warn "PATH not configured in $(basename "$config")"
            fi
        fi
    done
    
    # Check launcher script
    if [ -x "$HOME/.local/bin/seed" ]; then
        log_ok "Launcher script exists and is executable"
    else
        log_error "Launcher script missing or not executable"
    fi
}

# Permission check
check_permissions() {
    log_header "Permissions Check"
    
    local seed_home="$HOME/.seed"
    local check_paths=(
        "$seed_home"
        "$seed_home/config"
        "$seed_home/data"
        "$seed_home/cache"
        "$seed_home/logs"
        "$seed_home/agents"
        "$seed_home/env"
        "$HOME/.local/bin"
    )
    
    for path in "${check_paths[@]}"; do
        if [ -e "$path" ]; then
            local perms=$(stat -f "%A %u:%g" "$path" 2>/dev/null || stat -c "%a %u:%g" "$path")
            local owner=$(stat -f "%Su:%Sg" "$path" 2>/dev/null || stat -c "%U:%G" "$path")
            echo "$path: $perms ($owner)"
            
            # Check for common permission issues
            if [ ! -r "$path" ]; then
                log_error "Not readable: $path"
            fi
            if [ ! -w "$path" ]; then
                log_error "Not writable: $path"
            fi
            if [ -d "$path" ] && [ ! -x "$path" ]; then
                log_error "Not executable (required for directories): $path"
            fi
        else
            log_error "Path does not exist: $path"
        fi
    done
}

# Dependency check
check_dependencies() {
    log_header "Required Dependencies"
    
    local deps=(
        "python3:Python 3 runtime"
        "pip:Python package manager"
        "git:Version control"
        "curl:Network requests"
    )
    
    for dep in "${deps[@]}"; do
        IFS=':' read -r cmd desc <<< "$dep"
        if command -v "$cmd" >/dev/null 2>&1; then
            local version
            case "$cmd" in
                python3)
                    version=$(python3 --version 2>&1)
                    ;;
                pip)
                    version=$(pip --version 2>&1)
                    ;;
                git)
                    version=$(git --version 2>&1)
                    ;;
                curl)
                    version=$(curl --version 2>&1 | head -n 1)
                    ;;
            esac
            log_ok "$desc: $version"
        else
            log_error "$desc not found"
            case "$cmd" in
                python3)
                    echo "Install Python 3 from https://python.org"
                    ;;
                pip)
                    echo "Usually installed with Python. Try: python3 -m ensurepip"
                    ;;
                git)
                    echo "Install Git from https://git-scm.com"
                    ;;
                curl)
                    echo "Install curl through your system package manager"
                    ;;
            esac
        fi
    done
}

# Generate diagnostic report
generate_report() {
    local report_file="$HOME/.seed/logs/diagnostic_$(date +%Y%m%d_%H%M%S).log"
    
    {   # Redirect all output to report file
        echo "SEED Diagnostic Report"
        echo "Generated: $(date)"
        echo "----------------------------------------"
        
        check_system
        check_python
        check_directories
        check_config
        check_network
        check_path
        check_permissions
        check_dependencies
        
    } > "$report_file"
    
    echo -e "\n${GREEN}Diagnostic report generated:${NC} $report_file"
    echo "Share this file when reporting installation issues."
}

# Main execution
main() {
    echo -e "${BOLD}SEED Diagnostic Tool${NC}\n"
    echo "Running system checks..."
    
    # Run all checks
    check_system
    check_python
    check_directories
    check_config
    check_network
    check_path
    check_permissions
    check_dependencies
    
    # Generate report
    generate_report
}

# Run diagnostics
main