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
    HandlerCategory,
    HandlerMetadata,
    HandlersRegistry,
    HandlerType,
    command,
    get_registry,
    handler,
    message_handler,
    set_registry,
    text_handler,
)
from .middleware import LoggingMiddleware
from .protocols import ApiResponse

# Export sequence framework (protocols and types only - Clean Architecture)
from .sequence import (  # Deprecated global functions (for backward compatibility only)
    SequenceAnswer,
    SequenceDefinition,
    SequenceManagerProtocol,
    SequenceProviderProtocol,
    SequenceQuestion,
    SequenceServiceProtocol,
    SequenceSession,
    SequenceStateManager,
    SequenceStates,
    SequenceStatus,
    create_simple_sequence_definition,
    get_behavior_type,
    get_sequence_metadata,
    is_sequence_handler,
    sequence_handler,
)
from .services import LocalizationService, get_localization_service, t
from .utils import get_logger, setup_logger

__version__ = "1.0.0"

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
    # Types and enums
    "HandlerType",
    "HandlerCategory",
    "HandlerMetadata",
    # Middleware
    "LoggingMiddleware",
    # Services
    "LocalizationService",
    "get_localization_service",
    "t",
    # Protocols
    "ApiResponse",
    # Utilities
    "get_logger",
    "setup_logger",
    # Sequence framework (unified abstraction) - Types
    "SequenceStatus",
    "SequenceSession",
    "SequenceDefinition",
    "SequenceQuestion",
    "SequenceAnswer",
    # Sequence framework - Protocols
    "SequenceManagerProtocol",
    "SequenceProviderProtocol",
    "SequenceServiceProtocol",
    # Sequence framework - States
    "SequenceStates",
    "SequenceStateManager",
    # Sequence framework - Decorators
    "sequence_handler",
    # Sequence framework - Utilities
    "create_simple_sequence_definition",
    "is_sequence_handler",
    "get_sequence_metadata",
    "get_behavior_type",
]
