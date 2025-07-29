"""
Business questionnaire service initialization.

Creates and configures the core questionnaire service with concrete
business implementations for session management and question provision.
"""

from typing import Optional

from core.questionnaire.services import QuestionnaireService as CoreQuestionnaireService, set_questionnaire_service
from business.services.api_client import get_api_client
from business.services.session_manager import get_session_manager
from business.services.question_provider import get_question_provider


def _create_questionnaire_service() -> CoreQuestionnaireService:
    """
    Create and configure the core questionnaire service with business implementations.
    
    Returns:
        Configured CoreQuestionnaireService instance
    """
    # Get concrete implementations
    session_manager = get_session_manager()
    question_provider = get_question_provider()
    api_client = get_api_client()
    
    # Create core service with business implementations
    service = CoreQuestionnaireService(
        session_manager=session_manager,
        question_provider=question_provider,
        api_client=api_client
    )
    
    # Set as global instance
    set_questionnaire_service(service)
    
    return service


# Global questionnaire service instance
_questionnaire_service: Optional[CoreQuestionnaireService] = None


def get_questionnaire_service() -> CoreQuestionnaireService:
    """Get the global questionnaire service instance."""
    global _questionnaire_service
    if _questionnaire_service is None:
        _questionnaire_service = _create_questionnaire_service()
    return _questionnaire_service


# Legacy compatibility - create service with business logic
def submit_standalone_gender(user_id: int, gender: str, user) -> tuple[bool, str, str]:
    """
    Legacy compatibility function for standalone gender submission.
    
    Args:
        user_id: User identifier
        gender: Gender value
        user: User object
        
    Returns:
        Tuple of (success, response_message, summary_message)
    """
    from asyncio import run
    service = get_questionnaire_service()
    return run(service.submit_standalone_answer(user_id, 'gender', gender, user))


def generate_gender_summary(gender: str, user) -> str:
    """
    Legacy compatibility function for gender summary generation.
    
    Args:
        gender: Gender value  
        user: User object
        
    Returns:
        Summary text
    """
    service = get_questionnaire_service()
    return service.generate_standalone_summary('gender', gender, user) 