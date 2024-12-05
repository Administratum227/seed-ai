# SEED AI Framework

Scalable Ecosystem for Evolving Digital Agents - A framework for creating, managing, and orchestrating AI agents.

## Quick Installation

Install SEED on any system with a single command:

```bash
# Option 1: Direct installation
curl -sSL https://raw.githubusercontent.com/Administratum227/seed-ai/main/scripts/install.sh | bash

# Option 2: Download and verify first
wget https://raw.githubusercontent.com/Administratum227/seed-ai/main/scripts/install.sh
chmod +x install.sh
./install.sh
```

## Features

- 🤖 Zero-configuration agent creation and management
- 🔄 Built-in task orchestration and scheduling
- 🌐 Integrated API support (Brave Search, GitHub)
- 📊 Real-time monitoring dashboard
- 🛠️ Automated dependency management
- 🔒 Secure environment isolation

## System Requirements

- macOS 10.15+ or Linux (Ubuntu/Debian/Fedora)
- Internet connection for initial setup
- Admin privileges (only for system dependencies)

## Directory Structure

```
~/.seed/
├── config/         # Configuration files
├── data/           # Agent data storage
├── cache/          # API response cache
├── logs/           # System logs
└── agents/         # Agent state files
```

## Troubleshooting

If you encounter issues during installation:

```bash
# Run diagnostic tool
curl -sSL https://raw.githubusercontent.com/Administratum227/seed-ai/main/scripts/diagnose.sh | bash
```

The diagnostic tool will:
- Verify system requirements
- Check dependencies
- Validate configurations
- Generate detailed report

## Quick Start

After installation:

1. Launch the dashboard:
   ```bash
   seed dashboard
   ```

2. Create an agent:
   ```bash
   seed create my-agent --capabilities "web_search,task_planning"
   ```

3. Monitor status:
   ```bash
   seed status my-agent
   ```

## Documentation

- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Configuration Guide](docs/configuration.md)
- [Development Guide](docs/development.md)

## Development

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

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
