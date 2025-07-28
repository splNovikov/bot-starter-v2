# 🎯 Handler Registry System

The handler registry system is the core of the framework, providing type-safe, metadata-rich handler registration and management.

## 📋 Overview

The handler system consists of four main components:

1. **Registry** (`registry.py`) - Central handler management and introspection
2. **Decorators** (`decorators.py`) - Clean registration API with `@command`, `@text_handler`, etc.
3. **Types** (`types.py`) - Data structures and enums for type safety
4. **Protocols** (`protocols.py`) - Type interfaces for different handler types

## 🏗️ Registry Architecture

### Central Registry (`HandlersRegistry`)

The registry maintains all registered handlers and provides:

- **Handler Storage**: Maps handler IDs to `RegisteredHandler` objects
- **Command Mapping**: Maps commands and aliases to handlers
- **Category Organization**: Groups handlers by business domain
- **Statistics Tracking**: Monitors usage, errors, and performance
- **aiogram Integration**: Automatically registers handlers with routers

### Registry Methods

```python
from core.handlers.registry import get_registry

registry = get_registry()

# Registration (usually done by decorators)
handler_id = registry.register(handler_func, metadata)

# Retrieval
handler = registry.get_handler("handler_id")
handler = registry.get_handler_by_command("greet")
all_handlers = registry.get_all_handlers()

# Organization
core_handlers = registry.get_handlers_by_category(HandlerCategory.CORE)
command_handlers = registry.get_handlers_by_type(HandlerType.COMMAND)

# Introspection
commands = registry.get_commands()  # Dict[command, handler]
help_text = registry.generate_help_text()
stats = registry.get_stats_summary()
```

## 🎨 Decorator System

### @command - Command Handlers

For bot commands like `/start`, `/help`, `/weather`:

```python
from core.handlers.decorators import command
from core.handlers.types import HandlerCategory

@command(
    "weather",                        # Command name (without /)
    description="Get weather info",   # Help description
    category=HandlerCategory.UTILITY, # Organization category
    usage="/weather <city>",          # Usage pattern (optional)
    aliases=["w", "clima"],          # Alternative commands (optional)
    examples=[                        # Usage examples (optional)
        "/weather London",
        "/weather Tokyo"
    ],
    admin_only=False,                # Admin restriction (optional)
    hidden=False,                    # Hide from help (optional)
    tags=["weather", "api"],         # Tags for filtering (optional)
    version="1.0.0",                 # Version tracking (optional)
    author="Your Name"               # Author info (optional)
)
async def cmd_weather(message: Message) -> None:
    """Handle /weather command."""
    # Implementation here
    pass
```

### @text_handler - Text Processing

For processing any text message:

```python
from core.handlers.decorators import text_handler

@text_handler(
    "echo_processor",
    description="Echo user messages",
    category=HandlerCategory.USER,
    hidden=True  # Usually hidden since automatic
)
async def handle_text(message: Message) -> None:
    """Process text messages."""
    await message.answer(f"You said: {message.text}")
```

### @message_handler - Media Processing

For non-text content (photos, documents, voice, etc.):

```python
from core.handlers.decorators import message_handler

@message_handler(
    "media_processor",
    description="Handle media messages", 
    category=HandlerCategory.USER,
    hidden=True
)
async def handle_media(message: Message) -> None:
    """Handle media messages."""
    if message.content_type == "photo":
        await message.answer("Nice photo!")
    elif message.content_type == "document":
        await message.answer("Thanks for the document!")
```

### @handler - Generic Registration

For custom handler types or advanced usage:

```python
from core.handlers.decorators import handler
from core.handlers.types import HandlerType

@handler(
    "custom_handler",
    HandlerType.CALLBACK,
    description="Handle callback queries",
    category=HandlerCategory.USER
)
async def handle_callback(callback: CallbackQuery) -> None:
    """Handle callback queries."""
    await callback.answer("Button clicked!")
```

## 📊 Type System

### Handler Types (`HandlerType`)

```python
from core.handlers.types import HandlerType

HandlerType.COMMAND    # Bot commands (/start, /help)
HandlerType.TEXT       # Text message processing
HandlerType.MESSAGE    # Media and other message types
HandlerType.CALLBACK   # Inline keyboard callbacks
HandlerType.INLINE     # Inline query handling
```

### Handler Categories (`HandlerCategory`)

```python
from core.handlers.types import HandlerCategory

HandlerCategory.CORE     # Essential bot commands (start, help)
HandlerCategory.USER     # User interaction features
HandlerCategory.ADMIN    # Administrative commands
HandlerCategory.UTILITY  # Helper and utility commands
HandlerCategory.FUN      # Entertainment features
```

### Handler Metadata (`HandlerMetadata`)

Complete metadata structure for handlers:

```python
@dataclass
class HandlerMetadata:
    # Basic information
    name: str                    # Handler name
    description: str            # Help description
    handler_type: HandlerType   # Type of handler
    category: HandlerCategory   # Organization category
    
    # Command-specific
    command: Optional[str]      # Command name (for commands)
    aliases: List[str]          # Alternative commands
    usage: Optional[str]        # Usage pattern
    examples: List[str]         # Usage examples
    
    # Behavior configuration
    enabled: bool               # Handler enabled/disabled
    hidden: bool               # Hide from help
    admin_only: bool           # Require admin privileges
    
    # Additional metadata
    tags: List[str]            # Tags for categorization
    version: str               # Version tracking
    author: Optional[str]      # Author information
```

### Registered Handler (`RegisteredHandler`)

Container for handlers with metadata and statistics:

```python
@dataclass
class RegisteredHandler:
    function: HandlerFunction   # The actual handler function
    metadata: HandlerMetadata   # Handler metadata
    stats: HandlerStats        # Usage statistics
    
    @property
    def identifier(self) -> str:
        """Unique identifier for this handler."""
        # Returns "cmd_command" for commands or "type_name" for others
```

## 🔒 Protocol System

### Type-Safe Interfaces

Protocols ensure handlers conform to expected signatures:

```python
from core.handlers.protocols import CommandHandler, TextHandler

# These are protocols that define the expected signatures
@runtime_checkable
class CommandHandler(Protocol):
    async def __call__(self, message: Message) -> None: ...

@runtime_checkable  
class TextHandler(Protocol):
    async def __call__(self, message: Message) -> None: ...
```

### Available Protocols

- **`BaseHandler`**: Base protocol for all handlers
- **`CommandHandler`**: For command handlers (`/start`, `/help`)
- **`TextHandler`**: For text message processors
- **`MessageHandler`**: For media and other message types
- **`CallbackHandler`**: For inline keyboard callbacks
- **`InlineHandler`**: For inline query processing

### Protocol Validation

The registry validates handlers against their expected protocols:

```python
# This happens automatically during registration
def validate_handler_signature(handler: Any, expected_protocol: type[BaseHandler]) -> bool:
    """Validate handler conforms to protocol."""
    return isinstance(handler, expected_protocol)
```

## 📈 Statistics System

### Handler Statistics (`HandlerStats`)

Each handler automatically tracks:

```python
@dataclass
class HandlerStats:
    calls: int = 0              # Number of times called
    errors: int = 0             # Number of errors
    last_called: Optional[float] # Last call timestamp
    avg_response_time: float    # Average response time
```

### Statistics Collection

Statistics are collected automatically through middleware wrapper:

```python
# This happens automatically in the registry
def _wrap_handler_with_stats(self, handler: RegisteredHandler) -> Callable:
    """Wrap handler with statistics tracking."""
    @wraps(handler.function)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        handler.stats.calls += 1
        
        try:
            result = await handler.function(*args, **kwargs)
            # Update timing stats
            duration = time.time() - start_time
            handler.stats.avg_response_time = calculate_average(duration)
            handler.stats.last_called = time.time()
            return result
        except Exception as e:
            handler.stats.errors += 1
            logger.error(f"Error in handler {handler.identifier}: {e}")
            raise
```

### Registry Statistics

Get overall statistics:

```python
stats = registry.get_stats_summary()
# Returns:
{
    "total_handlers": 5,
    "total_calls": 150,
    "total_errors": 2,
    "error_rate": 0.013,
    "handlers_by_type": {"command": 3, "text": 1, "message": 1},
    "handlers_by_category": {"core": 2, "user": 3}
}
```

## 🔧 Auto-Generated Help

### Help Text Generation

The registry automatically generates help text from handler metadata:

```python
help_text = registry.generate_help_text()

# Generates formatted text like:
"""
🤖 Available Commands:

Core:
  /help - Show available commands and usage information
  /start - Get a welcome greeting message

User:
  /greet - Send a friendly greeting message
    Usage: /greet
    
Utility:
  /weather - Get weather information
    Usage: /weather <city>
    Examples: /weather London, /weather Tokyo
"""
```

### Category-Specific Help

Generate help for specific categories:

```python
admin_help = registry.generate_help_text(category=HandlerCategory.ADMIN)
```

## 🎯 Best Practices

### Handler Design
- Keep handlers **thin** - delegate business logic to services
- Use **descriptive names** and comprehensive metadata
- Add **usage examples** for complex commands
- Handle **errors gracefully** with proper logging

### Metadata Usage
- Provide **clear descriptions** for auto-generated help
- Use **appropriate categories** for organization
- Add **aliases** for user-friendly variations
- Include **usage patterns** and **examples**

### Type Safety
- Use **protocol-based typing** for handler signatures
- Leverage **runtime validation** to catch errors early
- Provide **proper type hints** for IDE support

### Performance
- Registry provides **automatic statistics** collection
- Use **registry introspection** for debugging
- Monitor **error rates** and **response times**

## 🚀 Advanced Usage

### Custom Handler Types

Extend the system with new handler types:

```python
# Add to HandlerType enum
class HandlerType(Enum):
    CUSTOM = "custom"

# Create protocol
@runtime_checkable
class CustomHandler(Protocol):
    async def __call__(self, event: CustomEvent) -> None: ...

# Add to protocol mapping
def get_handler_protocol(handler_type_name: str) -> Optional[type[BaseHandler]]:
    protocol_map = {
        'custom': CustomHandler,
        # ... existing mappings
    }
    return protocol_map.get(handler_type_name.lower())
```

### Runtime Handler Management

Dynamically register/unregister handlers:

```python
# Register handler programmatically
registry.register(my_handler_function, metadata)

# Unregister handler
registry.unregister("handler_id")

# Check registration status
if registry.is_registered("handler_id"):
    # Handler is registered
```

The handler registry system provides a powerful, type-safe foundation for building scalable Telegram bots with rich metadata and automatic introspection capabilities. 