"""
Business services initialization.

This module provides centralized access to business-layer services.
Currently focused on the essential greeting functionality for user interactions.
"""

# Core services
from .greeting import send_greeting, get_username, create_greeting_message

__all__ = [
    # Greeting services for /start handler
    'send_greeting',
    'get_username', 
    'create_greeting_message',
] 