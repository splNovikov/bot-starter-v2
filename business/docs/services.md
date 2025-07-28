# 🛠️ Service Development Guide

This guide explains how to create reusable business logic services that handlers can use to implement bot functionality.

## 📋 Service Principles

### 1. Single Responsibility
Each service should focus on one business domain or external integration:
- **Greeting service**: User greeting and personalization
- **Localization service**: Multi-language support and text localization
- **Help service**: Localized help text generation
- **Weather service**: Weather data and formatting  
- **Database service**: Data persistence operations
- **Auth service**: User authentication and authorization

### 2. Stateless Design
Services should be stateless functions when possible:
- Easy to test and reason about
- No hidden dependencies or side effects
- Predictable behavior across calls

### 3. Clear Interfaces
Services provide simple, clear APIs for handlers:
- Handler calls service function
- Service handles all business logic
- Service returns result or raises exception

### 4. Error Handling
Services handle their own errors gracefully:
- Log errors with proper context
- Provide fallback behavior when possible
- Re-raise exceptions for handlers to handle

## 🎨 Service Patterns

### 1. Utility Functions

Pure functions for data transformation:

```python
from aiogram.types import User

def get_username(user: User) -> str:
    """Extract display-friendly username from Telegram user."""
    return user.first_name or user.username or "Anonymous"

def format_user_info(user: User) -> dict:
    """Format user data for display."""
    return {
        "id": user.id,
        "name": get_username(user),
        "username": f"@{user.username}" if user.username else None
    }

def validate_command_args(args: list, min_args: int) -> bool:
    """Validate command has minimum required arguments."""
    return len(args) >= min_args
```

### 2. Singleton Services

Services that maintain state and provide global access:

```python
from typing import Optional
from business.services.localization import LocalizationService

# Global instance pattern (Singleton)
_localization_service: Optional[LocalizationService] = None

def get_localization_service() -> LocalizationService:
    """Get the global localization service instance."""
    global _localization_service
    if _localization_service is None:
        _localization_service = LocalizationService()
    return _localization_service
```

### 3. Async Services

Functions that perform I/O operations:

```python
import aiohttp
from core.utils.logger import get_logger

logger = get_logger()

async def get_weather(city: str) -> str:
    """Get weather information for a city."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://api.weather.com/{city}") as response:
                if response.status == 200:
                    data = await response.json()
                    return format_weather_data(data)
                else:
                    logger.error(f"Weather API error: {response.status}")
                    return "Weather information unavailable"
                    
    except aiohttp.ClientTimeout:
        logger.error(f"Weather API timeout for city: {city}")
        return "Weather service is currently unavailable"
    except Exception as e:
        logger.error(f"Weather API error for {city}: {e}")
        return "Unable to get weather information"

def format_weather_data(data: dict) -> str:
    """Format weather data for user display."""
    return f"🌤️ {data['city']}: {data['temp']}°C, {data['description']}"
```

## 🚀 Core Services Documentation

### 🌍 LocalizationService

**Purpose**: Provides multi-language support with automatic language detection and user preferences.

**Features**:
- JSON-based translations with lazy loading
- Parameter substitution in messages  
- User language preference storage
- Automatic fallback chain
- Caching for performance

**Usage**:
```python
from business.services.localization import t, get_localization_service

# Simple translation (for user-facing messages only)
greeting = t("greetings.hello", user=message.from_user, username="John")

# System logs should use regular logger in English
logger.info(f"User {user.id} requested weather for {city}")

# Direct service access
service = get_localization_service()
supported_langs = service.get_supported_languages()
```

**Important**: System logs, error messages for developers, and internal communications should always use regular Python logger in English. Only user-facing messages should use the localization system.

**Architecture**:
```
LocalizationService
├── _load_language()        # Cached language file loading
├── get_user_language()     # Language detection with fallback
├── set_user_language()     # User preference management
├── get_supported_languages() # Available language enumeration
└── t()                     # Main translation method
```

### 📖 LocalizedHelpService  

**Purpose**: Generates localized help text that respects user language preferences.

**Features**:
- Uses localization keys instead of hardcoded metadata
- Supports category filtering
- Maintains consistent formatting across languages
- Fallback error handling

**Usage**:
```python
from business.services.help_service import generate_localized_help

# Generate full help for user
help_text = generate_localized_help(message.from_user)

# Generate category-specific help
admin_help = generate_localized_help(
    message.from_user, 
    category=HandlerCategory.ADMIN
)
```

**Architecture**:
```
LocalizedHelpService
├── generate_help_text()    # Main help generation
├── get_command_help()      # Individual command help
├── _group_by_category()    # Handler organization
├── _get_category_name()    # Localized category names
└── _format_command_help()  # Command formatting
```

### 👋 GreetingService

**Purpose**: Handles user greeting and personalization logic.

**Usage**:
```python
from business.services.greeting import send_greeting, get_username

# Send localized greeting
await send_greeting(message)

# Extract username
username = get_username(message.from_user)
```

## 📊 Service Integration Patterns

### Handler-Service Integration

**Best Practice**: Keep handlers thin and delegate to services:

```python
@command("weather", description="Get weather information")
async def cmd_weather(message: Message) -> None:
    """Handle /weather command."""
    args = message.text.split()[1:] if message.text else []
    
    if not args:
        error_msg = t("errors.missing_city", user=message.from_user)
        await message.answer(error_msg)
        return
    
    city = " ".join(args)
    
    # System log in English
    logger.info(f"Weather request for {city} by user {message.from_user.id}")
    
    # Delegate to service
    weather_info = await get_weather(city)
    await message.answer(weather_info)
```

### Service Composition

**Pattern**: Services can depend on other services:

```python
class LocalizedHelpService:
    def __init__(self):
        self.registry = get_registry()
        self.localization_service = get_localization_service()  # Dependency
    
    def generate_help_text(self, user: User) -> str:
        # Uses both registry and localization services
        title = self.localization_service.t("commands.help.header", user=user)
        handlers = self.registry.get_all_handlers()
        # ... combine both services
```

### Error Handling in Services

**Pattern**: Consistent error handling across services:

```python
async def robust_service_function(data: str) -> str:
    """Example of robust error handling in services."""
    try:
        # Validate input
        if not data or len(data.strip()) == 0:
            raise ValueError("Input data is required")
        
        # Process data
        result = await external_api_call(data)
        
        # Validate result
        if not result:
            raise ServiceError("No result from external service")
        
        return result
        
    except ValueError as e:
        # Input validation errors - log in English (system log)
        logger.warning(f"Invalid input: {e}")
        return f"Invalid input: {e}"
        
    except ServiceError as e:
        # Expected service errors - log in English (system log)
        logger.warning(f"Service error: {e}")
        return "Service temporarily unavailable"
        
    except Exception as e:
        # Unexpected errors - log with full context in English
        logger.error(f"Unexpected error in service: {e}", exc_info=True)
        return "An unexpected error occurred"
```

## 🎯 Service Best Practices

### 1. **Dependency Injection Ready**
Design services to be easily injectable for testing:

```python
class DatabaseService:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or config.database_url
        self._connection = None
    
    async def connect(self):
        """Connect to database."""
        # Connection logic
        pass
```

### 2. **Configuration Management**
Services should get configuration from central config:

```python
from config import config

class ServiceConfig:
    def __init__(self):
        self.api_key = config.external_api_key
        self.timeout = config.api_timeout
        self.retries = config.api_retries
```

### 3. **Caching and Performance**
Use appropriate caching for expensive operations:

```python
from functools import lru_cache

class LocalizationService:
    @lru_cache(maxsize=32)
    def _load_language(self, language_code: str) -> Dict[str, Any]:
        """Load translations with caching."""
        # Expensive file loading operation
        pass
```

### 4. **Designed for Testing**
Design services to be easily mockable:

```python
# Service interface
from abc import ABC, abstractmethod

class WeatherServiceProtocol(ABC):
    @abstractmethod
    async def get_weather(self, city: str) -> str:
        pass

# Implementation
class WeatherService(WeatherServiceProtocol):
    async def get_weather(self, city: str) -> str:
        # Real implementation
        pass

# Test mock
class MockWeatherService(WeatherServiceProtocol):
    async def get_weather(self, city: str) -> str:
        return "Mock weather data"
```

### 5. **Localization Guidelines**

**Critical Rule**: Only user-facing messages should be localized. System logs, developer messages, and internal communications must be in English.

```python
async def my_service_function(user: User, data: str):
    """Example of proper localization usage."""
    try:
        # System log - ALWAYS in English
        logger.info(f"Processing request from user {user.id} with data length {len(data)}")
        
        result = process_data(data)
        
        # User message - localized
        success_msg = t("messages.processing_complete", user=user, result=result)
        return success_msg
        
    except Exception as e:
        # System log - ALWAYS in English  
        logger.error(f"Service error for user {user.id}: {e}")
        
        # User message - localized
        error_msg = t("errors.service_unavailable", user=user)
        return error_msg
```

**Do not localize:**
- Logger messages (`logger.info`, `logger.error`, etc.)
- Exception messages for developers
- Debug information
- System status messages
- API responses to other services
- Internal configuration or validation messages

**Do localize:**
- Messages shown to end users
- Bot responses to user commands
- Error messages displayed to users
- Help text and command descriptions
- User interface elements

## 🔄 Service Lifecycle

### Initialization
Services are initialized when first accessed via getter functions:

```python
# Lazy initialization pattern
_service_instance = None

def get_service():
    global _service_instance
    if _service_instance is None:
        _service_instance = Service()
    return _service_instance
```

### Cleanup
Services with resources should implement cleanup:

```python
class DatabaseService:
    async def close(self):
        """Close database connections."""
        if self._connection:
            await self._connection.close()
```

This service architecture ensures scalable, maintainable, and testable business logic that follows SOLID principles and integrates seamlessly with the core framework. 