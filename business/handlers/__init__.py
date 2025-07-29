"""
Business handlers package.

Contains application-specific handler implementations for user interactions.
Currently focused on the essential /start command handler with clean architecture.
"""

from .user_handlers import user_router, initialize_registry

__all__ = [
    'user_router',
    'initialize_registry'
] 