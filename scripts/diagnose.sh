#!/bin/bash

# SEED Diagnostic Tool
# Comprehensive system and installation verification

# Enable strict error handling
set -euo pipefail
IFS=$'\n\t'

# Style definitions
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m"

# Logging utilities
log_header() { echo -e "\n${BOLD}$1${NC}"; }
log_check() { echo -e "${BLUE}${BOLD}[*]${NC} $1"; }
log_ok() { echo -e "${GREEN}${BOLD}[✓]${NC} $1"; }
log_warn() { echo -e "${YELLOW}${BOLD}[!]${NC} $1"; }
log_error() { echo -e "${RED}${BOLD}[x]${NC} $1"; }

# System information check
check_system() {
    log_header "System Information"
    
    # OS Information
    log_check "Operating System:"
    case "$(uname)" in
        Darwin)
            sw_vers
            ;;
        Linux)
            if [ -f /etc/os-release ]; then
                cat /etc/os-release | grep -E '^(NAME|VERSION)='
            else
                uname -a
            fi
            ;;
    esac
    
    # Hardware Resources
    log_check "Hardware Resources:"
    echo "CPU Cores: $(sysctl -n hw.ncpu 2>/dev/null || nproc)"
    echo "Memory: $(vm_stat | grep 'Pages free:' | awk '{print $3}' 2>/dev/null || free -h)"
    echo "Disk Space: $(df -h ~ | awk 'NR==2')"
}

# Python environment check
check_python() {
    log_header "Python Environment"
    
    # Check Python versions
    if command -v python3 >/dev/null 2>&1; then
        log_ok "Python 3 installed: $(python3 --version)"
    else
        log_error "Python 3 not found"
    fi
    
    # Check virtual environment
    if [ -f "$HOME/.seed/env/bin/python" ]; then
        log_ok "Virtual environment exists"
        echo "Version: $($HOME/.seed/env/bin/python --version)"
        echo "Packages installed:"
        $HOME/.seed/env/bin/pip list
    else
        log_error "Virtual environment not found"
    fi
}

# Directory structure check
check_directories() {
    log_header "SEED Directory Structure"
    
    local dirs=("config" "data" "cache" "logs" "agents" "env")
    local seed_home="$HOME/.seed"
    
    for dir in "${dirs[@]}"; do
        if [ -d "$seed_home/$dir" ]; then
            if [ -w "$seed_home/$dir" ]; then
                log_ok "$dir: exists and writable"
            else
                log_warn "$dir: exists but not writable"
            fi
        else
            log_error "$dir: missing"
        fi
    done
}

# Configuration check
check_config() {
    log_header "Configuration"
    
    local config_file="$HOME/.seed/config/config.yaml"
    if [ -f "$config_file" ]; then
        log_ok "Config file exists"
        if [ -r "$config_file" ]; then
            echo "Configuration contents:"
            cat "$config_file"
        else
            log_error "Config file not readable"
        fi
    else
        log_error "Config file missing"
    fi
}

# Network connectivity check
check_network() {
    log_header "Network Connectivity"
    
    local endpoints=(
        "raw.githubusercontent.com"
        "api.github.com"
        "pypi.org"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -s --connect-timeout 5 "https://$endpoint" >/dev/null; then
            log_ok "$endpoint: accessible"
        else
            log_error "$endpoint: not accessible"
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
    
    # Generate report
    generate_report
}

# Run diagnostics
main