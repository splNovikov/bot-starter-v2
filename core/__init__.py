"""
Core framework package for the Telegram bot.

This package contains reusable framework components:
- Handler registry system
- Type definitions and protocols  
- Decorators for handler registration
- Middleware infrastructure
- Core utilities (logging)
"""

# Export core framework components
from .handlers import (
    HandlersRegistry, get_registry, set_registry,
    command, text_handler, message_handler, handler,
    HandlerType, HandlerCategory, HandlerMetadata
)
from .middleware import LoggingMiddleware
from .utils import get_logger, setup_logger

__version__ = "1.0.0"

__all__ = [
    # Registry system
    'HandlersRegistry',
    'get_registry', 
    'set_registry',
    
    # Decorators
    'command',
    'text_handler',
    'message_handler', 
    'handler',
    
    # Types and enums
    'HandlerType',
    'HandlerCategory',
    'HandlerMetadata',
    
    # Middleware
    'LoggingMiddleware',
    
    # Utilities
    'get_logger',
    'setup_logger'
] 