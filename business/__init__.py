"""
Business layer initialization.

This module provides the business logic layer for the Telegram bot,
containing essential handlers and services for user interactions.

The business layer follows clean architecture principles with:
- Handlers: Command and message handlers (/start)
- Services: Core business logic (greeting functionality)

This structure maintains separation of concerns and supports future scalability.
"""

# Import essential components for external access
from .handlers import user_router, initialize_registry
from .services import send_greeting, get_username, create_greeting_message

__all__ = [
    # Router and registry management
    'user_router',
    'initialize_registry',
    
    # Greeting services  
    'send_greeting',
    'get_username',
    'create_greeting_message',
] 