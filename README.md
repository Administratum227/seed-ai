# SEED AI Framework

## Zero-Dependency Installation

Choose your preferred installation method:

### Method 1: Direct Installation (Quick)
```bash
curl -sSL https://raw.githubusercontent.com/Administratum227/seed-ai/main/install.sh | bash
```

### Method 2: Secure Installation (Recommended)
```bash
# Download installer
curl -O https://raw.githubusercontent.com/Administratum227/seed-ai/main/install.sh

# Review the script (optional but recommended)
less install.sh

# Make executable and run
chmod +x install.sh
./install.sh
```

### Method 3: Git-based Installation (Most Reliable)
```bash
# Clone repository
git clone https://github.com/Administratum227/seed-ai.git

# Run installer
bash seed-ai/install.sh
```

## System Requirements

- macOS 10.15+ or Linux (Ubuntu/Debian/Fedora)
- Internet connection (for initial setup)
- Admin privileges (for system dependencies)

## Architecture Overview

```
┌─────────────────┐
│  SEED Framework │
├─────────────────┴──────────────┐
│ ┌──────────┐    ┌──────────┐   │
│ │  Agents  │<───│  Tasks   │   │
│ └──────────┘    └──────────┘   │
│ ┌──────────┐    ┌──────────┐   │
│ │   API    │<───│ Runtime  │   │
│ └──────────┘    └──────────┘   │
└────────────────────────────────┘
```

## Directory Structure

```
~/.seed/
├── config/          # Configuration files
├── data/            # Agent data storage
├── cache/           # API response cache
├── logs/            # System logs
└── agents/          # Agent state files
```

## Quick Start Guide

After installation:

1. Launch the dashboard:
```bash
seed dashboard
```

2. Create an agent:
```bash
seed create researcher --capabilities "web_search,analysis"
```

3. Monitor status:
```bash
seed status researcher
```

## Troubleshooting

If you encounter issues:

1. Run the diagnostic tool:
```bash
seed doctor
```

2. Check the logs:
```bash
cat ~/.seed/logs/seed.log
```

3. Verify installation:
```bash
seed verify
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Configuration](docs/configuration.md)
- [Development Guide](docs/development.md)

## Development Setup

```bash
# Clone repository
git clone https://github.com/Administratum227/seed-ai.git
cd seed-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
