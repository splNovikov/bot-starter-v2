# Telegram Bot Starter v2

A modern Telegram bot built with **aiogram v3.x**, featuring Router-based architecture, comprehensive logging, and following best practices for maintainability and scalability.

## ✨ Features

- 🚀 **Modern aiogram v3.x** with Router system
- 🔧 **Environment-based configuration** with python-dotenv
- 📝 **Structured logging** with loguru (console + file)
- 🛡️ **Comprehensive error handling** and graceful shutdown
- 🏗️ **Clean architecture** with separation of concerns
- 🔄 **Middleware support** for cross-cutting concerns
- ⚡ **Async/await patterns** for optimal performance
- 🐳 **Production-ready** with proper logging and monitoring

## 📁 Project Structure

```
bot-starter-v2/
├── main.py                    # Main application entry point
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── handlers/                 # Message and callback handlers
│   ├── __init__.py
│   └── user_handlers.py      # User interaction handlers
├── middlewares/              # Custom middleware
│   ├── __init__.py
│   └── logging_middleware.py # Request/response logging
├── utils/                    # Utility modules
│   ├── __init__.py
│   └── logger.py            # Logging configuration
└── logs/                    # Log files (auto-created)
    └── bot_errors.log       # Error logs
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### 2. Installation

```bash
# Clone or create the project
cd bot-starter-v2

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Configuration

Edit `.env` file and add your bot token:

```env
BOT_TOKEN=your_bot_token_from_botfather
LOG_LEVEL=INFO
```

### 4. Run the Bot

```bash
python main.py
```

You should see output like:
```
2024-01-20 12:00:00 | INFO     | main:start:123 | Starting Telegram bot application...
2024-01-20 12:00:01 | INFO     | main:_bot_context:89 | Bot initialized: @YourBot (Your Bot Name)
2024-01-20 12:00:01 | INFO     | main:start:145 | Starting polling...
```

## 🤖 Bot Commands

- `/start` - Get a greeting message
- `/help` - Show available commands
- **Any text message** - Bot will respond with "Hello, {username}!"

## 🏗️ Architecture

### Router System (aiogram v3.x)

The bot uses aiogram's Router system for scalable message handling:

```python
# handlers/user_handlers.py
user_router = Router(name="user_handlers")

@user_router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    # Handler logic
```

### Configuration Management

Environment-based configuration with validation:

```python
# config.py
@dataclass
class BotConfig:
    token: str
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "BotConfig":
        # Load and validate environment variables
```

### Structured Logging

Comprehensive logging with loguru:

- **Console output**: Colored, structured logs
- **File logging**: Error logs saved to `logs/bot_errors.log`
- **Automatic rotation**: 10MB rotation with 1-month retention

### Middleware Support

Custom middleware for cross-cutting concerns:

```python
# middlewares/logging_middleware.py
class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Log request/response, handle errors
```

## 🛠️ Development

### Adding New Handlers

1. Create handler functions in `handlers/user_handlers.py`:

```python
@user_router.message(Command("new_command"))
async def handle_new_command(message: Message) -> None:
    await message.answer("New command response!")
```

2. Handlers are automatically registered via the router system.

### Adding Middleware

1. Create new middleware in `middlewares/`:

```python
class CustomMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Middleware logic
        return await handler(event, data)
```

2. Register in `main.py`:

```python
dp.message.middleware(CustomMiddleware())
```

### Environment Variables

Add new configuration options in `config.py`:

```python
@dataclass
class BotConfig:
    token: str
    log_level: str = "INFO"
    new_setting: str = "default_value"  # Add new settings
```

## 🐳 Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Process Management

Use process managers like `systemd`, `supervisor`, or `pm2` for production:

```ini
# systemd service example
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📊 Monitoring

- **Logs**: Check `logs/bot_errors.log` for errors
- **Console output**: Real-time logging with colored output
- **Health checks**: Bot automatically handles connection issues

## 🔒 Security Best Practices

- ✅ Environment variables for sensitive data
- ✅ Input validation and error handling
- ✅ Structured logging (no sensitive data in logs)
- ✅ Graceful shutdown handling
- ✅ Rate limiting ready (via aiogram built-ins)

## 📈 Scaling

The Router-based architecture supports easy scaling:

- **Horizontal**: Multiple bot instances with shared storage
- **Vertical**: Async/await patterns for high concurrency
- **Modular**: Easy to split into microservices

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper error handling and logging
3. Include type hints and docstrings
4. Test your changes thoroughly

## 📄 License

This project is open source and available under the MIT License. 