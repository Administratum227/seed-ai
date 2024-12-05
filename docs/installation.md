# Installation Guide

## Quick Start

The fastest way to get started with SEED is using our bootstrap installer:

```bash
curl -sSL https://seed-ai.dev/install | bash
```

This will:
1. Check system requirements
2. Install necessary dependencies
3. Set up Python environment
4. Install SEED framework
5. Configure environment

## Manual Installation

If you prefer manual installation:

### macOS

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.9

# Install SEED
pip3 install seed-ai-framework
```

### Linux (Ubuntu/Debian)

```bash
# Install Python and dependencies
sudo apt-get update
sudo apt-get install python3.9 python3-pip python3-venv

# Install SEED
pip3 install seed-ai-framework
```

## Configuration

After installation, initialize SEED:

```bash
seed init
```

Configuration is stored in `~/.seed/config/config.yaml`.

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   # Fix permissions
   sudo chown -R $USER ~/.seed
   ```

2. **Path Issues**
   ```bash
   # Add to PATH
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Getting Help

For additional help:
- Run `seed doctor` for diagnostics
- Visit our [Discord community](https://discord.gg/seed-ai)
- Open an issue on [GitHub](https://github.com/seed-ai/framework/issues)