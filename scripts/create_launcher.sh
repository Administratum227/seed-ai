#!/bin/bash

# SEED Launcher Creation Script
create_launcher() {
    log_info "Creating launcher script"
    
    # Create local bin directory
    mkdir -p "$HOME/.local/bin"
    
    # Create the launcher script
    cat > "$HOME/.local/bin/seed" << 'EOL'
#!/bin/bash
# SEED AI Framework Launcher

# Find the SEED environment
SEED_ENV="$HOME/.seed/env"
if [ ! -f "$SEED_ENV/bin/activate" ]; then
    echo "Error: SEED environment not found at $SEED_ENV"
    echo "Try reinstalling with: curl -sSL https://raw.githubusercontent.com/Administratum227/seed-ai/main/scripts/install.sh | bash"
    exit 1
fi

# Activate virtual environment
source "$SEED_ENV/bin/activate"

# Execute SEED command
exec seed "$@"
EOL
    
    # Make launcher executable
    chmod +x "$HOME/.local/bin/seed"
    
    # Add to PATH if needed
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        
        # Also add to zsh config if it exists
        if [ -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        fi
        
        # Make PATH changes available immediately
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    log_success "Launcher script created"
}