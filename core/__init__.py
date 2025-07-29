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
from .services import LocalizationService, get_localization_service, t
from .protocols import ApiClientProtocol, ApiResponse
from .utils import get_logger, setup_logger

# Export sequence framework (unified abstraction for all interactive flows)
from .sequence import (
    SequenceStatus, SequenceSession, SequenceDefinition, SequenceQuestion, SequenceAnswer,
    SequenceManagerProtocol, SequenceProviderProtocol, SequenceServiceProtocol,
    SequenceStates, SequenceStateManager,
    BaseSequenceManager, SequenceService, get_sequence_service, set_sequence_service,
    sequence_handler, create_simple_sequence_definition,
    is_sequence_handler, get_sequence_metadata, get_behavior_type
)

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
    
    # Services
    'LocalizationService',
    'get_localization_service',
    't',
    
    # Protocols
    'ApiClientProtocol',
    'ApiResponse',
    
    # Utilities
    'get_logger',
    'setup_logger',
    
    # Sequence framework (unified abstraction) - Types
    'SequenceStatus',
    'SequenceSession',
    'SequenceDefinition',
    'SequenceQuestion',
    'SequenceAnswer',
    
    # Sequence framework - Protocols
    'SequenceManagerProtocol',
    'SequenceProviderProtocol',
    'SequenceServiceProtocol',
    
    # Sequence framework - States
    'SequenceStates',
    'SequenceStateManager',
    
    # Sequence framework - Services
    'BaseSequenceManager',
    'SequenceService',
    'get_sequence_service',
    'set_sequence_service',
    
    # Sequence framework - Decorators
    'sequence_handler',
    
    # Sequence framework - Utilities
    'create_simple_sequence_definition',
    'is_sequence_handler',
    'get_sequence_metadata',
    'get_behavior_type'
] 