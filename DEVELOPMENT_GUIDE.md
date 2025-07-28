# 🤖 Telegram Bot Development Guide

This guide explains how to add new handlers and extend functionality in our layered Telegram bot architecture.

## 📁 Architecture Overview

```
bot-starter-v2/
├── 🔧 core/                      # Framework Layer (Reusable)
│   ├── handlers/                 # Registry system & decorators  
│   ├── middleware/               # Infrastructure middleware
│   ├── utils/                    # Core utilities (logging)
│   └── docs/                     # Core framework documentation
│
├── 🎯 business/                  # Business Layer (Application-specific)
│   ├── handlers/                 # Message handling logic
│   ├── services/                 # Business domain logic
│   └── docs/                     # Business layer documentation
│
├── main.py                       # Application entry point
├── config.py                     # Configuration
└── requirements.txt              # Dependencies
```

## 📚 Complete Documentation

### 🔧 Core Framework Documentation
- **[Core README](core/docs/README.md)** - Framework overview and principles
- **[Handler System](core/docs/handlers.md)** - Registry, decorators, types, protocols
- **[Middleware](core/docs/middleware.md)** - Infrastructure middleware components
- **[Utilities](core/docs/utils.md)** - Logging and core utilities

### 🎯 Business Layer Documentation  
- **[Business README](business/docs/README.md)** - Business layer overview
- **[Handler Development](business/docs/handlers.md)** - How to add and organize handlers
- **[Service Development](business/docs/services.md)** - How to create business services
- **[Practical Examples](business/docs/examples.md)** - Real-world implementation examples

## 🎯 Core Principles

### 🔄 Clean Dependency Flow
```
Business Layer → depends on → Core Framework Layer
     ↑                              ↑
Application Logic              Reusable Components
Domain-Specific               Framework Features
```

### 🎭 Separation of Concerns
- **Core**: Reusable framework components (registry, types, decorators)
- **Business**: Application-specific logic (handlers, services)
- **Handlers**: Thin message processors that delegate to services
- **Services**: Business logic and external integrations

## 🚀 Quick Start: Adding New Features

### 1️⃣ Adding a Simple Command

```python
# In business/handlers/user_handlers.py

@command(
    "hello",
    description="Say hello to the bot",
    category=HandlerCategory.USER,
    usage="/hello [name]",
    examples=["/hello", "/hello John"]
)
async def cmd_hello(message: Message) -> None:
    """Handle /hello command."""
    args = message.text.split()[1:] if message.text else []
    name = args[0] if args else "friend"
    
    await message.answer(f"Hello, {name}! 👋")
```

### 2️⃣ Adding a Service with External API

```python
# 1. Create business/services/weather.py
async def get_weather(city: str) -> str:
    """Get weather information for a city."""
    # Implementation here

# 2. Export in business/services/__init__.py
from .weather import get_weather
__all__.extend(['get_weather'])

# 3. Add handler in business/handlers/user_handlers.py
@command("weather", description="Get weather info")
async def cmd_weather(message: Message) -> None:
    city = " ".join(message.text.split()[1:])
    weather_info = await get_weather(city)
    await message.answer(weather_info)
```

## 🎨 Handler Types & Examples

### 📬 Command Handlers
For bot commands like `/start`, `/help`, `/weather`:

```python
@command(
    "mycommand",                      # Command name (without /)
    description="What this does",     # Help text description
    category=HandlerCategory.USER,    # Core, User, Admin, Utility, Fun
    usage="/mycommand [args]",        # Usage pattern (optional)
    aliases=["alias1", "alias2"],     # Alternative commands (optional)
    examples=["/mycommand example"],  # Usage examples (optional)
    admin_only=False,                 # Restrict to admins (optional)
    hidden=False                      # Hide from help (optional)
)
async def cmd_mycommand(message: Message) -> None:
    """Handle /mycommand."""
    await message.answer("Response")
```

### 📝 Text Handlers
For processing any text message:

```python
@text_handler(
    "text_processor",
    description="Process text messages",
    category=HandlerCategory.USER,
    hidden=True  # Usually hidden since automatic
)
async def handle_text(message: Message) -> None:
    """Process text messages."""
    # Analyze message.text and respond
    pass
```

### 📎 Message Handlers
For non-text content (photos, documents, voice):

```python
@message_handler(
    "media_processor",
    description="Handle media messages",
    category=HandlerCategory.USER,
    hidden=True
)
async def handle_media(message: Message) -> None:
    """Handle photos, documents, etc."""
    if message.content_type == "photo":
        await message.answer("Nice photo!")
    elif message.content_type == "document":
        await message.answer("Thanks for the document!")
```

## 📊 Handler Categories

Organize your handlers by purpose:

- **`HandlerCategory.CORE`**: Essential commands (`/start`, `/help`)
- **`HandlerCategory.USER`**: User interaction features
- **`HandlerCategory.ADMIN`**: Administrative commands
- **`HandlerCategory.UTILITY`**: Helper commands
- **`HandlerCategory.FUN`**: Entertainment features

## 🧪 Development Workflow

### 1. Plan Your Feature
- What business domain does it belong to?
- Does it need external data or APIs?
- How will users interact with it?

### 2. Create Business Logic
```bash
# Create service if needed
touch business/services/my_feature.py

# Implement business logic
# Add to business/services/__init__.py
```

### 3. Create Handlers
```python
# In business/handlers/user_handlers.py
from business.services.my_feature import my_service_function

@command("myfeature", description="My new feature")
async def cmd_myfeature(message: Message) -> None:
    result = await my_service_function(message.text)
    await message.answer(result)
```

### 4. Test Integration
```python
# Test service independently
def test_my_service():
    result = my_service_function("test input")
    assert result == "expected output"

# Test handler with registry
registry = get_registry()
handler = registry.get_handler_by_command("myfeature")
assert handler is not None
```

## 🔍 Registry Inspection

Useful commands for debugging and development:

```python
from core import get_registry

registry = get_registry()

# See all registered handlers
handlers = registry.get_all_handlers()
print(f"Total handlers: {len(handlers)}")

# See all commands and aliases
commands = registry.get_commands()
for cmd, handler in commands.items():
    print(f"/{cmd} → {handler.metadata.description}")

# Generate help text
help_text = registry.generate_help_text()
print(help_text)

# Get usage statistics
stats = registry.get_stats_summary()
print(stats)
```

## ✅ Best Practices

### 🎯 Handler Design
- Keep handlers **thin** - delegate to services
- Use **descriptive names** and comprehensive metadata
- Add **usage examples** for complex commands
- Handle **errors gracefully** with try/catch blocks

### 🔧 Service Design
- Focus on **single responsibility**
- Make services **stateless** when possible
- Provide **clear, simple APIs**
- Handle **errors gracefully** with proper logging
- Make services **easily testable**

### 📁 Organization
- Group related functionality using **categories**
- Use **aliases** for user-friendly command variations
- **Hide automatic handlers** (text/message) from help
- Export components properly in `__init__.py` files

### 🧪 Testing
- Test **services independently** without aiogram
- Mock **external dependencies** (APIs, databases)
- Test **error conditions** and edge cases
- Use **integration tests** for complete workflows

## 🎉 You're Ready!

With this layered architecture, you can:

- ✅ Add new commands easily with rich metadata
- ✅ Create reusable business services
- ✅ Maintain clean separation of concerns  
- ✅ Scale your bot with proper organization
- ✅ Test components independently
- ✅ Generate help text automatically

## 📚 Next Steps

1. **Read the documentation** in `core/docs/` and `business/docs/`
2. **Study existing code** to understand patterns
3. **Start with simple commands** and gradually add complexity
4. **Follow established patterns** for consistency
5. **Test thoroughly** before deploying

---

**Happy coding!** 🚀 The comprehensive documentation in the `docs/` folders provides detailed examples and patterns for every aspect of bot development. 