"""
Core questionnaire framework package.

Provides reusable questionnaire infrastructure components:
- Type definitions and protocols for questionnaires
- Abstract base services for session management and question provision
- Core orchestration services
- Decorators for questionnaire handler registration
"""

from .protocols import (
    SessionManagerProtocol,
    QuestionProviderProtocol,
    QuestionnaireServiceProtocol
)
from .types import (
    QuestionData,
    QuestionOption,
    QuestionType,
    QuestionnaireSession,
    HandlerCategory
)
from .states import (
    BaseQuestionnaireStates,
    BaseGenderStates
)
from .services import (
    BaseSessionManager,
    BaseQuestionProvider,
    QuestionnaireService,
    get_questionnaire_service,
    set_questionnaire_service
)
from .decorators import (
    questionnaire_handler,
    single_question_handler,
    multi_step_questionnaire_handler,
    survey_handler,
    quiz_handler
)

__version__ = "1.0.0"

__all__ = [
    # Protocols
    'SessionManagerProtocol',
    'QuestionProviderProtocol', 
    'QuestionnaireServiceProtocol',
    
    # Types and data structures
    'QuestionData',
    'QuestionOption',
    'QuestionType',
    'QuestionnaireSession',
    'HandlerCategory',
    
    # FSM States
    'BaseQuestionnaireStates',
    'BaseGenderStates',
    
    # Services
    'BaseSessionManager',
    'BaseQuestionProvider',
    'QuestionnaireService',
    'get_questionnaire_service',
    'set_questionnaire_service',
    
    # Decorators
    'questionnaire_handler',
    'single_question_handler',
    'multi_step_questionnaire_handler',
    'survey_handler',
    'quiz_handler'
] 