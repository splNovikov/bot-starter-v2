# 🤖 Modern Telegram Bot Starter

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.13+-green.svg)](https://aiogram.dev)
[![Localization](https://img.shields.io/badge/Localization-✅-brightgreen.svg)](locales/)
[![Architecture](https://img.shields.io/badge/Architecture-Clean-brightgreen.svg)](#architecture)

A production-ready Telegram bot starter template built with **aiogram v3.x**, featuring clean architecture, comprehensive localization, and type-safe handler system.

## ✨ Key Features

- **🏗️ Clean Architecture** - SOLID principles with layered design
- **🌍 Multi-Language Support** - English, Spanish, Russian (easily extensible)
- **🔧 Type-Safe Handlers** - Registry-based system with rich metadata
- **⚡ Auto-Registration** - Decorators handle all the boilerplate
- **📊 Built-in Analytics** - Performance monitoring and statistics

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/bot-starter-v2.git
cd bot-starter-v2

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your BOT_TOKEN
```

### Run the Bot

```bash
python main.py
```

**Try these commands:**
- `/start` - Welcome message in your language
- `/help` - Auto-generated help (localized)
- `/language` - Change language interactively
- `/greet` (or `/hi`, `/hello`) - Friendly greeting

## 🏗️ Architecture

```
bot-starter-v2/
├── 🔧 core/                    # Framework Layer (Reusable)
│   ├── handlers/               # Registry system & decorators
│   ├── middleware/             # Infrastructure components
│   └── utils/                  # Core utilities
├── 🎯 business/                # Business Layer (Application-specific)
│   ├── handlers/               # Message handling logic
│   └── services/               # Domain services
├── 🌍 locales/                 # Translation files
│   ├── en.json, es.json, ru.json
└── docs/                       # Documentation
```

**Core Principles:**
- **Clean Dependency Flow**: Business → Core (never reverse)
- **Single Responsibility**: Each class has one purpose
- **Localization-First**: All user text uses translation system
- **Type Safety**: Protocol-based interfaces with runtime validation

## 🌍 Localization

The bot automatically detects user language and provides content in:
- **🇺🇸 English** (default)
- **🇪🇸 Spanish**
- **🇷🇺 Russian**

**Language Detection Chain:**
1. User preference (via `/language` command)
2. Telegram user locale
3. Default language fallback

## 📚 Documentation

### 🎯 Business Layer Development
- **[Business Overview](business/docs/README.md)** - Application architecture and patterns
- **[Handler Development](business/docs/handlers.md)** - Creating commands and message processors
- **[Service Development](business/docs/services.md)** - Building business logic services
- **[Implementation Examples](business/docs/examples.md)** - Real-world patterns and examples

### 🔧 Core Framework
- **[Core Overview](core/docs/README.md)** - Framework architecture and principles
- **[Handler System](core/docs/handlers.md)** - Registry, decorators, and type system
- **[Middleware](core/docs/middleware.md)** - Request processing pipeline
- **[Utilities](core/docs/utils.md)** - Logging and helper functions

### 📖 General Documentation
- **[Localization Guide](docs/localization.md)** - Complete multi-language support guide
- **[Contributing Guide](docs/contributing.md)** - Development guidelines and standards

## 🔧 Code Quality & Formatting

This project uses **autoflake** and **isort** for import management and code quality. Black is temporarily disabled due to compatibility issues (see [BLACK_COMPATIBILITY.md](BLACK_COMPATIBILITY.md)).

### 🚀 Quick Setup

```bash
# Automated setup (recommended)
python setup_dev.py

# Manual setup
pip install -r requirements.txt
pre-commit install
```

### Quick Format
```bash
# Using the formatting script (recommended)
python format_code.py

# Using Makefile (if you have make installed)
make format

# Or run formatters individually
autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive .
isort .
```

### Check Formatting (without changes)
```bash
# Using Makefile
make check-format

# Or run individually
autoflake --remove-all-unused-imports --remove-unused-variables --check .
isort --check-only --diff .
```

### Remove Unused Imports Only
```bash
# Using Makefile
make clean-imports

# Or run directly
autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive .
```

### IDE Integration
- **VS Code**: Install "isort" and "autoflake" extensions
- **PyCharm**: Enable isort and autoflake in Settings → Tools → External Tools
- **Vim/Neovim**: Use `isort` and `autoflake` with your preferred plugin

### Pre-commit Hooks
The project includes pre-commit hooks that automatically:
- Remove unused imports and variables
- Sort imports
- Fix trailing whitespace and file endings

These hooks run automatically on every commit to ensure code quality.

**Note**: Black formatting is temporarily disabled in pre-commit hooks due to compatibility issues. See [BLACK_COMPATIBILITY.md](BLACK_COMPATIBILITY.md) for resolution steps.

## 🔧 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_TOKEN` | - | **Required** - Your Telegram bot token |
| `API_BASE_URL` | `https://api.example.com` | Base URL for questionnaire API |
| `API_TIMEOUT` | `30` | API request timeout in seconds |
| `DEFAULT_LANGUAGE` | `en` | Default language for new users |
| `SUPPORTED_LANGUAGES` | `en,es,ru` | Comma-separated language codes |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING) |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for development guidelines, architecture patterns, and submission process.

**Quick Start:**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow the [architecture patterns](business/docs/README.md)
4. Add comprehensive documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[aiogram](https://aiogram.dev)** - Async Telegram Bot framework
- **[loguru](https://loguru.readthedocs.io)** - Elegant logging
- **Community** - Thanks to all contributors!

---

**Ready to build something amazing?** 🚀

Start with the [Handler Development Guide](business/docs/handlers.md) and explore the [examples](business/docs/examples.md) to see what's possible!
