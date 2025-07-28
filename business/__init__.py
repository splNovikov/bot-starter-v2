"""
Business logic package for the Telegram bot.

Contains application-specific business logic and handlers.
See business/docs/README.md for comprehensive documentation.
"""

from .handlers import user_router, initialize_registry
from .services import send_greeting, get_username, create_greeting_message

# Initialize the registry system when business layer is imported
initialize_registry()

__version__ = "1.0.0"

__all__ = [
    # Handlers
    'user_router',
    
    # Services
    'send_greeting',
    'get_username', 
    'create_greeting_message'
] 