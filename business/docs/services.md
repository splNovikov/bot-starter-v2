# 🛠️ Service Development Guide

This guide explains how to create reusable business logic services that handlers can use to implement bot functionality.

## 📋 Service Principles

### 1. Single Responsibility
Each service should focus on one business domain or external integration:
- **Greeting service**: User greeting and personalization
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

### 2. Async Services

Functions that perform I/O operations:

```python
import aiohttp
from core.utils.logger import get_logger

logger = get_logger()

async def get_weather(city: str) -> str:
    """Get weather information for a city."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.weather.com/v1/current?city={city}"
            headers = {"API-Key": "your-api-key"}
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return format_weather_response(data)
                elif response.status == 404:
                    return f"Weather data not available for {city}"
                else:
                    return "Weather service temporarily unavailable"
                    
    except asyncio.TimeoutError:
        logger.error(f"Weather API timeout for city: {city}")
        return "Weather service is taking too long to respond"
    except Exception as e:
        logger.error(f"Weather API error for {city}: {e}")
        return "Sorry, couldn't get weather information"

def format_weather_response(data: dict) -> str:
    """Format weather API response for user display."""
    city = data.get('name', 'Unknown')
    temp = data.get('main', {}).get('temp', 'N/A')
    description = data.get('weather', [{}])[0].get('description', 'N/A')
    
    return f"🌤️ Weather in {city}:\n{temp}°C, {description.title()}"
```

### 3. Service Classes

For stateful services with multiple methods:

```python
from typing import Dict, Optional
import asyncio

class DatabaseService:
    """Handle database operations for user data."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._connection = None
        self.logger = get_logger()
    
    async def connect(self) -> None:
        """Establish database connection."""
        try:
            # Database connection logic
            self._connection = await create_connection(self.connection_string)
            self.logger.info("Database connection established")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    async def save_user_preference(self, user_id: int, key: str, value: str) -> bool:
        """Save user preference to database."""
        try:
            if not self._connection:
                await self.connect()
            
            query = "INSERT OR REPLACE INTO user_preferences (user_id, key, value) VALUES (?, ?, ?)"
            await self._connection.execute(query, (user_id, key, value))
            await self._connection.commit()
            
            self.logger.info(f"Saved preference for user {user_id}: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving preference: {e}")
            return False
    
    async def get_user_preferences(self, user_id: int) -> Dict[str, str]:
        """Get all preferences for a user."""
        try:
            if not self._connection:
                await self.connect()
            
            query = "SELECT key, value FROM user_preferences WHERE user_id = ?"
            cursor = await self._connection.execute(query, (user_id,))
            rows = await cursor.fetchall()
            
            return {row[0]: row[1] for row in rows}
            
        except Exception as e:
            self.logger.error(f"Error getting preferences: {e}")
            return {}
    
    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self.logger.info("Database connection closed")

# Usage
db_service = DatabaseService("sqlite:///bot.db")
```

## 🚀 Step-by-Step: Creating a New Service

### Example: Creating a Translation Service

```python
# 1. Create business/services/translation.py

import aiohttp
from typing import Optional
from core.utils.logger import get_logger

logger = get_logger()

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish', 
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese'
}

async def translate_text(text: str, target_lang: str, source_lang: str = 'auto') -> str:
    """
    Translate text to target language.
    
    Args:
        text: Text to translate
        target_lang: Target language code (e.g., 'en', 'es')
        source_lang: Source language code (default: 'auto')
    
    Returns:
        Translated text or error message
    """
    try:
        # Validate target language
        if target_lang not in SUPPORTED_LANGUAGES:
            return f"Unsupported language: {target_lang}\nSupported: {', '.join(SUPPORTED_LANGUAGES.keys())}"
        
        # Validate text length
        if len(text) > 5000:
            return "Text too long (max 5000 characters)"
        
        # Call translation API
        translated = await _call_translation_api(text, source_lang, target_lang)
        
        if translated:
            return f"🌐 Translation ({SUPPORTED_LANGUAGES[target_lang]}):\n{translated}"
        else:
            return "Translation failed. Please try again."
            
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return "Translation service temporarily unavailable"

async def _call_translation_api(text: str, source: str, target: str) -> Optional[str]:
    """Call external translation API."""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.translate.service.com/v1/translate"
            data = {
                'text': text,
                'source': source,
                'target': target
            }
            headers = {'Authorization': 'Bearer YOUR_API_KEY'}
            
            async with session.post(url, json=data, headers=headers, timeout=15) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('translated_text')
                return None
                
    except Exception as e:
        logger.error(f"Translation API error: {e}")
        return None

def get_supported_languages() -> str:
    """Get formatted list of supported languages."""
    lang_list = [f"{code} - {name}" for code, name in SUPPORTED_LANGUAGES.items()]
    return "🌐 Supported languages:\n" + "\n".join(lang_list)

# 2. Export in business/services/__init__.py
from .translation import translate_text, get_supported_languages

__all__.extend([
    'translate_text',
    'get_supported_languages'
])

# 3. Create handler in business/handlers/user_handlers.py
@command(
    "translate",
    description="Translate text to another language",
    category=HandlerCategory.UTILITY,
    usage="/translate <language> <text>",
    examples=[
        "/translate es Hello world",
        "/translate fr Good morning"
    ]
)
async def cmd_translate(message: Message) -> None:
    """Handle /translate command."""
    args = message.text.split(maxsplit=2)[1:] if message.text else []
    
    if len(args) < 2:
        languages = get_supported_languages()
        await message.answer(
            f"Usage: /translate <language> <text>\n\n{languages}"
        )
        return
    
    target_lang = args[0].lower()
    text_to_translate = args[1]
    
    result = await translate_text(text_to_translate, target_lang)
    await message.answer(result)
```

## 🎯 Service Best Practices

### 1. Error Handling

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
        # Input validation errors - don't log as errors
        logger.warning(f"Invalid input: {e}")
        return f"Invalid input: {e}"
        
    except ServiceError as e:
        # Expected service errors
        logger.warning(f"Service error: {e}")
        return "Service temporarily unavailable"
        
    except Exception as e:
        # Unexpected errors - log with full context
        logger.error(f"Unexpected error in service: {e}", exc_info=True)
        return "An unexpected error occurred"
```

### 2. Input Validation

```python
def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input for safe processing."""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    import re
    text = re.sub(r'[<>"\']', '', text)
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text.strip()
```

### 3. Async Best Practices

```python
import asyncio
from typing import List

async def process_multiple_items(items: List[str]) -> List[str]:
    """Process multiple items concurrently."""
    # Process items concurrently for better performance
    tasks = [process_single_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle results and exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Error processing item {i}: {result}")
            processed_results.append(f"Error processing item {i}")
        else:
            processed_results.append(result)
    
    return processed_results

async def process_with_retry(data: str, max_retries: int = 3) -> str:
    """Process data with retry logic."""
    for attempt in range(max_retries):
        try:
            return await external_service_call(data)
        except TemporaryError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
            await asyncio.sleep(wait_time)
```

### 4. Configuration and Environment

```python
import os
from typing import Optional

class ServiceConfig:
    """Configuration for external services."""
    
    API_KEY: Optional[str] = os.getenv('WEATHER_API_KEY')
    BASE_URL: str = os.getenv('WEATHER_BASE_URL', 'https://api.weather.com')
    TIMEOUT: int = int(os.getenv('API_TIMEOUT', '10'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.API_KEY:
            raise ValueError("WEATHER_API_KEY environment variable is required")

# Use in service
async def get_weather_with_config(city: str) -> str:
    """Get weather using configuration."""
    ServiceConfig.validate()
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=ServiceConfig.TIMEOUT)) as session:
            url = f"{ServiceConfig.BASE_URL}/current"
            headers = {"API-Key": ServiceConfig.API_KEY}
            params = {"city": city}
            
            async with session.get(url, headers=headers, params=params) as response:
                # Process response
                pass
    except Exception as e:
        logger.error(f"Weather service error: {e}")
        raise
```

## 🧪 Testing Services

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock, patch
from business.services.weather import get_weather

@pytest.mark.asyncio
async def test_get_weather_success():
    """Test successful weather API call."""
    mock_response_data = {
        'name': 'London',
        'main': {'temp': 20},
        'weather': [{'description': 'sunny'}]
    }
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = mock_response_data
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await get_weather("London")
        
        assert "London" in result
        assert "20°C" in result
        assert "Sunny" in result

@pytest.mark.asyncio
async def test_get_weather_api_error():
    """Test weather API error handling."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 500
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await get_weather("London")
        
        assert "unavailable" in result.lower()

@pytest.mark.asyncio 
async def test_get_weather_timeout():
    """Test weather API timeout handling."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.side_effect = asyncio.TimeoutError()
        
        result = await get_weather("London")
        
        assert "taking too long" in result.lower()
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_weather_service_integration():
    """Test weather service with handler integration."""
    from business.handlers.user_handlers import cmd_weather
    from unittest.mock import MagicMock, AsyncMock
    
    # Mock message
    message = MagicMock()
    message.text = "/weather London"
    message.answer = AsyncMock()
    
    # Mock service to return known result
    with patch('business.services.weather.get_weather') as mock_service:
        mock_service.return_value = "London: 20°C, Sunny"
        
        await cmd_weather(message)
        
        mock_service.assert_called_once_with("London")
        message.answer.assert_called_once_with("London: 20°C, Sunny")
```

## 📁 Service Organization

### File Structure

```python
business/services/
├── __init__.py           # Export all services
├── greeting.py           # User greeting logic
├── weather.py            # Weather API integration
├── translation.py        # Translation services
├── database.py           # Data persistence
├── auth.py              # Authentication/authorization
├── notifications.py      # External notifications
└── utils.py             # Shared service utilities
```

### Service Dependencies

```python
# services/utils.py - Shared utilities
async def make_api_request(url: str, headers: dict = None, timeout: int = 10) -> dict:
    """Common API request utility."""
    # Shared HTTP client logic

def format_error_message(error: Exception, context: str) -> str:
    """Format error messages consistently."""
    # Common error formatting

# Use in other services
from .utils import make_api_request, format_error_message

async def some_service_function():
    try:
        data = await make_api_request("https://api.example.com/data")
        return process_data(data)
    except Exception as e:
        error_msg = format_error_message(e, "some_service_function")
        logger.error(error_msg)
        raise
```

## 🔄 Service Lifecycle

### Initialization

```python
# business/services/__init__.py
from .greeting import send_greeting, get_username, create_greeting_message
from .weather import get_weather
from .database import DatabaseService

# Initialize stateful services
db_service = DatabaseService("sqlite:///bot.db")

# Export functions and instances
__all__ = [
    # Greeting services
    'send_greeting',
    'get_username', 
    'create_greeting_message',
    
    # Weather services
    'get_weather',
    
    # Database service
    'db_service'
]
```

### Cleanup

```python
# In main.py or application shutdown
async def cleanup_services():
    """Clean up service resources."""
    from business.services import db_service
    
    await db_service.close()
    logger.info("Services cleaned up")
```

## 📚 Next Steps

1. **Study existing service** in `business/services/greeting.py`
2. **Start with simple utility functions** before complex services
3. **Create comprehensive tests** for all service functions
4. **Use proper error handling** and logging throughout
5. **Export services properly** in package `__init__.py` files

Services provide the business logic foundation that makes handlers thin and maintainable while keeping complex operations properly organized and testable. 