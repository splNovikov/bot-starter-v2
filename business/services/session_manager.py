"""
Session management service for questionnaire interactions.

Concrete implementation extending the core base session manager
with business-specific logic and in-memory storage.
"""

from typing import Optional

from core.utils.logger import get_logger
from core.questionnaire.services import BaseSessionManager
from core.questionnaire.types import QuestionnaireSession

logger = get_logger()


class SessionManager(BaseSessionManager):
    """Manages questionnaire sessions in memory."""
    
    def __init__(self):
        """Initialize session manager."""
        super().__init__()
    
    def _persist_session(self, session: QuestionnaireSession) -> None:
        """
        Persist session data (in-memory implementation).
        
        Args:
            session: Session to persist
        """
        # In-memory implementation - no additional persistence needed
        # Data is already stored in self._sessions from BaseSessionManager
        pass
    
    def update_session(self, user_id: int, **kwargs) -> bool:
        """
        Update session data.
        
        Args:
            user_id: Telegram user ID
            **kwargs: Fields to update
            
        Returns:
            True if session was updated, False if session doesn't exist
        """
        session = self._sessions.get(user_id)
        if not session:
            return False
        
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        logger.debug(f"Updated session for user {user_id}: {kwargs}")
        return True
    
    def delete_session(self, user_id: int) -> bool:
        """
        Delete user session.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if session was deleted, False if no session existed
        """
        session = self._sessions.pop(user_id, None)
        if session:
            logger.info(f"Deleted session {session.session_id} for user {user_id}")
            return True
        return False
    
    def add_answer(self, user_id: int, question_key: str, answer: str) -> bool:
        """
        Add an answer to the user's session.
        
        Args:
            user_id: Telegram user ID
            question_key: Question identifier
            answer: User's answer
            
        Returns:
            True if answer was added, False if no session exists
        """
        session = self._sessions.get(user_id)
        if not session:
            return False
        
        session.answers[question_key] = answer
        
        # Special handling for gender
        if question_key == 'gender':
            session.is_female = answer.lower() in ['female', 'woman', 'f', 'женщина', 'ж', 'mujer', 'm']
        
        logger.debug(f"Added answer for user {user_id}: {question_key} = {answer}")
        return True
    
    def advance_question(self, user_id: int) -> bool:
        """
        Advance to the next question in the session.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if advanced, False if no session exists
        """
        session = self._sessions.get(user_id)
        if not session:
            return False
        
        session.current_question += 1
        logger.debug(f"Advanced user {user_id} to question {session.current_question}")
        return True


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager 