# 📬 Handler Development Guide

This guide explains how to create message handlers that respond to user interactions in the Telegram bot.

## 🎯 Handler Overview

Handlers are functions that process incoming messages and provide responses to users. They're automatically registered using decorators and support rich metadata for documentation and introspection.

## 🚀 Quick Start: Adding a Localized Command

### Step 1: Add translations to locale files

```json
// locales/en.json
{
  "commands": {
    "joke": {
      "description": "Get a random joke",
      "no_jokes": "Sorry, no jokes available right now!",
      "loading": "Getting you a joke..."
    }
  }
}
```

```json
// locales/es.json  
{
  "commands": {
    "joke": {
      "description": "Obtener un chiste aleatorio",
      "no_jokes": "¡Lo siento, no hay chistes disponibles ahora!",
      "loading": "Buscando un chiste para ti..."
    }
  }
}
```

### Step 2: Create the handler

```python
# business/handlers/user_handlers.py
from core.services.localization import t

@command(
    "joke",
    description="Get a random joke",  # This gets localized automatically
    category=HandlerCategory.USER,
    usage="/joke",
    examples=["/joke"]
)
async def cmd_joke(message: Message) -> None:
    """Handle /joke command with localization."""
    try:
        # Show loading message in user's language
        loading_msg = t("commands.joke.loading", user=message.from_user)
        await message.answer(loading_msg)
        
        # Get joke from service (also localized)
        joke = await get_random_joke(message.from_user)
        await message.answer(joke)
        
    except Exception as e:
        logger.error(f"Error getting joke: {e}")
        error_msg = t("errors.generic", user=message.from_user)
        await message.answer(error_msg)
```

### Step 3: Create the service

```python  
# business/services/joke.py
from core.services.localization import t

async def get_random_joke(user) -> str:
    """Get a random joke in user's language."""
    try:
        # Your joke API logic here
        joke_text = await fetch_joke_from_api()
        return joke_text
    except Exception:
        return t("commands.joke.no_jokes", user=user)
```

## 🎨 Handler Types

### 1. Command Handlers (`@command`)

For bot commands like `/start`, `/help`, `/weather`:

```python
from core.handlers.decorators import command
from core.handlers.types import HandlerCategory

@command(
    "weather",                          # Command name (without /)
    description="Get weather information",  # Help description
    category=HandlerCategory.UTILITY,   # Organization category
    usage="/weather <city>",            # Usage pattern (optional)
    aliases=["w", "clima"],            # Alternative commands (optional)
    examples=[                          # Usage examples (optional)
        "/weather London",
        "/weather Tokyo"
    ],
    admin_only=False,                  # Admin restriction (optional)
    hidden=False,                      # Hide from help (optional)
    tags=["weather", "api"],           # Tags for filtering (optional)
    version="1.0.0",                   # Version tracking (optional)
    author="Your Name"                 # Author info (optional)
)
async def cmd_weather(message: Message) -> None:
    """Handle /weather command."""
    # Implementation here
    pass
```

### 2. Text Handlers (`@text_handler`)

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

### 3. Message Handlers (`@message_handler`)

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
    elif message.content_type == "voice":
        await message.answer("I heard your voice message!")
```

## 📊 Handler Categories

Organize handlers by business purpose:

- **`HandlerCategory.CORE`**: Essential bot commands (`/start`, `/help`)
- **`HandlerCategory.USER`**: User interaction features (`/greet`, text processing)
- **`HandlerCategory.ADMIN`**: Administrative commands
- **`HandlerCategory.UTILITY`**: Helper and utility commands
- **`HandlerCategory.FUN`**: Entertainment features

## 🚀 Step-by-Step: Adding a New Command

### Example: Adding a `/joke` Command

```python
# In business/handlers/user_handlers.py

from business.services.entertainment import get_random_joke  # Create this service

@command(
    "joke",
    description="Get a random joke",
    category=HandlerCategory.FUN,
    usage="/joke",
    examples=["/joke"],
    tags=["entertainment", "humor"]
)
async def cmd_joke(message: Message) -> None:
    """Handle /joke command."""
    try:
        joke = await get_random_joke()  # Delegate to service
        await message.answer(f"😄 {joke}")
        
    except Exception as e:
        logger.error(f"Error getting joke: {e}")
        await message.answer("Sorry, I couldn't think of a joke right now!")
```

### Example: Adding Command Arguments

```python
@command(
    "remind",
    description="Set a reminder",
    category=HandlerCategory.UTILITY,
    usage="/remind <time> <message>",
    examples=["/remind 5m Take a break", "/remind 1h Meeting with team"]
)
async def cmd_remind(message: Message) -> None:
    """Handle /remind command with arguments."""
    args = message.text.split()[1:] if message.text else []
    
    if len(args) < 2:
        await message.answer(
            "Usage: /remind <time> <message>\n"
            "Examples: /remind 5m Take a break"
        )
        return
    
    time_str = args[0]
    reminder_text = " ".join(args[1:])
    
    try:
        # Delegate to service for parsing and scheduling
        success = await schedule_reminder(
            user_id=message.from_user.id,
            time_str=time_str,
            text=reminder_text
        )
        
        if success:
            await message.answer(f"✅ Reminder set: {reminder_text}")
        else:
            await message.answer("❌ Invalid time format. Use: 5m, 1h, 2d")
            
    except Exception as e:
        logger.error(f"Error setting reminder: {e}")
        await message.answer("Sorry, couldn't set reminder. Please try again.")
```

## 🎯 Handler Best Practices

### 1. Keep Handlers Thin

```python
# ❌ BAD: Business logic in handler
@command("weather", description="Get weather")
async def cmd_weather(message: Message) -> None:
    args = message.text.split()[1:]
    if not args:
        await message.answer("Please specify a city")
        return
    
    city = " ".join(args)
    
    # Don't put business logic here!
    async with aiohttp.ClientSession() as session:
        url = f"https://api.weather.com/v1/current?city={city}"
        async with session.get(url) as response:
            data = await response.json()
            # ... more business logic
    
    await message.answer(f"Weather: {data['temp']}°C")

# ✅ GOOD: Delegate to service
@command("weather", description="Get weather")
async def cmd_weather(message: Message) -> None:
    args = message.text.split()[1:] if message.text else []
    
    if not args:
        await message.answer("Please specify a city: /weather <city>")
        return
    
    city = " ".join(args)
    weather_info = await get_weather(city)  # Service handles business logic
    await message.answer(weather_info)
```

### 2. Handle Errors Gracefully

```python
@command("example", description="Example with proper error handling")
async def cmd_example(message: Message) -> None:
    try:
        result = await some_service_function()
        await message.answer(result)
        
    except ServiceError as e:
        # Expected service errors
        logger.warning(f"Service error for user {message.from_user.id}: {e}")
        await message.answer("Service is temporarily unavailable. Please try again later.")
        
    except ValidationError as e:
        # User input errors
        await message.answer(f"Invalid input: {e}")
        
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in example command: {e}", exc_info=True)
        await message.answer("Something went wrong. Please try again.")
```

### 3. Provide Rich Metadata

```python
@command(
    "weather",
    description="Get current weather information for any city",
    category=HandlerCategory.UTILITY,
    usage="/weather <city name>",
    examples=[
        "/weather London",
        "/weather New York",
        "/weather San Francisco"
    ],
    aliases=["w"],  # Allow /w as shortcut
    tags=["weather", "api", "information"]
)
async def cmd_weather(message: Message) -> None:
    """
    Get weather information for a specified city.
    
    Uses external weather API to fetch current conditions
    and provides user-friendly formatted response.
    """
    # Implementation
```

### 4. Use Appropriate Categories

```python
# Core functionality - always available
@command("start", category=HandlerCategory.CORE)
@command("help", category=HandlerCategory.CORE)

# User features - main bot functionality
@command("greet", category=HandlerCategory.USER)
@command("profile", category=HandlerCategory.USER)

# Administrative commands
@command("ban", category=HandlerCategory.ADMIN, admin_only=True)
@command("stats", category=HandlerCategory.ADMIN, admin_only=True)

# Utility commands
@command("weather", category=HandlerCategory.UTILITY)
@command("remind", category=HandlerCategory.UTILITY)

# Entertainment
@command("joke", category=HandlerCategory.FUN)
@command("game", category=HandlerCategory.FUN)
```

## 🔧 Handler Organization

### File Structure

```python
# business/handlers/user_handlers.py - Main user interactions
# business/handlers/admin_handlers.py - Administrative commands (future)
# business/handlers/game_handlers.py - Game-related commands (future)
```

### Current Structure in `user_handlers.py`

```python
# Core commands
@command("start", category=HandlerCategory.CORE)
async def cmd_start(message: Message) -> None: ...

@command("help", category=HandlerCategory.CORE)
async def cmd_help(message: Message) -> None: ...

# User interaction commands
@command("greet", category=HandlerCategory.USER)
async def cmd_greet(message: Message) -> None: ...

# Automatic handlers (hidden from help)
@text_handler("greeting_responder", hidden=True)
async def handle_text_message(message: Message) -> None: ...

@message_handler("media_responder", hidden=True)
async def handle_other_messages(message: Message) -> None: ...
```

## 🧪 Testing Handlers (Future Enhancement)

**Note**: Comprehensive testing framework is planned for future releases. The current handler architecture is designed to support easy testing through dependency injection and clear separation of concerns.

### Planned Testing Approach

- **Unit Testing**: Individual handler functions with mocked dependencies
- **Integration Testing**: Handler registration and aiogram router integration  
- **Localization Testing**: Multi-language response verification

## 🔍 Handler Introspection

### Registry Integration

All handlers are automatically registered and can be inspected:

```python
from core import get_registry

registry = get_registry()

# Get all handlers
all_handlers = registry.get_all_handlers()
print(f"Total handlers: {len(all_handlers)}")

# Get specific handler
weather_handler = registry.get_handler_by_command("weather")
if weather_handler:
    print(f"Description: {weather_handler.metadata.description}")
    print(f"Usage: {weather_handler.metadata.usage}")
    print(f"Examples: {weather_handler.metadata.examples}")

# Get handlers by category
utility_handlers = registry.get_handlers_by_category(HandlerCategory.UTILITY)
for handler in utility_handlers:
    print(f"/{handler.metadata.command} - {handler.metadata.description}")
```

### Auto-Generated Help

The `/help` command automatically includes all registered handlers:

```python
@command("help", category=HandlerCategory.CORE)
async def cmd_help(message: Message) -> None:
    """Generate help from registry metadata."""
    registry = get_registry()
    help_text = registry.generate_help_text()  # Auto-generated!
    await message.answer(help_text, parse_mode="HTML")
```

## 🚀 Advanced Handler Patterns

### State Management

```python
# Using handler data for simple state
@command("quiz", description="Start a quiz")
async def cmd_quiz(message: Message) -> None:
    # Store state in user data or database
    await start_quiz_session(message.from_user.id)
    await message.answer("Quiz started! What's 2+2?")

@text_handler("quiz_responder", hidden=True)
async def handle_quiz_answer(message: Message) -> None:
    # Check if user is in quiz mode
    if await is_in_quiz(message.from_user.id):
        result = await process_quiz_answer(message.from_user.id, message.text)
        await message.answer(result)
```

### Middleware Integration

```python
# Handlers automatically get middleware data
@command("admin", description="Admin command", admin_only=True)
async def cmd_admin(message: Message, **data) -> None:
    # Middleware can inject data like is_admin
    if not data.get('is_admin', False):
        await message.answer("You don't have admin privileges")
        return
    
    # Admin functionality here
```

### Error Recovery

```python
@command("upload", description="Upload and process file")
async def cmd_upload(message: Message) -> None:
    try:
        await process_file(message)
    except FileTooBigError:
        await message.answer("File is too large (max 10MB)")
    except UnsupportedFormatError:
        await message.answer("Unsupported file format")
    except ExternalServiceError:
        await message.answer("Processing service unavailable, try again later")
    except Exception as e:
        logger.error(f"Unexpected error in upload: {e}")
        await message.answer("Upload failed, please try again")
```

## 📚 Next Steps

1. **Study existing handlers** in `business/handlers/user_handlers.py`
2. **Start with simple commands** and gradually add complexity
3. **Create supporting services** in `business/services/`
4. **Document thoroughly** with clear descriptions and examples
5. **Use registry introspection** for debugging and monitoring

The handler system provides a powerful, type-safe way to build scalable bot functionality with automatic help generation and comprehensive metadata. 