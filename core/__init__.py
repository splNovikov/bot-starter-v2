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

# Export questionnaire framework
from .questionnaire import (
    SessionManagerProtocol, QuestionProviderProtocol, QuestionnaireServiceProtocol,
    QuestionData, QuestionOption, QuestionType, QuestionnaireSession,
    BaseQuestionnaireStates, BaseGenderStates,
    BaseSessionManager, BaseQuestionProvider, QuestionnaireService,
    get_questionnaire_service, set_questionnaire_service,
    questionnaire_handler, single_question_handler, multi_step_questionnaire_handler,
    survey_handler, quiz_handler
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
    
    # Questionnaire framework - Protocols
    'SessionManagerProtocol',
    'QuestionProviderProtocol', 
    'QuestionnaireServiceProtocol',
    
    # Questionnaire framework - Types
    'QuestionData',
    'QuestionOption',
    'QuestionType',
    'QuestionnaireSession',
    
    # Questionnaire framework - States
    'BaseQuestionnaireStates',
    'BaseGenderStates',
    
    # Questionnaire framework - Services
    'BaseSessionManager',
    'BaseQuestionProvider',
    'QuestionnaireService',
    'get_questionnaire_service',
    'set_questionnaire_service',
    
    # Questionnaire framework - Decorators
    'questionnaire_handler',
    'single_question_handler',
    'multi_step_questionnaire_handler',
    'survey_handler',
    'quiz_handler'
] 