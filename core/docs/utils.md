# 🔧 Core Utilities

The core utilities provide essential infrastructure components used throughout the framework and business layer.

## 📋 Overview

Core utilities include:
- **Logging System**: Professional logging with structured output
- **Configuration Management**: Environment-based configuration
- **Common Utilities**: Shared helper functions and classes

## 📝 Logging System

The logging system provides structured, professional logging using the `loguru` library.

### Features

- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Structured Output**: Consistent formatting for easy parsing
- **File Rotation**: Automatic log file rotation and cleanup
- **Console and File Output**: Simultaneous logging to console and files
- **Performance Tracking**: Built-in timing and performance metrics
- **Error Context**: Automatic exception tracking with stack traces

### Setup and Configuration

```python
from core.utils.logger import setup_logger, get_logger

# Initialize logging system (called once at startup)
setup_logger()

# Get logger instance (use throughout application)
logger = get_logger()
```

### Logging Configuration

The logger is configured in `core/utils/logger.py`:

```python
def setup_logger():
    """Setup loguru logger with appropriate configuration."""
    logger.remove()  # Remove default handler
    
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File logging with rotation
    logger.add(
        "logs/bot.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
```

### Usage Examples

```python
from core.utils.logger import get_logger

logger = get_logger()

# Different log levels
logger.debug("Detailed debugging information")
logger.info("General information about program execution")
logger.warning("Warning about potential issues")
logger.error("Error occurred, but application continues")
logger.critical("Critical error, application may stop")

# Structured logging with context
logger.info(
    f"User {user_id} executed command {command} in chat {chat_id}",
    extra={
        "user_id": user_id,
        "command": command, 
        "chat_id": chat_id,
        "response_time": 0.25
    }
)

# Exception logging with traceback
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
```

### Log Output Examples

**Console Output:**
```
2024-01-01 12:00:00.123 | INFO     | handlers.user_handlers:cmd_start:45 | User 123456 started bot
2024-01-01 12:00:01.456 | ERROR    | services.weather:get_weather:89 | Weather API timeout
```

**File Output:**
```
2024-01-01 12:00:00.123 | INFO     | handlers.user_handlers:cmd_start:45 | User 123456 started bot
2024-01-01 12:00:01.456 | ERROR    | services.weather:get_weather:89 | Weather API timeout
Traceback (most recent call last):
  File "weather.py", line 87, in get_weather
    response = await session.get(url, timeout=5)
  ...
```

### Performance Logging

```python
import time
from core.utils.logger import get_logger

logger = get_logger()

# Method 1: Manual timing
start_time = time.time()
result = await some_operation()
duration = time.time() - start_time
logger.info(f"Operation completed in {duration:.2f}s")

# Method 2: Context manager (if implemented)
with logger.timer("Database query"):
    result = await db.query(sql)
# Automatically logs: "Database query completed in 0.15s"
```

### Logger Instance Management

The system uses a singleton pattern for logger instances:

```python
def get_logger(name: str = None) -> loguru.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Optional logger name for categorization
        
    Returns:
        Configured logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger
```

### Custom Logger Categories

```python
# Create categorized loggers
db_logger = get_logger("database")
api_logger = get_logger("external_api")
auth_logger = get_logger("authentication")

# Usage
db_logger.info("Database connection established")
api_logger.warning("API rate limit approaching")
auth_logger.error("Invalid authentication attempt")
```

## ⚙️ Configuration Management

While not currently implemented, the utilities package can be extended with configuration management:

### Example Configuration Utility

```python
# core/utils/config.py
import os
from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class LoggingConfig:
    level: str = "INFO"
    file_rotation: str = "10 MB"
    retention: str = "7 days"
    console_format: str = "{time} | {level} | {message}"
    file_format: str = "{time} | {level} | {name}:{function}:{line} | {message}"

@dataclass
class CoreConfig:
    logging: LoggingConfig = LoggingConfig()
    debug: bool = False
    environment: str = "production"
    
    @classmethod
    def from_env(cls) -> 'CoreConfig':
        """Load configuration from environment variables."""
        return cls(
            logging=LoggingConfig(
                level=os.getenv("LOG_LEVEL", "INFO"),
                file_rotation=os.getenv("LOG_ROTATION", "10 MB"),
                retention=os.getenv("LOG_RETENTION", "7 days")
            ),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            environment=os.getenv("ENVIRONMENT", "production")
        )

# Usage
config = CoreConfig.from_env()
```

## 🛠️ Common Utilities

### Example Helper Functions

```python
# core/utils/helpers.py
from typing import Optional, Dict, Any
import asyncio
import functools

def retry_async(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for retrying async functions."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get nested dictionary values."""
    try:
        keys = key.split('.')
        value = data
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default

async def timeout_after(seconds: float):
    """Context manager for operation timeout."""
    return asyncio.wait_for(asyncio.sleep(0), timeout=seconds)

# Usage examples
@retry_async(max_attempts=3, delay=1.0)
async def flaky_api_call():
    # This will retry up to 3 times with exponential backoff
    pass

user_name = safe_get(user_data, 'profile.personal.name', 'Anonymous')
```

### Validation Utilities

```python
# core/utils/validation.py
import re
from typing import Optional

def validate_command(command: str) -> bool:
    """Validate bot command format."""
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', command))

def validate_user_id(user_id: Any) -> bool:
    """Validate Telegram user ID."""
    return isinstance(user_id, int) and user_id > 0

def sanitize_text(text: str, max_length: int = 4096) -> str:
    """Sanitize text for Telegram message sending."""
    if not text:
        return ""
    
    # Remove potentially problematic characters
    text = re.sub(r'[^\w\s\.,!?-]', '', text)
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text.strip()
```

## 🔧 Extending Core Utilities

### Adding New Utilities

1. **Create utility module** in `core/utils/`
2. **Import in `core/utils/__init__.py`**
3. **Add to `__all__` for clean exports**
4. **Document usage and examples**

Example structure:
```python
# core/utils/cache.py
class SimpleCache:
    """Simple in-memory cache for expensive operations."""
    # Implementation here

# core/utils/__init__.py
from .cache import SimpleCache
__all__.extend(['SimpleCache'])
```

### Integration with Business Layer

Core utilities are imported and used throughout the business layer:

```python
# In business layer
from core.utils.logger import get_logger
from core.utils.validation import validate_command, sanitize_text

logger = get_logger()

@command("example", description="Example command")
async def cmd_example(message: Message) -> None:
    # Use core utilities
    logger.info(f"Processing example command from user {message.from_user.id}")
    
    safe_text = sanitize_text(message.text)
    await message.answer(safe_text)
```

## 🎯 Best Practices

### Logging
- Use **appropriate log levels** (DEBUG for development, INFO for production)
- Include **relevant context** in log messages
- **Don't log sensitive information** (passwords, tokens, personal data)
- Use **structured logging** for easier parsing and analysis

### Error Handling
- **Always log exceptions** with proper context
- Use `exc_info=True` for **full stack traces**
- **Don't swallow exceptions** unless explicitly handled
- **Provide meaningful error messages** for debugging

### Performance
- **Log timing information** for expensive operations
- **Use async logging** to avoid blocking operations
- **Rotate log files** to prevent disk space issues
- **Monitor log file sizes** in production

### Configuration
- **Use environment variables** for configuration
- **Provide sensible defaults** for all settings
- **Validate configuration** at startup
- **Document all configuration options**

The core utilities provide the foundation for reliable, observable, and maintainable bot applications. 