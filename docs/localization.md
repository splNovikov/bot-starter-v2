# 🌍 Localization System Guide

Complete guide to the bot's multi-language support system with automatic language detection and user preferences.

## 🎯 Overview

The localization system provides comprehensive multi-language support with:
- **Automatic Detection**: Uses Telegram user locale with smart fallback chain
- **User Preferences**: Per-user language settings with persistent storage  
- **Localized Help**: Dynamic help generation in user's language
- **Interactive Switching**: `/language` command with inline keyboard
- **Parameter Substitution**: Dynamic content with type-safe parameters

## ⚠️ **CRITICAL: What Should Be Localized**

**IMPORTANT PRINCIPLE**: Only user-facing messages should be localized. System logs, developer messages, and internal communications must always be in English.

### ✅ **DO Localize (User-Facing):**
- Bot responses to user commands
- Error messages displayed to users  
- Help text and command descriptions
- User interface elements (buttons, menus)
- Welcome and greeting messages
- Status messages shown to users

### ❌ **DO NOT Localize (System/Developer):**
- Logger messages (`logger.info`, `logger.error`, etc.)
- Exception messages for developers
- Debug information and system logs
- Internal validation messages
- API responses to other services
- Configuration and startup messages

### Example of Correct Usage:

```python
async def my_handler(message: Message) -> None:
    try:
        # System log - ALWAYS English
        logger.info(f"Processing command from user {message.from_user.id}")
        
        result = await some_service()
        
        # User message - Localized
        success_msg = t("commands.success", user=message.from_user, result=result)
        await message.answer(success_msg)
        
    except Exception as e:
        # System log - ALWAYS English
        logger.error(f"Error in handler: {e}")
        
        # User message - Localized
        error_msg = t("errors.generic", user=message.from_user)
        await message.answer(error_msg)
```

## 🏗️ Architecture

### Components

- **`LocalizationService`** - Core localization logic with caching
- **`LocalizationMiddleware`** - Automatic language detection for handlers
- **`LocalizedHelpService`** - Generates help text in user's language
- **Language Handlers** - Commands for language management (`/language`, `/languages`)

### Language Detection Chain

```
1. User Preference (set via /language command)
        ↓ (if not set)
2. Telegram Locale (from user.language_code)  
        ↓ (if not available)
3. Default Language (configured in .env)
```

## 🚀 Quick Start

### Adding New Languages

1. **Create locale file**: `locales/new_language.json`
2. **Add to config**: Update `SUPPORTED_LANGUAGES` in `.env`
3. **Restart bot**: New language automatically available

Example locale file structure:
```json
{
  "_language_name": "Français",
  "_language_code": "fr",
  "_version": "1.0.0",
  "greetings": {
    "hello": "Bonjour, {username}!"
  },
  "commands": {
    "help": {
      "description": "Afficher les commandes disponibles"
    }
  },
  "errors": {
    "generic": "Une erreur s'est produite."
  }
}
```

### Using Translations in Code

```python
from core.services.localization import t
from core.utils.logger import get_logger

logger = get_logger()

# User-facing message - LOCALIZE
greeting = t("greetings.hello", user=message.from_user, username="John")

# System log - ENGLISH ONLY
logger.info(f"User {message.from_user.id} sent greeting command")

# User error message - LOCALIZE
error = t("errors.api_failed", user=user, service="Weather", code=404)

# System error log - ENGLISH ONLY  
logger.error(f"Weather API failed with code 404 for user {user.id}")
```

## 📝 Translation Key Organization

### Hierarchical Structure

**Recommended structure** for maintainability:

```json
{
  "greetings": {
    "hello": "Hello, {username}!",
    "welcome": "Welcome to the bot!"
  },
  "commands": {
    "help": {
      "description": "Show available commands",
      "header": "🤖 Available Commands:",
      "no_commands": "No commands available."
    },
    "weather": {
      "description": "Get weather information",
      "city_required": "Please specify a city",
      "not_found": "City {city} not found",
      "result": "{city}: {temp}°C, {condition}"
    }
  },
  "errors": {
    "generic": "Something went wrong. Please try again.",
    "network": "Network error. Please check your connection.",
    "api_failed": "{service} service error ({code})"
  },
  "messages": {
    "processing": "Processing your request...",
    "success": "Operation completed successfully!"
  }
}
```

**Note**: No `logging` or `system` sections should exist in locale files. These messages should use Python's logger directly in English.

### Key Naming Conventions

- **Dot notation**: `category.subcategory.key`
- **Descriptive names**: `weather.city_not_found` instead of `weather.error1`
- **Consistent prefixes**: All command descriptions under `commands.{command}.description`
- **Parameter names**: Use clear parameter names like `{username}`, `{city}`, `{temp}`

## 🎨 Advanced Usage

### Service Integration

```python
class WeatherService:
    def __init__(self):
        self.localization = get_localization_service()
        self.logger = get_logger()
    
    async def get_weather(self, city: str, user) -> str:
        """Get localized weather information."""
        try:
            # System log - English only
            self.logger.info(f"Fetching weather for {city} requested by user {user.id}")
            
            # API call
            data = await self._fetch_weather_data(city)
            
            # User response - Localized
            return self.localization.t(
                "weather.result",
                user=user,
                city=data['city'],
                temp=data['temp'],
                condition=data['condition']
            )
        except CityNotFoundError:
            # System log - English only
            self.logger.warning(f"City not found: {city}")
            
            # User response - Localized
            return self.localization.t("weather.city_not_found", user=user, city=city)
        except APIError as e:
            # System log - English only
            self.logger.error(f"Weather API error: {e}")
            
            # User response - Localized
            return self.localization.t("errors.weather_unavailable", user=user)
```

### Middleware Integration

The `LocalizationMiddleware` automatically adds these to handler context:

```python
async def my_handler(message: Message, user_language: str, t: Callable) -> None:
    # user_language: detected user language ("en", "es", "ru", etc.)
    # t: pre-configured translation function for this user
    
    # System log - English only
    logger.info(f"Handler called with user language: {user_language}")
    
    # User response - Localized via injected t() function
    response = t("commands.example.response", param1="value")
    await message.answer(response)
```

### User Language Management

```python
from core.services.localization import get_localization_service

service = get_localization_service()

# Get user's current language
current_lang = service.get_user_language(user)

# Set user's language preference  
success = service.set_user_language(user.id, "es")

# System log about language change - English only
logger.info(f"User {user.id} changed language from {old_lang} to es")

# Get all supported languages
languages = service.get_supported_languages()
# Returns: {"en": "English", "es": "Español", "ru": "Русский"}
```

## 🔧 Best Practices

### 1. Error Handling

```python
async def robust_handler(message: Message) -> None:
    """Example of robust error handling with proper localization."""
    try:
        # System log - English only
        logger.info(f"Processing request from user {message.from_user.id}")
        
        # Main logic
        result = await some_service_function()
        
        # User success message - Localized
        success_msg = t("commands.example.success", user=message.from_user, result=result)
        await message.answer(success_msg)
        
    except ValidationError as e:
        # System log - English only
        logger.warning(f"Validation error for user {message.from_user.id}: {e}")
        
        # User error message - Localized
        error_msg = t("errors.invalid_input", user=message.from_user, details=str(e))
        await message.answer(error_msg)
        
    except ServiceUnavailableError:
        # System log - English only
        logger.error(f"Service unavailable for user {message.from_user.id}")
        
        # User error message - Localized
        error_msg = t("errors.service_unavailable", user=message.from_user)
        await message.answer(error_msg)
        
    except Exception as e:
        # System log - English only (with full context)
        logger.error(f"Unexpected error for user {message.from_user.id}: {e}", exc_info=True)
        
        # User error message - Localized
        error_msg = t("errors.generic", user=message.from_user)
        await message.answer(error_msg)
```

### 2. Parameter Validation

```python
# Safe parameter substitution
def safe_translate(key: str, user: User, **params) -> str:
    """Safely translate with parameter validation."""
    # System log - English only
    logger.debug(f"Translating key '{key}' for user {user.id} with params: {list(params.keys())}")
    
    # Sanitize parameters
    safe_params = {}
    for k, v in params.items():
        if isinstance(v, str):
            safe_params[k] = v.strip()[:100]  # Limit length
        else:
            safe_params[k] = str(v)
    
    return t(key, user=user, **safe_params)
```

### 3. Testing Localized Features (Future Enhancement)

**Note**: Testing framework is planned for future releases. Current localization system is designed with testability in mind through clear interfaces and dependency injection.

The planned testing approach will verify:
- Correct language detection for different user scenarios
- Proper parameter substitution in different languages  
- Fallback behavior when translations are missing
- System logs remain in English regardless of user language

## ⚡ Performance

The localization system is optimized for production use:

- **Lazy Loading**: Translation files loaded only when needed
- **LRU Caching**: Frequently used translations cached in memory (`@lru_cache`)
- **Efficient Fallbacks**: Smart fallback chain avoids repeated lookups
- **Minimal Overhead**: Translation lookup is O(1) for most cases

### Caching Strategy

```python
# The system automatically caches:
# - Translation files (per language)
# - User language preferences  
# - Computed translation results

# Cache stats (for monitoring) - system log in English
service = get_localization_service()
logger.info(f"Localization cache stats: {service._load_language.cache_info()}")
```

## 🐛 Debugging

### Enable Debug Logging

```python
import logging

# System debug logs - English only
logging.getLogger("business.services.localization").setLevel(logging.DEBUG)

# This will show (in English):
# - Language detection for each user
# - Translation key lookups
# - Fallback chain execution
# - Cache hits/misses
```

### Common Issues

**Translation not found:**
```
ERROR - Translation key 'missing.key' not found in default language en
```
- Check key exists in `locales/en.json`
- Verify key path is correct (dot notation)

**Parameter substitution error:**
```
ERROR - Error formatting translation 'weather.result' with params {...}
```  
- Ensure all required parameters are provided
- Check parameter names match in translation string

**Language not loading:**
```
WARNING - Language file locales/invalid.json not found or invalid
```
- Verify JSON syntax is valid
- Check file permissions and path

**System logs in wrong language:**
```
INFO - Сообщение от Pavel (ID: 123, Chat: 456): text
```
- **Fix**: Replace `t("logging.xxx")` with direct `logger.info("Message from Pavel...")` 
- System logs must always be in English

## 📊 Monitoring

### Built-in Statistics

```python
from core.handlers.registry import get_registry
from core.services.localization import get_localization_service

# Language usage stats - system logs in English
localization = get_localization_service()
supported_langs = localization.get_supported_languages()
logger.info(f"Supported languages: {list(supported_langs.keys())}")

# Handler usage by language - system logs in English
registry = get_registry()
handlers = registry.get_all_handlers()
logger.info(f"Total handlers with localization: {len(handlers)}")
```

## 🚀 Extension Examples

### Adding Context-Aware Translations

```python
# Context-based translations
def context_translate(base_key: str, context: str, user: User, **params) -> str:
    """Translate with context fallback."""
    # System log - English only
    logger.debug(f"Attempting context translation: {base_key}.{context}")
    
    # Try context-specific key first
    context_key = f"{base_key}.{context}"
    
    try:
        return t(context_key, user=user, **params)
    except KeyError:
        # System log - English only
        logger.debug(f"Context key not found, falling back to base: {base_key}")
        
        # Fall back to base key
        return t(base_key, user=user, **params)

# Usage
greeting = context_translate("greetings.hello", "morning", user=user, username="John")
# Tries: greetings.hello.morning -> greetings.hello
```

### Pluralization Support

```json
{
  "messages": {
    "items_count": {
      "zero": "No items",
      "one": "1 item", 
      "other": "{count} items"
    }
  }
}
```

```python
def pluralize(key: str, count: int, user: User, **params) -> str:
    """Handle pluralization."""
    # System log - English only
    logger.debug(f"Pluralizing {key} with count {count}")
    
    if count == 0:
        plural_key = f"{key}.zero"
    elif count == 1:
        plural_key = f"{key}.one"
    else:
        plural_key = f"{key}.other"
    
    return t(plural_key, user=user, count=count, **params)
```

## 🎯 Migration Guide

If you have existing code with localized system logs, follow this migration pattern:

### Before (Incorrect):
```python
# ❌ Wrong - system log localized
log_msg = t("logging.user_message", user=user, username=username, user_id=user.id)
logger.info(log_msg)

# ❌ Wrong - system message localized  
startup_msg = t("system.startup", user=None)
logger.info(startup_msg)
```

### After (Correct):
```python
# ✅ Correct - system log in English
logger.info(f"Message from {username} (ID: {user.id}): {message_type}")

# ✅ Correct - system message in English
logger.info("Bot is starting up...")
```

Remember: **System logs are for developers and operations - they must be in English. User messages are for end users - they should be localized.**

This localization system provides a solid foundation for multi-language bots that can scale globally while maintaining professional development standards! 🌍 