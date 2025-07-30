"""
Application layer initialization.

This module provides the application layer for the Telegram bot,
containing essential handlers and services for user interactions.

The application layer follows clean architecture principles with:
- Handlers: Command and message handlers (/start)
- Services: Core application logic (greeting functionality)

This structure maintains separation of concerns and supports future scalability.
"""

# Import essential components for external access
from .handlers import user_router, initialize_registry
from .handlers.start import send_greeting, get_username, create_greeting_message

__all__ = [
    # Router and registry management
    'user_router',
    'initialize_registry',
    
    # Greeting services  
    'send_greeting',
    'get_username',
    'create_greeting_message',
] 