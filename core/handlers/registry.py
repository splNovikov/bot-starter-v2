"""
Central registry system for managing bot handlers.
Provides type-safe handler registration, metadata management, and introspection.
"""

import time
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from functools import wraps

from aiogram import Router

from .types import (
    HandlerType, HandlerCategory, HandlerMetadata, HandlerStats, 
    RegisteredHandler, HandlerRegistry
)
from .protocols import (
    BaseHandler, AnyHandler, validate_handler_signature, get_handler_protocol
)
from core.utils.logger import get_logger


class HandlersRegistry:
    """
    Central registry for managing bot handlers with type safety and metadata.
    
    Provides handler registration, validation, introspection, and help generation.
    """
    
    def __init__(self, router: Optional[Router] = None):
        """
        Initialize the handlers registry.
        
        Args:
            router: Optional aiogram router to register handlers with
        """
        self._handlers: HandlerRegistry = {}
        self._commands: Dict[str, str] = {}  # command -> handler_id mapping
        self._categories: Dict[HandlerCategory, List[str]] = defaultdict(list)
        self._router = router
        self._logger = get_logger()
        
    def register(
        self,
        handler_func: AnyHandler,
        metadata: HandlerMetadata,
        auto_register_router: bool = True
    ) -> str:
        """
        Register a handler with the registry.
        
        Args:
            handler_func: The handler function
            metadata: Handler metadata
            auto_register_router: Whether to automatically register with aiogram router
            
        Returns:
            str: The handler identifier
            
        Raises:
            ValueError: If handler validation fails
            RuntimeError: If handler is already registered
        """
        # Validate handler signature
        expected_protocol = get_handler_protocol(metadata.handler_type.value)
        if expected_protocol and not validate_handler_signature(handler_func, expected_protocol):
            raise ValueError(
                f"Handler {metadata.name} does not conform to {expected_protocol.__name__} protocol"
            )
        
        # Create registered handler
        registered_handler = RegisteredHandler(
            function=handler_func,
            metadata=metadata,
            stats=HandlerStats()
        )
        
        handler_id = registered_handler.identifier
        
        # Check for duplicates
        if handler_id in self._handlers:
            raise RuntimeError(f"Handler with id '{handler_id}' is already registered")
        
        # Store handler
        self._handlers[handler_id] = registered_handler
        
        # Update command mapping
        if metadata.command:
            self._commands[metadata.command] = handler_id
            # Also register aliases
            for alias in metadata.aliases:
                self._commands[alias] = handler_id
        
        # Update category mapping
        self._categories[metadata.category].append(handler_id)
        
        # Auto-register with aiogram router if enabled
        if auto_register_router and self._router:
            self._register_with_router(registered_handler)
            
        self._logger.info(f"Registered handler: {handler_id} ({metadata.handler_type.value})")
        return handler_id
    
    def _register_with_router(self, handler: RegisteredHandler) -> None:
        """Register handler with aiogram router."""
        if not self._router:
            return
            
        metadata = handler.metadata
        wrapped_func = self._wrap_handler_with_stats(handler)
        
        if metadata.handler_type == HandlerType.COMMAND:
            from aiogram.filters import Command
            
            # Register main command
            self._router.message.register(wrapped_func, Command(metadata.command))
            
            # Register all aliases as separate command handlers
            for alias in metadata.aliases:
                self._router.message.register(wrapped_func, Command(alias))
            
        elif metadata.handler_type == HandlerType.TEXT:
            from aiogram import F
            self._router.message.register(wrapped_func, F.text)
            
        elif metadata.handler_type == HandlerType.MESSAGE:
            self._router.message.register(wrapped_func)
            
        elif metadata.handler_type == HandlerType.CALLBACK:
            # For callback queries, we need to register them manually
            # since they require specific filters that can't be determined from metadata alone
            # The callback query handler will be registered directly with the router
            pass
            
        # Add more handler types as needed
        
    def _wrap_handler_with_stats(self, handler: RegisteredHandler) -> Callable:
        """Wrap handler function with statistics tracking."""
        @wraps(handler.function)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            handler.stats.calls += 1
            
            try:
                result = await handler.function(*args, **kwargs)
                
                # Update timing stats
                duration = time.time() - start_time
                handler.stats.avg_response_time = (
                    (handler.stats.avg_response_time * (handler.stats.calls - 1) + duration) 
                    / handler.stats.calls
                )
                handler.stats.last_called = time.time()
                
                return result
                
            except Exception as e:
                handler.stats.errors += 1
                self._logger.error(f"Error in handler {handler.identifier}: {e}")
                raise
                
        return wrapper
    
    def get_handler(self, identifier: str) -> Optional[RegisteredHandler]:
        """Get a registered handler by identifier."""
        return self._handlers.get(identifier)
    
    def get_handler_by_command(self, command: str) -> Optional[RegisteredHandler]:
        """Get a handler by command name."""
        handler_id = self._commands.get(command)
        return self._handlers.get(handler_id) if handler_id else None
    
    def get_all_handlers(self) -> List[RegisteredHandler]:
        """Get all registered handlers."""
        return list(self._handlers.values())
    
    def get_handlers_by_category(self, category: HandlerCategory) -> List[RegisteredHandler]:
        """Get all handlers in a specific category."""
        handler_ids = self._categories.get(category, [])
        return [self._handlers[hid] for hid in handler_ids if hid in self._handlers]
    
    def get_handlers_by_type(self, handler_type: HandlerType) -> List[RegisteredHandler]:
        """Get all handlers of a specific type."""
        return [
            handler for handler in self._handlers.values()
            if handler.metadata.handler_type == handler_type
        ]
    
    def get_commands(self) -> Dict[str, RegisteredHandler]:
        """Get all command handlers mapped by command name."""
        return {
            cmd: self._handlers[handler_id] 
            for cmd, handler_id in self._commands.items()
            if handler_id in self._handlers
        }
    
    def is_registered(self, identifier: str) -> bool:
        """Check if a handler is registered."""
        return identifier in self._handlers
    
    def unregister(self, identifier: str) -> bool:
        """
        Unregister a handler.
        
        Args:
            identifier: Handler identifier
            
        Returns:
            bool: True if handler was unregistered, False if not found
        """
        if identifier not in self._handlers:
            return False
            
        handler = self._handlers[identifier]
        
        # Remove from main registry
        del self._handlers[identifier]
        
        # Remove from command mapping
        if handler.metadata.command:
            self._commands.pop(handler.metadata.command, None)
            for alias in handler.metadata.aliases:
                self._commands.pop(alias, None)
        
        # Remove from category mapping
        if identifier in self._categories[handler.metadata.category]:
            self._categories[handler.metadata.category].remove(identifier)
            
        self._logger.info(f"Unregistered handler: {identifier}")
        return True
    
    def generate_help_text(self, category: Optional[HandlerCategory] = None) -> str:
        """
        Generate help text from registered handlers.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            str: Formatted help text
        """
        if category:
            handlers = self.get_handlers_by_category(category)
            title = f"🤖 <b>{category.value.title()} Commands:</b>\n\n"
        else:
            handlers = [h for h in self.get_all_handlers() if not h.metadata.hidden]
            title = "🤖 <b>Available Commands:</b>\n\n"
        
        if not handlers:
            return title + "No commands available."
        
        # Group by category
        by_category = defaultdict(list)
        for handler in handlers:
            if handler.metadata.handler_type == HandlerType.COMMAND:
                by_category[handler.metadata.category].append(handler)
        
        help_lines = [title]
        
        for cat in HandlerCategory:
            cat_handlers = by_category.get(cat, [])
            if not cat_handlers:
                continue
                
            help_lines.append(f"<b>{cat.value.title()}:</b>")
            
            for handler in sorted(cat_handlers, key=lambda h: h.metadata.command or ""):
                cmd = handler.metadata.command
                desc = handler.metadata.description
                usage = handler.metadata.usage or f"/{cmd}"
                
                help_lines.append(f"  /{cmd} - {desc}")
                if usage != f"/{cmd}":
                    help_lines.append(f"    Usage: {usage}")
            
            help_lines.append("")  # Empty line between categories
        
        return "\n".join(help_lines)
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get statistics summary for all handlers."""
        total_calls = sum(h.stats.calls for h in self._handlers.values())
        total_errors = sum(h.stats.errors for h in self._handlers.values())
        
        return {
            "total_handlers": len(self._handlers),
            "total_calls": total_calls,
            "total_errors": total_errors,
            "error_rate": total_errors / total_calls if total_calls > 0 else 0,
            "handlers_by_type": {
                htype.value: len(self.get_handlers_by_type(htype))
                for htype in HandlerType
            },
            "handlers_by_category": {
                cat.value: len(self.get_handlers_by_category(cat))
                for cat in HandlerCategory
            }
        }


# Global registry instance
_global_registry: Optional[HandlersRegistry] = None


def get_registry() -> HandlersRegistry:
    """Get the global handlers registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = HandlersRegistry()
    return _global_registry


def set_registry(registry: HandlersRegistry) -> None:
    """Set the global handlers registry instance."""
    global _global_registry
    _global_registry = registry 