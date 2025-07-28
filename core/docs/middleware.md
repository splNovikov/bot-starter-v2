# 🛡️ Middleware System

The core framework provides infrastructure middleware components for cross-cutting concerns like logging, monitoring, and request processing.

## 📋 Overview

Middleware in the core framework handles:
- **Logging**: Structured logging of requests and responses
- **Error Handling**: Centralized error tracking and reporting
- **Performance Monitoring**: Response time and throughput metrics
- **Request Tracking**: User activity and interaction patterns

## 🔍 LoggingMiddleware

The `LoggingMiddleware` provides comprehensive logging for all bot interactions.

### Features

- **Event Type Detection**: Automatically identifies message types (text, photo, command, etc.)
- **User Information**: Extracts and logs user details for analytics
- **Error Tracking**: Captures and logs exceptions with full context
- **Performance Metrics**: Tracks processing time for performance monitoring
- **Structured Logging**: Uses consistent format for easy parsing and analysis

### Usage

```python
from core.middleware import LoggingMiddleware

# In main.py or bot setup
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())
```

### Implementation Details

The middleware handles different aiogram v3 event types directly:

```python
class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            # Get event type and user info
            event_type = self._get_event_type(event)
            user_info = self._get_user_info(event)
            
            logger.info(
                f"Processing {event_type} from user {user_info['username']} "
                f"(ID: {user_info['user_id']}, Chat: {user_info['chat_id']})"
            )
            
            # Call next handler with timing
            result = await handler(event, data)
            
            logger.debug(f"Successfully processed {event_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing {event_type}: {e}", exc_info=True)
            raise
```

### Event Type Detection

Automatically detects different types of Telegram events:

```python
def _get_event_type(self, event: TelegramObject) -> str:
    """Get the type of the event."""
    if isinstance(event, Message):
        return "message"
    elif isinstance(event, CallbackQuery):
        return "callback_query"
    elif isinstance(event, InlineQuery):
        return "inline_query"
    else:
        return event.__class__.__name__.lower()
```

### User Information Extraction

Safely extracts user information from different event types:

```python
def _get_user_info(self, event: TelegramObject) -> Dict[str, Any]:
    """Extract user information from the event."""
    user = None
    chat_id = None
    
    if isinstance(event, Message):
        user = event.from_user
        chat_id = event.chat.id
    elif isinstance(event, CallbackQuery):
        user = event.from_user
        chat_id = event.message.chat.id if event.message else None
    elif isinstance(event, InlineQuery):
        user = event.from_user
        chat_id = None  # Inline queries don't have chat context
    
    return {
        "user_id": user.id if user else None,
        "username": user.first_name or user.username if user else "Unknown",
        "chat_id": chat_id
    }
```

### Log Output Examples

**Successful Request:**
```
2024-01-01 12:00:00 | INFO | Processing message from user John (ID: 123456, Chat: 789012)
2024-01-01 12:00:00 | DEBUG | Successfully processed message
```

**Error Handling:**
```
2024-01-01 12:00:00 | INFO | Processing message from user John (ID: 123456, Chat: 789012)
2024-01-01 12:00:00 | ERROR | Error processing message: Service temporarily unavailable
Traceback (most recent call last):
  File "middleware.py", line 45, in __call__
    result = await handler(event, data)
  ...
```

## 🚀 Creating Custom Middleware

### Middleware Pattern

```python
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

class CustomMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Pre-processing
        # Modify event or data if needed
        
        # Call next handler
        result = await handler(event, data)
        
        # Post-processing
        # Modify result or perform cleanup
        
        return result
```

### Example: Rate Limiting Middleware

```python
import time
from collections import defaultdict
from core.utils.logger import get_logger

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests = defaultdict(list)
        self.logger = get_logger()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Extract user ID
        user_id = None
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        
        if user_id and self._is_rate_limited(user_id):
            self.logger.warning(f"Rate limit exceeded for user {user_id}")
            # Could send rate limit message or just drop request
            return None
        
        return await handler(event, data)
    
    def _is_rate_limited(self, user_id: int) -> bool:
        """Check if user has exceeded rate limit."""
        current_time = time.time()
        user_requests = self.user_requests[user_id]
        
        # Remove old requests outside window
        user_requests[:] = [
            req_time for req_time in user_requests
            if current_time - req_time < self.window_seconds
        ]
        
        # Check if limit exceeded
        if len(user_requests) >= self.max_requests:
            return True
        
        # Add current request
        user_requests.append(current_time)
        return False
```

### Example: Authentication Middleware

```python
class AuthMiddleware(BaseMiddleware):
    def __init__(self, admin_users: set[int]):
        self.admin_users = admin_users
        self.logger = get_logger()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Add user authentication info to data
        user_id = None
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        
        data['is_admin'] = user_id in self.admin_users if user_id else False
        data['user_id'] = user_id
        
        return await handler(event, data)
```

## 🔧 Middleware Registration

### Order Matters

Middleware is executed in registration order for requests and reverse order for responses:

```python
# Registration order
dp.message.middleware(LoggingMiddleware())      # Runs first
dp.message.middleware(AuthMiddleware())         # Runs second  
dp.message.middleware(RateLimitMiddleware())    # Runs third

# Execution order:
# Request: Logging -> Auth -> RateLimit -> Handler
# Response: Handler -> RateLimit -> Auth -> Logging
```

### Router-Specific Middleware

```python
# Apply to all message types
dp.message.middleware(LoggingMiddleware())

# Apply to specific routers
user_router.message.middleware(UserMiddleware())
admin_router.message.middleware(AdminMiddleware())
```

## 📊 Integration with Handler Registry

The middleware system works seamlessly with the handler registry:

```python
# Middleware processes the event
# Registry statistics are collected automatically
# Handler is called with proper context

# Example of data flow:
# 1. LoggingMiddleware logs request
# 2. AuthMiddleware adds user info
# 3. Registry wrapper tracks statistics
# 4. Handler processes request
# 5. Registry wrapper updates timing
# 6. AuthMiddleware can modify response
# 7. LoggingMiddleware logs result
```

## 🎯 Best Practices

### Middleware Design
- Keep middleware **focused** on single concerns
- Make middleware **stateless** when possible
- Handle **errors gracefully** without breaking the chain
- Use **proper logging** for debugging and monitoring

### Performance
- Minimize **processing time** in middleware
- Use **async/await** properly for I/O operations
- Consider **caching** for expensive operations
- **Profile** middleware performance impact

### Error Handling
- **Never let middleware crash** the entire request
- **Log errors** with proper context
- **Provide fallbacks** when possible
- **Re-raise critical errors** that handlers should handle

### Testing
- **Mock external dependencies** (databases, APIs)
- **Test middleware in isolation** before integration
- **Test error conditions** and edge cases
- **Measure performance impact** of middleware

The middleware system provides a powerful way to implement cross-cutting concerns while maintaining clean separation between infrastructure and business logic. 