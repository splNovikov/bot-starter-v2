# 🎯 Business Logic Documentation

The business layer contains application-specific logic, handlers, and services that implement the bot's functionality using the core framework.

## 📁 Business Architecture

```
business/
├── handlers/           # Application-specific handlers
│   └── user_handlers.py # User interaction handlers
├── services/           # Business logic services
│   └── greeting.py     # Greeting business logic
└── docs/              # Business layer documentation
    ├── README.md      # This file
    ├── handlers.md    # How to add handlers
    ├── services.md    # How to create services
    └── examples.md    # Practical examples
```

## 🎯 Core Principles

### 1. **Clean Architecture**
The business layer depends on the core framework but never the reverse. This keeps the core reusable and the business logic focused.

### 2. **Separation of Concerns**
- **Handlers**: Thin message processors that handle user interactions
- **Services**: Business logic and external integrations
- **Clear boundaries**: Each component has a single responsibility

### 3. **Domain-Driven Design**
Business logic is organized around domains (greeting, weather, user management, etc.) rather than technical concerns.

### 4. **Testability**
All business logic is designed to be easily testable in isolation from Telegram-specific concerns.

## 🚀 Key Features

### **Handler-Service Architecture**
- Handlers process messages and delegate to services
- Services contain reusable business logic
- Clean separation enables easy testing and maintenance

### **Automatic Registration**
- Handlers are automatically registered with the core framework
- Rich metadata enables auto-generated help and introspection
- Type safety prevents common errors

### **Domain Organization**
- Services are organized by business domain
- Clear module structure makes codebase navigable
- Easy to add new features and domains

## 🎨 Current Implementation

### **User Handlers**
- **`/start`**: Welcome new users with greeting
- **`/greet`**: Send friendly greeting (with `/hi`, `/hello` aliases)
- **`/help`**: Auto-generated help from handler metadata
- **Text processing**: Automatic greeting for any text message
- **Media handling**: Response to photos, documents, etc.

### **Greeting Service**
- **`get_username()`**: Extract display name from user
- **`create_greeting_message()`**: Generate personalized greeting
- **`send_greeting()`**: Complete greeting workflow with logging

## 🔄 Development Workflow

### **Adding New Features**

1. **Plan the Domain**: Identify what business area the feature belongs to
2. **Create Services**: Implement business logic in `services/`
3. **Create Handlers**: Add user-facing handlers in `handlers/`
4. **Export Components**: Update `__init__.py` files for clean imports
5. **Test Integration**: Verify everything works together

### **Example: Adding Weather Feature**

```python
# 1. Create business/services/weather.py
async def get_weather(city: str) -> str:
    """Get weather information for a city."""
    # Business logic here

# 2. Add handler in business/handlers/user_handlers.py
@command("weather", description="Get weather info")
async def cmd_weather(message: Message) -> None:
    # Handler logic here

# 3. Export in business/services/__init__.py
from .weather import get_weather
__all__.extend(['get_weather'])
```

## 📊 Handler Categories

Business handlers are organized by purpose:

- **`CORE`**: Essential functionality (`/start`, `/help`)
- **`USER`**: User interaction features (`/greet`, text processing)
- **`ADMIN`**: Administrative commands (future)
- **`UTILITY`**: Helper commands (future: `/weather`, `/status`)
- **`FUN`**: Entertainment features (future: games, jokes)

## 🔍 Registry Integration

The business layer leverages the core registry for:

```python
from core import get_registry

registry = get_registry()

# Introspection
handlers = registry.get_all_handlers()
commands = registry.get_commands()

# Auto-generated help
help_text = registry.generate_help_text()

# Statistics
stats = registry.get_stats_summary()
```

## 📚 Detailed Documentation

- **[Handler Development](handlers.md)** - How to add and organize handlers
- **[Service Development](services.md)** - How to create business services
- **[Practical Examples](examples.md)** - Real-world implementation examples

## 🔄 Integration with Core Framework

The business layer consumes core framework services:

```python
# Import core components
from core.handlers.decorators import command
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger

# Core framework provides:
# - Type-safe handler registration
# - Rich metadata system
# - Automatic help generation
# - Statistics collection
# - Logging infrastructure
```

## 🎯 Design Patterns

### **Thin Handlers**
```python
@command("example", description="Example command")
async def cmd_example(message: Message) -> None:
    """Keep handlers thin - delegate to services."""
    result = await some_business_service(message.text)
    await message.answer(result)
```

### **Service Composition**
```python
async def complex_workflow(message: Message) -> None:
    """Compose multiple services for complex workflows."""
    user_data = await get_user_data(message.from_user.id)
    processed_data = await process_data(user_data)
    result = await generate_response(processed_data)
    await send_response(message, result)
```

### **Error Handling**
```python
@command("example", description="Example with error handling")
async def cmd_example(message: Message) -> None:
    """Handle errors gracefully with fallbacks."""
    try:
        result = await external_service()
        await message.answer(result)
    except ServiceError:
        await message.answer("Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await message.answer("Something went wrong")
```

## 🎉 Getting Started

1. **Study existing handlers** in `business/handlers/user_handlers.py`
2. **Examine services** in `business/services/greeting.py`
3. **Read detailed guides** in the docs/ folder
4. **Start with simple commands** and gradually add complexity
5. **Follow the established patterns** for consistency

The business layer provides a clean, organized way to implement bot functionality while leveraging the powerful core framework for infrastructure concerns.

## 🚀 Future Expansion

The architecture supports easy expansion:

- **New domains**: Weather, database, authentication, notifications
- **Complex workflows**: Multi-step interactions, state management
- **External integrations**: APIs, databases, file systems
- **Advanced features**: Inline keyboards, games, payment processing

Start simple and build incrementally using the established patterns! 