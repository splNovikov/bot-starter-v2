"""
Core handlers framework package.

Provides the handler registry system, type definitions, protocols, and decorators
for building type-safe, metadata-rich Telegram bot handlers.
"""

from .registry import HandlersRegistry, get_registry, set_registry
from .decorators import command, text_handler, message_handler, handler
from .types import HandlerType, HandlerCategory, HandlerMetadata, RegisteredHandler
from .protocols import (
    BaseHandler, CommandHandler, TextHandler, MessageHandler,
    CallbackHandler, InlineHandler, AnyHandler
)

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
    
    # Types and data structures
    'HandlerType',
    'HandlerCategory',
    'HandlerMetadata',
    'RegisteredHandler',
    
    # Protocols
    'BaseHandler',
    'CommandHandler',
    'TextHandler',
    'MessageHandler',
    'CallbackHandler',
    'InlineHandler',
    'AnyHandler'
] 