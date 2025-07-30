"""
Concrete sequence manager implementation.

Extends BaseSequenceManager to provide in-memory session management
for the sequence framework.
"""

from core.sequence.services.base_sequence_manager import BaseSequenceManager
from core.sequence.types import SequenceSession, SequenceAnswer
from core.utils.logger import get_logger

logger = get_logger()


class InMemorySequenceManager(BaseSequenceManager):
    """
    In-memory sequence manager implementation.
    
    Extends BaseSequenceManager to provide concrete session management
    with in-memory storage and logging hooks.
    """
    
    def _on_session_created(self, session: SequenceSession) -> None:
        """
        Hook called when a session is created.
        
        Args:
            session: Created session
        """
        logger.info(f"Created sequence session {session.session_id} for user {session.user_id} - {session.sequence_name}")
    
    def _on_session_accessed(self, session: SequenceSession) -> None:
        """
        Hook called when a session is accessed.
        
        Args:
            session: Accessed session
        """
        logger.debug(f"Accessed sequence session {session.session_id} for user {session.user_id}")
    
    def _on_answer_added(self, session: SequenceSession, answer: SequenceAnswer) -> None:
        """
        Hook called when an answer is added.
        
        Args:
            session: Session that received the answer
            answer: Added answer
        """
        logger.info(f"Added answer '{answer.answer_value}' for question '{answer.question_key}' "
                   f"to session {session.session_id}")
    
    def _on_step_advanced(self, session: SequenceSession) -> None:
        """
        Hook called when session advances to next step.
        
        Args:
            session: Session that advanced
        """
        logger.debug(f"Advanced to step {session.current_step} in session {session.session_id}")
    
    def _on_session_completed(self, session: SequenceSession) -> None:
        """
        Hook called when a session is completed.
        
        Args:
            session: Completed session
        """
        logger.info(f"Completed sequence session {session.session_id} for user {session.user_id} - {session.sequence_name}")
    
    def _on_session_abandoned(self, session: SequenceSession) -> None:
        """
        Hook called when a session is abandoned.
        
        Args:
            session: Abandoned session
        """
        logger.warning(f"Abandoned sequence session {session.session_id} for user {session.user_id} - {session.sequence_name}")
    
    def _on_session_cleared(self, session: SequenceSession) -> None:
        """
        Hook called when a session is cleared.
        
        Args:
            session: Cleared session
        """
        logger.info(f"Cleared sequence session {session.session_id} for user {session.user_id}")


__all__ = ['InMemorySequenceManager'] 