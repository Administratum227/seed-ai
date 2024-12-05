# SEED AI Framework

A framework for creating, managing, and orchestrating AI agents powered by Claude.

## Zero-Dependency Installation

Install SEED with a single command on any fresh system:

```bash
curl -sSL https://raw.githubusercontent.com/Administratum227/seed-ai/main/scripts/install.sh | bash
```

This will:
- Install all required system dependencies
- Set up Python environment
- Configure SEED framework
- Create launch scripts

## Features

- 🤖 Easy AI agent creation and management
- 🔄 Built-in task orchestration
- 🌐 API integrations (Brave Search, GitHub)
- 📊 Real-time monitoring dashboard
- 🛠️ Zero-configuration setup
- 🔒 Secure virtual environment isolation

## Requirements

- macOS 10.15+ or Linux (Ubuntu/Debian/Fedora)
- Internet connection
- Admin privileges (for initial setup only)

## Troubleshooting

If you encounter installation issues, run our diagnostic tool:

```bash
curl -sSL https://raw.githubusercontent.com/Administratum227/seed-ai/main/scripts/diagnose.sh | bash
```

The tool will:
- Check system requirements
- Verify dependencies
- Validate configuration
- Generate a diagnostic report

## Getting Started

After installation:

1. Launch the dashboard:
   ```bash
   seed dashboard
   ```

2. Create your first agent:
   ```bash
   seed create my-agent --capabilities "web_search,task_planning"
   ```

3. Monitor agent status:
   ```bash
   seed status my-agent
   ```

## Documentation

- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
