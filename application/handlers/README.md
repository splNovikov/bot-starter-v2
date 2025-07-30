# Handlers Organization

This directory contains all bot handlers organized by feature and functionality.

## Structure

```
business/handlers/
├── __init__.py              # Main package exports
├── router.py                # Main router aggregator
├── registry_init.py         # Registry initialization
├── basic/                   # Fundamental commands everyone needs
│   ├── __init__.py
│   └── start_handler.py     # /start command
├── settings/                # Configuration and preferences
│   ├── __init__.py
│   └── locale_handler.py    # /locale command
├── sequences/               # Multi-step workflow handlers
│   └── __init__.py          # (Future: order_handler.py, support_handler.py)
└── admin/                   # Admin-only commands
    └── __init__.py          # (Future: admin_handlers.py)
```

## Handler Types

### Basic Handlers (`basic/`)
- **Purpose**: Fundamental commands that every user needs
- **Examples**: `/start`, `/help`
- **Characteristics**: Simple commands with immediate responses
- **Pattern**: Use `@command` decorator

### Settings Handlers (`settings/`)
- **Purpose**: Configuration and user preferences
- **Examples**: `/locale`, `/profile`
- **Characteristics**: Interactive commands with keyboards/forms
- **Pattern**: Use `@command` decorator + callback handlers

### Sequence Handlers (`sequences/`)
- **Purpose**: Commands that start multi-step workflows
- **Examples**: `/order`, `/support`, `/survey`
- **Characteristics**: Initiate complex workflows using sequence system
- **Pattern**: Use `@sequence_command` decorator + sequence services

### Admin Handlers (`admin/`)
- **Purpose**: Admin-only functionality
- **Examples**: `/stats`, `/broadcast`, `/ban`
- **Characteristics**: Require admin privileges
- **Pattern**: Use `@admin_command` decorator + permission checks

## Adding New Handlers

### 1. Basic Command
```python
# business/handlers/basic/help_handler.py
from aiogram import Router
from aiogram.types import Message
from core.handlers.decorators import command

help_router = Router(name="help_handler")

@command("help", description="Show help information")
async def cmd_help(message: Message) -> None:
    await message.answer("Help information here")
```

### 2. Settings Command
```python
# business/handlers/settings/profile_handler.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from core.handlers.decorators import command

profile_router = Router(name="profile_handler")

@command("profile", description="Manage profile settings")
async def cmd_profile(message: Message) -> None:
    # Show profile keyboard
    pass

@profile_router.callback_query(F.data.startswith("profile:"))
async def handle_profile_callback(callback: CallbackQuery) -> None:
    # Handle profile callbacks
    pass
```

### 3. Sequence Command
```python
# business/handlers/sequences/order_handler.py
from aiogram import Router
from aiogram.types import Message
from core.sequence.decorators import sequence_command

order_router = Router(name="order_handler")

@sequence_command("order", description="Start ordering process")
async def cmd_order(message: Message) -> None:
    # Initialize ordering sequence
    pass
```

### 4. Admin Command
```python
# business/handlers/admin/admin_handlers.py
from aiogram import Router
from aiogram.types import Message
from core.handlers.decorators import admin_command

admin_router = Router(name="admin_handler")

@admin_command("stats", description="Show bot statistics")
async def cmd_stats(message: Message) -> None:
    # Check admin permissions and show stats
    pass
```

## Router Registration

After creating a new handler:

1. **Update the module's `__init__.py`**:
```python
# business/handlers/basic/__init__.py
from .start_handler import start_router
from .help_handler import help_router  # Add new router

__all__ = ['start_router', 'help_router']
```

2. **Update the main router**:
```python
# business/handlers/router.py
from .basic import start_router, help_router  # Add new router

main_router.include_router(start_router)
main_router.include_router(help_router)  # Add new router
```

## Best Practices

- **Single Responsibility**: Each handler file should handle one command/feature
- **Consistent Naming**: Use descriptive names like `start_handler.py`, `locale_handler.py`
- **Error Handling**: Always include proper error handling and logging
- **Documentation**: Include docstrings for all handlers
- **Testing**: Create tests for each handler module
- **Backward Compatibility**: Maintain compatibility during transitions 