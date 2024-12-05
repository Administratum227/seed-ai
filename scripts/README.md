# SEED Installation Scripts

This directory contains scripts for installing, configuring, and maintaining the SEED AI Framework.

## Scripts

### install.sh
Main installation script that handles:
- System dependency installation
- Python environment setup
- Framework installation
- Path configuration

### diagnose.sh
Diagnostic tool that checks:
- System requirements
- Dependencies
- Configuration
- Common issues

## Usage

### Installation
```bash
curl -sSL https://raw.githubusercontent.com/Administratum227/seed-ai/main/scripts/install.sh | bash
```

### Diagnostics
```bash
curl -sSL https://raw.githubusercontent.com/Administratum227/seed-ai/main/scripts/diagnose.sh | bash
```

## Security

All scripts:
- Run with minimal required privileges
- Use secure download methods
- Validate checksums where applicable
- Implement error handling
