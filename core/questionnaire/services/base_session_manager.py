"""
Base session manager for questionnaire framework.

Provides abstract base class with common session management functionality
that can be extended by concrete implementations.
"""

import uuid
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional

from core.utils.logger import get_logger
from ..protocols import SessionManagerProtocol
from ..types import QuestionnaireSession

logger = get_logger()


class BaseSessionManager(SessionManagerProtocol, ABC):
    """
    Abstract base class for session management implementations.
    
    Provides common functionality while allowing concrete implementations
    to customize data storage and persistence strategies.
    """
    
    def __init__(self):
        """Initialize base session manager."""
        self._sessions: Dict[int, QuestionnaireSession] = {}
    
    def create_session(self, user_id: int) -> str:
        """
        Create a new questionnaire session.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session ID string
        """
        session_id = str(uuid.uuid4())
        session = QuestionnaireSession(
            session_id=session_id,
            user_id=user_id,
            current_question=0,
            answers={},
            started_at=time.time(),
            updated_at=time.time()
        )
        
        # Store session
        self._sessions[user_id] = session
        
        # Call hook for custom logic
        self._on_session_created(session)
        
        logger.info(f"Created questionnaire session {session_id} for user {user_id}")
        return session_id
    
    def get_session(self, user_id: int) -> Optional[dict]:
        """
        Get existing session data as dictionary.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session data dictionary or None if no session exists
        """
        session = self._sessions.get(user_id)
        return session.to_dict() if session else None
    
    def get_session_object(self, user_id: int) -> Optional[QuestionnaireSession]:
        """
        Get session as typed object.
        
        Args:
            user_id: User identifier
            
        Returns:
            QuestionnaireSession object or None if no session exists
        """
        return self._sessions.get(user_id)
    
    def add_answer(self, user_id: int, question_key: str, answer: str) -> bool:
        """
        Add answer to session.
        
        Args:
            user_id: User identifier
            question_key: Question identifier
            answer: User's answer
            
        Returns:
            True if answer was successfully added
        """
        try:
            session = self._sessions.get(user_id)
            if not session:
                logger.warning(f"No session found for user {user_id}")
                return False
            
            # Add answer to session
            session.add_answer(question_key, answer)
            
            # Call hook for custom logic
            self._on_answer_added(session, question_key, answer)
            
            # Persist session if needed
            self._persist_session(session)
            
            logger.debug(f"Added answer for {question_key} in session {session.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding answer for user {user_id}: {e}")
            return False
    
    def advance_question(self, user_id: int) -> None:
        """
        Advance to next question in session.
        
        Args:
            user_id: User identifier
        """
        session = self._sessions.get(user_id)
        if session:
            session.current_question += 1
            session.updated_at = time.time()
            
            # Call hook for custom logic
            self._on_question_advanced(session)
            
            # Persist session if needed
            self._persist_session(session)
            
            logger.debug(f"Advanced to question {session.current_question} for user {user_id}")
    
    def cancel_session(self, user_id: int) -> bool:
        """
        Cancel active session.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if session was successfully cancelled
        """
        try:
            session = self._sessions.get(user_id)
            if not session:
                return False
            
            # Call hook for custom logic
            self._on_session_cancelled(session)
            
            # Remove session
            del self._sessions[user_id]
            
            logger.info(f"Cancelled session {session.session_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling session for user {user_id}: {e}")
            return False
    
    def delete_session(self, user_id: int) -> bool:
        """
        Delete session data.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if session was successfully deleted
        """
        try:
            session = self._sessions.get(user_id)
            if not session:
                return False
            
            # Call hook for custom logic
            self._on_session_deleted(session)
            
            # Remove session
            del self._sessions[user_id]
            
            logger.info(f"Deleted session {session.session_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting session for user {user_id}: {e}")
            return False
    
    # Abstract methods for customization
    
    @abstractmethod
    def _persist_session(self, session: QuestionnaireSession) -> None:
        """
        Persist session data (implemented by subclasses).
        
        Args:
            session: Session to persist
        """
        pass
    
    # Hook methods for customization (optional override)
    
    def _on_session_created(self, session: QuestionnaireSession) -> None:
        """
        Hook called after session creation.
        
        Args:
            session: Created session
        """
        pass
    
    def _on_answer_added(self, session: QuestionnaireSession, question_key: str, answer: str) -> None:
        """
        Hook called after answer is added.
        
        Args:
            session: Session object
            question_key: Question identifier
            answer: User's answer
        """
        pass
    
    def _on_question_advanced(self, session: QuestionnaireSession) -> None:
        """
        Hook called after question advancement.
        
        Args:
            session: Session object
        """
        pass
    
    def _on_session_cancelled(self, session: QuestionnaireSession) -> None:
        """
        Hook called before session cancellation.
        
        Args:
            session: Session to be cancelled
        """
        pass
    
    def _on_session_deleted(self, session: QuestionnaireSession) -> None:
        """
        Hook called before session deletion.
        
        Args:
            session: Session to be deleted
        """
        pass
    
    # Utility methods
    
    def get_all_sessions(self) -> Dict[int, QuestionnaireSession]:
        """
        Get all active sessions (for debugging/admin purposes).
        
        Returns:
            Dictionary of user_id -> session
        """
        return self._sessions.copy()
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired sessions.
        
        Args:
            max_age_hours: Maximum age for sessions in hours
            
        Returns:
            Number of sessions cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        expired_users = []
        
        for user_id, session in self._sessions.items():
            if current_time - session.updated_at > max_age_seconds:
                expired_users.append(user_id)
        
        # Remove expired sessions
        for user_id in expired_users:
            self.delete_session(user_id)
        
        if expired_users:
            logger.info(f"Cleaned up {len(expired_users)} expired sessions")
        
        return len(expired_users) 