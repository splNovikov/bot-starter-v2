"""
Decorators for declarative handler registration.
Provides clean, type-safe decorators for registering handlers with metadata.
"""

from typing import Optional, List, Callable, TypeVar

from .protocols import CommandHandler, TextHandler, MessageHandler, CallbackHandler, AnyHandler
from .registry import get_registry
from .types import HandlerType, HandlerCategory, HandlerMetadata
from core.utils.logger import get_logger

# Type variable for preserving function signatures
F = TypeVar('F', bound=Callable)

logger = get_logger()


def command(
    name: str,
    *,
    description: str,
    category: HandlerCategory = HandlerCategory.USER,
    usage: Optional[str] = None,
    aliases: Optional[List[str]] = None,
    examples: Optional[List[str]] = None,
    enabled: bool = True,
    hidden: bool = False,
    admin_only: bool = False,
    tags: Optional[List[str]] = None,
    version: str = "1.0.0",
    author: Optional[str] = None
) -> Callable[[CommandHandler], CommandHandler]:
    """
    Decorator for registering command handlers.
    
    Args:
        name: Command name (without the '/' prefix)
        description: Human-readable description of the command
        category: Handler category for organization
        usage: Usage example (auto-generated if not provided)
        aliases: Alternative command names
        examples: Usage examples
        enabled: Whether the handler is enabled
        hidden: Whether to hide from help
        admin_only: Whether command requires admin privileges
        tags: Tags for categorization
        version: Handler version
        author: Handler author
        
    Returns:
        Decorated handler function
        
    Example:
        @command("greet", description="Send a greeting message")
        async def cmd_greet(message: Message) -> None:
            await send_greeting(message)
    """
    def decorator(func: CommandHandler) -> CommandHandler:
        metadata = HandlerMetadata(
            name=name,
            description=description,
            handler_type=HandlerType.COMMAND,
            category=category,
            command=name,
            aliases=aliases or [],
            usage=usage,
            examples=examples or [],
            enabled=enabled,
            hidden=hidden,
            admin_only=admin_only,
            tags=tags or [],
            version=version,
            author=author
        )
        
        # Register with global registry
        registry = get_registry()
        handler_id = registry.register(func, metadata)
        
        # Add metadata to function for introspection
        func.__handler_metadata__ = metadata  # type: ignore
        func.__handler_id__ = handler_id  # type: ignore
        
        logger.debug(f"Registered command handler: /{name}")
        return func
    
    return decorator


def callback_query(
    name: str,
    *,
    description: str,
    category: HandlerCategory = HandlerCategory.USER,
    enabled: bool = True,
    hidden: bool = False,
    admin_only: bool = False,
    tags: Optional[List[str]] = None,
    version: str = "1.0.0",
    author: Optional[str] = None
) -> Callable[[CallbackHandler], CallbackHandler]:
    """
    Decorator for registering callback query handlers.
    
    Args:
        name: Handler name
        description: Human-readable description
        category: Handler category
        enabled: Whether the handler is enabled
        hidden: Whether to hide from help
        admin_only: Whether handler requires admin privileges
        tags: Tags for categorization
        version: Handler version
        author: Handler author
        
    Returns:
        Decorated handler function
        
    Example:
        @callback_query("locale_change", description="Handle locale change")
        async def handle_locale_change(callback: CallbackQuery) -> None:
            await process_locale_change(callback)
    """
    def decorator(func: CallbackHandler) -> CallbackHandler:
        metadata = HandlerMetadata(
            name=name,
            description=description,
            handler_type=HandlerType.CALLBACK,
            category=category,
            enabled=enabled,
            hidden=hidden,
            admin_only=admin_only,
            tags=tags or [],
            version=version,
            author=author
        )
        
        # Register with global registry
        registry = get_registry()
        handler_id = registry.register(func, metadata)
        
        # Add metadata to function for introspection
        func.__handler_metadata__ = metadata  # type: ignore
        func.__handler_id__ = handler_id  # type: ignore
        
        logger.debug(f"Registered callback query handler: {name}")
        return func
    
    return decorator


def text_handler(
    name: str,
    *,
    description: str,
    category: HandlerCategory = HandlerCategory.USER,
    enabled: bool = True,
    hidden: bool = False,
    admin_only: bool = False,
    tags: Optional[List[str]] = None,
    version: str = "1.0.0",
    author: Optional[str] = None
) -> Callable[[TextHandler], TextHandler]:
    """
    Decorator for registering text message handlers.
    
    Args:
        name: Handler name
        description: Human-readable description
        category: Handler category
        enabled: Whether the handler is enabled
        hidden: Whether to hide from help
        admin_only: Whether handler requires admin privileges
        tags: Tags for categorization
        version: Handler version
        author: Handler author
        
    Returns:
        Decorated handler function
        
    Example:
        @text_handler("echo", description="Echo user messages")
        async def handle_echo(message: Message) -> None:
            await message.answer(message.text)
    """
    def decorator(func: TextHandler) -> TextHandler:
        metadata = HandlerMetadata(
            name=name,
            description=description,
            handler_type=HandlerType.TEXT,
            category=category,
            enabled=enabled,
            hidden=hidden,
            admin_only=admin_only,
            tags=tags or [],
            version=version,
            author=author
        )
        
        # Register with global registry
        registry = get_registry()
        handler_id = registry.register(func, metadata)
        
        # Add metadata to function for introspection
        func.__handler_metadata__ = metadata  # type: ignore
        func.__handler_id__ = handler_id  # type: ignore
        
        logger.debug(f"Registered text handler: {name}")
        return func
    
    return decorator


def message_handler(
    name: str,
    *,
    description: str,
    category: HandlerCategory = HandlerCategory.USER,
    enabled: bool = True,
    hidden: bool = False,
    admin_only: bool = False,
    tags: Optional[List[str]] = None,
    version: str = "1.0.0",
    author: Optional[str] = None
) -> Callable[[MessageHandler], MessageHandler]:
    """
    Decorator for registering general message handlers.
    
    Args:
        name: Handler name
        description: Human-readable description
        category: Handler category
        enabled: Whether the handler is enabled
        hidden: Whether to hide from help
        admin_only: Whether handler requires admin privileges
        tags: Tags for categorization
        version: Handler version
        author: Handler author
        
    Returns:
        Decorated handler function
        
    Example:
        @message_handler("media", description="Handle media messages")
        async def handle_media(message: Message) -> None:
            await message.answer("Nice media!")
    """
    def decorator(func: MessageHandler) -> MessageHandler:
        metadata = HandlerMetadata(
            name=name,
            description=description,
            handler_type=HandlerType.MESSAGE,
            category=category,
            enabled=enabled,
            hidden=hidden,
            admin_only=admin_only,
            tags=tags or [],
            version=version,
            author=author
        )
        
        # Register with global registry
        registry = get_registry()
        handler_id = registry.register(func, metadata)
        
        # Add metadata to function for introspection
        func.__handler_metadata__ = metadata  # type: ignore
        func.__handler_id__ = handler_id  # type: ignore
        
        logger.debug(f"Registered message handler: {name}")
        return func
    
    return decorator


def handler(
    name: str,
    handler_type: HandlerType,
    *,
    description: str,
    category: HandlerCategory = HandlerCategory.USER,
    command: Optional[str] = None,
    aliases: Optional[List[str]] = None,
    usage: Optional[str] = None,
    examples: Optional[List[str]] = None,
    enabled: bool = True,
    hidden: bool = False,
    admin_only: bool = False,
    tags: Optional[List[str]] = None,
    version: str = "1.0.0",
    author: Optional[str] = None
) -> Callable[[AnyHandler], AnyHandler]:
    """
    Generic decorator for registering any type of handler.
    
    This is a more flexible decorator that can handle any handler type.
    For common cases, prefer the specific decorators like @command, @text_handler, etc.
    
    Args:
        name: Handler name
        handler_type: Type of handler
        description: Human-readable description
        category: Handler category
        command: Command name (for command handlers)
        aliases: Alternative command names
        usage: Usage example
        examples: Usage examples
        enabled: Whether the handler is enabled
        hidden: Whether to hide from help
        admin_only: Whether handler requires admin privileges
        tags: Tags for categorization
        version: Handler version
        author: Handler author
        
    Returns:
        Decorated handler function
    """
    def decorator(func: AnyHandler) -> AnyHandler:
        metadata = HandlerMetadata(
            name=name,
            description=description,
            handler_type=handler_type,
            category=category,
            command=command,
            aliases=aliases or [],
            usage=usage,
            examples=examples or [],
            enabled=enabled,
            hidden=hidden,
            admin_only=admin_only,
            tags=tags or [],
            version=version,
            author=author
        )
        
        # Register with global registry
        registry = get_registry()
        handler_id = registry.register(func, metadata)
        
        # Add metadata to function for introspection
        func.__handler_metadata__ = metadata  # type: ignore
        func.__handler_id__ = handler_id  # type: ignore
        
        logger.debug(f"Registered {handler_type.value} handler: {name}")
        return func
    
    return decorator


# Convenience functions for handler introspection
def get_handler_metadata(func: Callable) -> Optional[HandlerMetadata]:
    """Get metadata from a decorated handler function."""
    return getattr(func, '__handler_metadata__', None)


def get_handler_id(func: Callable) -> Optional[str]:
    """Get handler ID from a decorated handler function.""" 
    return getattr(func, '__handler_id__', None)


def is_registered_handler(func: Callable) -> bool:
    """Check if a function is a registered handler."""
    return hasattr(func, '__handler_metadata__') and hasattr(func, '__handler_id__') 