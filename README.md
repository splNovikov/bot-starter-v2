# 🤖 Modern Telegram Bot Starter v2

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.12+-green.svg)](https://aiogram.dev)
[![Localization](https://img.shields.io/badge/Localization-✅-brightgreen.svg)](locales/)
[![Architecture](https://img.shields.io/badge/Architecture-Clean-brightgreen.svg)](#architecture)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-Ruff%20%7C%20isort%20%7C%20autoflake-brightgreen.svg)](#code-quality--formatting)

A production-ready Telegram bot starter template built with **aiogram v3.x**, featuring clean architecture, comprehensive localization, and type-safe handler system.

## ✨ Key Features

- **🏗️ Clean Architecture** - SOLID principles with layered design
- **🌍 Multi-Language Support** - English, Spanish, Russian (easily extensible)
- **🔧 Type-Safe Handlers** - Registry-based system with rich metadata
- **⚡ Auto-Registration** - Decorators handle all the boilerplate
- **📊 Built-in Analytics** - Performance monitoring and statistics
- **🎨 Modern Code Quality** - Ruff, isort, and autoflake for formatting
- **🐍 Python 3.13 Ready** - Optimized for the latest Python version

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** (recommended) or Python 3.11+
- **Git** for cloning the repository
- **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bot-starter-v2.git
cd bot-starter-v2

# Setup development environment (automated)
make setup

# Create environment file
cp .env.example .env
# Edit .env with your BOT_TOKEN
```

### Run the Bot

```bash
# Start the bot
make run
```

**Try these commands:**
- `/start` - Welcome message in your language
- `/help` - Auto-generated help (localized)
- `/language` - Change language interactively
- `/greet` (or `/hi`, `/hello`) - Friendly greeting

## 🛠️ Development Commands

The project includes a comprehensive Makefile for common development tasks:

```bash
# Setup and installation
make setup              # Complete development environment setup
make install-dev        # Install development dependencies

# Code formatting and quality
make format             # Format all Python files
make check-format       # Check formatting without changes
make clean-imports      # Remove unused imports only

# Running and maintenance
make run                # Run the bot
make clean              # Clean up Python cache files
make help               # Show all available commands
```

## 🏗️ Architecture

This project follows **Clean Architecture** and **SOLID** principles with clear layer separation:
- **Core Layer** - Framework components, protocols, and utilities
- **Application Layer** - Business logic and bot handlers  
- **Infrastructure Layer** - External systems and implementations

📖 **[View Detailed Architecture Documentation →](docs/ARCHITECTURE.md)**

The architecture includes dependency injection, sequence management, and comprehensive testing with automated validation.

## 🌍 Localization

The bot automatically detects user language and provides content in:
- **🇺🇸 English** (default)
- **🇪🇸 Spanish**
- **🇷🇺 Russian**

**Language Detection Chain:**
1. User preference (via `/language` command)
2. Telegram user locale
3. Default language fallback

### Adding New Languages

1. Create a new JSON file in `locales/` (e.g., `fr.json`)
2. Translate all keys from `en.json`

## 🔧 Code Quality & Formatting

This project uses modern Python code quality tools:

- **Ruff** - Fast Python linter and formatter
- **isort** - Import sorting and organization
- **autoflake** - Remove unused imports and variables

### Automated Setup

The development environment is automatically configured with:

```bash
make setup
```

This command:
- Creates a virtual environment
- Installs all dependencies
- Verifies tool installation
- Provides helpful error messages if issues occur

### Manual Formatting Workflow

```bash
# Format all code (recommended)
make format

# Check formatting without changes
make check-format

# Remove unused imports only
make clean-imports
```

### IDE Integration

**VS Code:**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

**PyCharm:**
- Enable Ruff in Settings → Tools → External Tools
- Configure isort and autoflake as external tools

## 🔧 Configuration

Create a `.env` file in the project root:

```bash
# Required
BOT_TOKEN=your_telegram_bot_token_here

# Optional (with defaults)
FALLBACK_LANGUAGE=ru
LOG_LEVEL=INFO
API_BASE_URL=https://api.example.com
API_TIMEOUT=30
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_TOKEN` | - | **Required** - Your Telegram bot token |
| `FALLBACK_LANGUAGE` | `ru` | Fallback language when user preferences can't be determined |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING) |
| `API_BASE_URL` | `https://api.example.com` | Base URL for external APIs |
| `API_TIMEOUT` | `30` | API request timeout in seconds |

## 🚀 Deployment

### Local Development

```bash
# Setup environment
make setup

# Create .env file
echo "BOT_TOKEN=your_token_here" > .env

# Run the bot
make run
```

### Production Deployment

1. **Environment Setup:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install -r requirements.txt
   ```

2. **Configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Run:**
   ```bash
   python3 main.py
   ```

### Docker Deployment

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## 🐛 Troubleshooting

### Common Issues

**1. "pip: command not found"**
```bash
# Use python3 -m pip instead
python3 -m pip install -r requirements.txt
```

**2. "externally-managed-environment"**
```bash
# Use virtual environment
make setup
```

**3. Import errors in virtual environment**
```bash
# Recreate virtual environment
rm -rf venv
make setup
```

**4. Formatting tools not found**
```bash
# Reinstall development dependencies
make install-dev
```

### Getting Help

- Check the [Issues](https://github.com/yourusername/bot-starter-v2/issues) page
- Review the [Architecture Documentation](#architecture)
- Ensure your Python version is 3.11+ (3.13+ recommended)

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/bot-starter-v2.git
cd bot-starter-v2

# Setup development environment
make setup

# Create feature branch
git checkout -b feature/amazing-feature
```

### Code Standards

- Follow the existing architecture patterns
- Use type hints throughout
- Add comprehensive docstrings
- Ensure all code is properly formatted
- Write tests for new features

### Submission Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and format code: `make format`
4. Test your changes: `make check-format`
5. Commit: `git commit -m "Add amazing feature"`
6. Push: `git push origin feature/amazing-feature`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Detailed Clean Architecture documentation
- **[PlantUML Diagram](docs/architecture.puml)** - Visual architecture overview

## 🙏 Acknowledgments

- **[aiogram](https://aiogram.dev)** - Async Telegram Bot framework
- **[loguru](https://loguru.readthedocs.io)** - Elegant logging
- **[Ruff](https://github.com/astral-sh/ruff)** - Fast Python linter
- **Community** - Thanks to all contributors!

---

**Ready to build something amazing?** 🚀

Start with the [Quick Start](#-quick-start) guide and explore the [Architecture Guide](docs/ARCHITECTURE.md) to understand the patterns!
