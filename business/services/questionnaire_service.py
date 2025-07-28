"""
Questionnaire service for orchestrating questionnaire interactions.

Coordinates between session management, question provision, and API integration
following the Single Responsibility Principle.
"""

from typing import Optional, Tuple
from aiogram.types import User

from core.utils.logger import get_logger
from business.services.localization import t
from business.services.interfaces import ApiClientProtocol, SessionManagerProtocol, QuestionProviderProtocol
from business.services.api_client import get_api_client
from business.services.session_manager import get_session_manager
from business.services.question_provider import get_question_provider

logger = get_logger()


class QuestionnaireService:
    """Service for orchestrating questionnaire interactions."""
    
    def __init__(
        self,
        api_client: Optional[ApiClientProtocol] = None,
        session_manager: Optional[SessionManagerProtocol] = None,
        question_provider: Optional[QuestionProviderProtocol] = None
    ):
        """
        Initialize questionnaire service with dependency injection.
        
        Args:
            api_client: API client for external requests
            session_manager: Session management service
            question_provider: Question provision service
        """
        self._api_client = api_client or get_api_client()
        self._session_manager = session_manager or get_session_manager()
        self._question_provider = question_provider or get_question_provider()
    
    def start_questionnaire(self, user_id: int) -> str:
        """
        Start a new questionnaire session.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Session ID
        """
        session_id = self._session_manager.create_session(user_id)
        logger.info(f"Started questionnaire session {session_id} for user {user_id}")
        return session_id
    
    def get_session(self, user_id: int) -> Optional[dict]:
        """
        Get active questionnaire session for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Active session data or None if no session exists
        """
        return self._session_manager.get_session(user_id)
    
    def get_current_question_key(self, user_id: int, user: User) -> Optional[str]:
        """
        Get the current question key for the user's session.
        
        Args:
            user_id: Telegram user ID
            user: Telegram user object
            
        Returns:
            Current question key or None if questionnaire is complete
        """
        session_data = self._session_manager.get_session(user_id)
        if not session_data:
            return None
        
        return self._question_provider.get_next_question(session_data['answers'], user)
    
    def get_question_text(self, question_key: str, user: User) -> str:
        """
        Get localized question text.
        
        Args:
            question_key: Question identifier
            user: Telegram user object for localization
            
        Returns:
            Localized question text
        """
        return self._question_provider.get_question_text(question_key, user)
    
    async def submit_answer(
        self, 
        user_id: int, 
        answer: str, 
        user: User
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Submit answer for current question and advance session.
        
        Args:
            user_id: Telegram user ID
            answer: User's answer
            user: Telegram user object for localization
            
        Returns:
            Tuple of (success, next_question_key, error_message)
        """
        try:
            # Get current session
            session_data = self._session_manager.get_session(user_id)
            if not session_data:
                return False, None, t("questionnaire.errors.no_session", user=user)
            
            # Get current question key
            current_question_key = self._question_provider.get_next_question(session_data['answers'], user)
            if not current_question_key:
                return False, None, t("questionnaire.errors.no_current_question", user=user)
            
            # Add answer to session
            if not self._session_manager.add_answer(user_id, current_question_key, answer):
                return False, None, t("questionnaire.errors.submit_failed", user=user)
            
            # Submit answer to API
            api_response = await self._api_client.submit_questionnaire_answer(
                user_id=user_id,
                question_key=current_question_key,
                answer=answer,
                session_id=session_data['session_id']
            )
            
            if not api_response.success:
                logger.warning(f"Failed to submit answer to API: {api_response.error}")
                # Continue with local processing even if API fails
            
            # Advance session
            self._session_manager.advance_question(user_id)
            
            # Get updated session data for next question
            updated_session = self._session_manager.get_session(user_id)
            next_question_key = self._question_provider.get_next_question(updated_session['answers'], user)
            
            # If no next question, questionnaire is complete
            if not next_question_key:
                await self._complete_questionnaire(user_id, updated_session['session_id'], user)
                return True, None, None
            
            return True, next_question_key, None
            
        except Exception as e:
            logger.error(f"Error submitting answer for user {user_id}: {e}")
            return False, None, t("questionnaire.errors.submit_failed", user=user)
    
    async def submit_standalone_gender(self, user_id: int, gender: str, user: User) -> Tuple[bool, str, str]:
        """
        Submit standalone gender response (for /gender command).
        
        Args:
            user_id: Telegram user ID
            gender: User's gender response
            user: Telegram user object for localization
            
        Returns:
            Tuple of (success, response_message, summary_message)
        """
        try:
            # Submit to API
            api_response = await self._api_client.submit_gender(user_id, gender)
            
            if api_response.success:
                logger.info(f"Successfully submitted gender for user {user_id}")
                
                # Generate summary
                summary = self.generate_gender_summary(gender, user)
                success_msg = t("questionnaire.gender_submitted", user=user)
                
                return True, success_msg, summary
            else:
                logger.warning(f"Failed to submit gender to API: {api_response.error}")
                return False, t("questionnaire.errors.submit_failed", user=user), ""
                
        except Exception as e:
            logger.error(f"Error submitting gender for user {user_id}: {e}")
            return False, t("questionnaire.errors.submit_failed", user=user), ""
    
    async def _complete_questionnaire(self, user_id: int, session_id: str, user: User):
        """
        Complete the questionnaire session.
        
        Args:
            user_id: User ID
            session_id: Session ID
            user: Telegram user object
        """
        try:
            # Submit completion to API
            api_response = await self._api_client.complete_questionnaire(
                user_id=user_id,
                session_id=session_id
            )
            
            if api_response.success:
                logger.info(f"Questionnaire completed successfully for user {user_id}")
            else:
                logger.warning(f"Failed to mark questionnaire complete in API: {api_response.error}")
            
            # Clean up session
            self._session_manager.delete_session(user_id)
            
        except Exception as e:
            logger.error(f"Error completing questionnaire for user {user_id}: {e}")
    
    def cancel_session(self, user_id: int):
        """
        Cancel active questionnaire session.
        
        Args:
            user_id: Telegram user ID
        """
        if self._session_manager.delete_session(user_id):
            logger.info(f"Cancelled questionnaire session for user {user_id}")
    
    def get_progress_text(self, user_id: int, user: User) -> str:
        """
        Get progress text for current session.
        
        Args:
            user_id: Telegram user ID
            user: Telegram user object for localization
            
        Returns:
            Localized progress text
        """
        session_data = self._session_manager.get_session(user_id)
        if not session_data:
            return t("questionnaire.errors.no_session", user=user)
        
        current, total = self._question_provider.get_progress(session_data['answers'], user)
        return t("questionnaire.progress", user=user, current=current, total=total)
    
    def generate_questionnaire_summary(self, user_id: int, user: User) -> str:
        """
        Generate a summary of the completed questionnaire.
        
        Args:
            user_id: Telegram user ID
            user: Telegram user object for localization
            
        Returns:
            Localized summary text with all answers
        """
        session_data = self._session_manager.get_session(user_id)
        if not session_data:
            return t("questionnaire.errors.no_session", user=user)
        
        answers = session_data['answers']
        
        # Build summary sections
        summary_parts = [
            t("questionnaire.summary.header", user=user)
        ]
        
        # Add each answer to summary
        question_keys = ['question_1', 'question_2', 'gender']
        if 'question_4' in answers:
            question_keys.append('question_4')
        
        for i, question_key in enumerate(question_keys, 1):
            if question_key in answers:
                question_text = self.get_question_text(question_key, user)
                answer = answers[question_key]
                
                # Format each Q&A pair
                qa_text = t("questionnaire.summary.qa_format", 
                           user=user, 
                           number=i,
                           question=question_text.replace("🎯 ", "").replace("⭐ ", "").replace("👤 ", "").replace("💄 ", ""),
                           answer=answer)
                summary_parts.append(qa_text)
        
        return "\n\n".join(summary_parts)
    
    def generate_gender_summary(self, gender: str, user: User) -> str:
        """
        Generate a summary for standalone gender submission.
        
        Args:
            gender: User's gender response
            user: Telegram user object for localization
            
        Returns:
            Localized gender summary text
        """
        return t("questionnaire.gender_summary", user=user, gender=gender)


# Global questionnaire service instance
_questionnaire_service: Optional[QuestionnaireService] = None


def get_questionnaire_service() -> QuestionnaireService:
    """Get the global questionnaire service instance."""
    global _questionnaire_service
    if _questionnaire_service is None:
        _questionnaire_service = QuestionnaireService()
    return _questionnaire_service 