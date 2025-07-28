"""
Business services package.

Contains reusable business logic services that implement core bot functionality.
All services follow SOLID principles and are designed for easy testing and maintenance.
"""

from .greeting import send_greeting, get_username, create_greeting_message
from .localization import (
    LocalizationService, 
    get_localization_service, 
    t
)
from .help_service import (
    LocalizedHelpService,
    get_help_service,
    generate_localized_help
)
from .questionnaire_service import get_questionnaire_service
from .api_client import get_api_client
from .session_manager import get_session_manager
from .question_provider import get_question_provider

__version__ = "2.0.0"

__all__ = [
    # Greeting services
    'send_greeting',
    'get_username', 
    'create_greeting_message',
    
    # Localization services
    'LocalizationService',
    'get_localization_service', 
    't',
    
    # Help services
    'LocalizedHelpService',
    'get_help_service',
    'generate_localized_help',
    
    # Questionnaire services
    'get_questionnaire_service',
    'get_api_client',
    'get_session_manager',
    'get_question_provider'
] 