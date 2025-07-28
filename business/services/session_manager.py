"""
Session management service for questionnaire interactions.

Handles session lifecycle, data storage, and cleanup following the 
Single Responsibility Principle.
"""

import uuid
from typing import Dict, Optional
from dataclasses import dataclass, asdict

from core.utils.logger import get_logger
from business.services.interfaces import SessionManagerProtocol

logger = get_logger()


@dataclass
class QuestionnaireSession:
    """Active questionnaire session data."""
    session_id: str
    user_id: int
    current_question: int
    answers: Dict[str, str]
    is_female: Optional[bool] = None
    
    def __post_init__(self):
        """Initialize session with default values."""
        if not self.answers:
            self.answers = {}

    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return asdict(self)


class SessionManager(SessionManagerProtocol):
    """Manages questionnaire sessions in memory."""
    
    def __init__(self):
        """Initialize session manager."""
        self._sessions: Dict[int, QuestionnaireSession] = {}
    
    def create_session(self, user_id: int) -> str:
        """
        Create a new questionnaire session.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Session ID string
        """
        session_id = str(uuid.uuid4())
        session = QuestionnaireSession(
            session_id=session_id,
            user_id=user_id,
            current_question=0,
            answers={}
        )
        
        self._sessions[user_id] = session
        logger.info(f"Created session {session_id} for user {user_id}")
        
        return session_id
    
    def get_session(self, user_id: int) -> Optional[dict]:
        """
        Get active session for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Session data as dict or None if no session exists
        """
        session = self._sessions.get(user_id)
        return session.to_dict() if session else None
    
    def get_session_object(self, user_id: int) -> Optional[QuestionnaireSession]:
        """
        Get active session object for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Session object or None if no session exists
        """
        return self._sessions.get(user_id)
    
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