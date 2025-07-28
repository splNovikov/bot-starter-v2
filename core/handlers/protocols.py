"""
Protocol definitions for type-safe handler interfaces.
Defines the contracts that all handlers must implement.
"""

from typing import Protocol, Awaitable, Optional, Any, runtime_checkable
from aiogram.types import Message, CallbackQuery, InlineQuery


@runtime_checkable
class BaseHandler(Protocol):
    """Base protocol for all handlers."""
    
    async def __call__(self, *args: Any, **kwargs: Any) -> Optional[Any]:
        """Handle the incoming update."""
        ...


@runtime_checkable  
class CommandHandler(Protocol):
    """Protocol for command handlers (e.g., /start, /help)."""
    
    async def __call__(self, message: Message) -> None:
        """
        Handle a command message.
        
        Args:
            message: The incoming message containing the command
        """
        ...


@runtime_checkable
class TextHandler(Protocol):
    """Protocol for text message handlers."""
    
    async def __call__(self, message: Message) -> None:
        """
        Handle a text message.
        
        Args:
            message: The incoming text message
        """
        ...


@runtime_checkable
class MessageHandler(Protocol):
    """Protocol for general message handlers (photos, documents, etc.)."""
    
    async def __call__(self, message: Message) -> None:
        """
        Handle any type of message.
        
        Args:
            message: The incoming message of any type
        """
        ...


@runtime_checkable
class CallbackHandler(Protocol):
    """Protocol for callback query handlers."""
    
    async def __call__(self, callback: CallbackQuery) -> None:
        """
        Handle a callback query from inline keyboards.
        
        Args:
            callback: The incoming callback query
        """
        ...


@runtime_checkable
class InlineHandler(Protocol):
    """Protocol for inline query handlers."""
    
    async def __call__(self, inline_query: InlineQuery) -> None:
        """
        Handle an inline query.
        
        Args:
            inline_query: The incoming inline query
        """
        ...


# Union type for all possible handler types
AnyHandler = CommandHandler | TextHandler | MessageHandler | CallbackHandler | InlineHandler


def validate_handler_signature(handler: Any, expected_protocol: type[BaseHandler]) -> bool:
    """
    Validate that a handler function conforms to the expected protocol.
    
    Args:
        handler: The handler function to validate
        expected_protocol: The protocol the handler should implement
        
    Returns:
        bool: True if the handler is valid, False otherwise
    """
    try:
        return isinstance(handler, expected_protocol)
    except TypeError:
        # In case of complex type checking issues
        return hasattr(handler, '__call__')


def get_handler_protocol(handler_type_name: str) -> Optional[type[BaseHandler]]:
    """
    Get the appropriate protocol class for a handler type.
    
    Args:
        handler_type_name: The name of the handler type
        
    Returns:
        The corresponding protocol class or None if not found
    """
    protocol_map = {
        'command': CommandHandler,
        'text': TextHandler, 
        'message': MessageHandler,
        'callback': CallbackHandler,
        'inline': InlineHandler,
    }
    
    return protocol_map.get(handler_type_name.lower()) 