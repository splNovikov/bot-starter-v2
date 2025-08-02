"""
Core handlers framework package.

Provides the handler registry system, type definitions, protocols, and decorators
for building type-safe, metadata-rich Telegram bot handlers.
"""

from .decorators import command, handler, message_handler, text_handler
from .protocols import (
    AnyHandler,
    BaseHandler,
    CallbackHandler,
    CommandHandler,
    InlineHandler,
    MessageHandler,
    TextHandler,
)
from .registry import HandlersRegistry, get_registry, set_registry
from .types import HandlerCategory, HandlerMetadata, HandlerType, RegisteredHandler

__all__ = [
    # Registry system
    "HandlersRegistry",
    "get_registry",
    "set_registry",
    # Decorators
    "command",
    "text_handler",
    "message_handler",
    "handler",
    # Types and data structures
    "HandlerType",
    "HandlerCategory",
    "HandlerMetadata",
    "RegisteredHandler",
    # Protocols
    "BaseHandler",
    "CommandHandler",
    "TextHandler",
    "MessageHandler",
    "CallbackHandler",
    "InlineHandler",
    "AnyHandler",
]
