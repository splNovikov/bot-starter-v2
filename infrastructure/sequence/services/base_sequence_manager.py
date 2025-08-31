"""
Base sequence manager for the sequence framework.

Provides abstract base class with common session management functionality
that can be extended by concrete implementations.
"""

from abc import ABC, abstractmethod
import time
from typing import Dict, Optional
import uuid

from core.sequence.protocols import SequenceManagerProtocol
from core.sequence.types import SequenceAnswer, SequenceSession, SequenceStatus
from core.utils.logger import get_logger

logger = get_logger()


class BaseSequenceManager(SequenceManagerProtocol, ABC):
    """
    Abstract base class for sequence session management implementations.

    Provides common functionality while allowing concrete implementations
    to customize data storage and persistence strategies.
    """

    def __init__(self):
        """Initialize base sequence manager."""
        self._sessions: Dict[int, SequenceSession] = {}

    def create_session(self, user_id: int, sequence_name: str) -> str:
        """
        Create a new sequence session.

        Args:
            user_id: User identifier
            sequence_name: Name of the sequence to start

        Returns:
            Session ID string
        """
        session_id = str(uuid.uuid4())
        session = SequenceSession(
            session_id=session_id,
            user_id=user_id,
            sequence_name=sequence_name,
            current_step=0,
            answers={},
            status=SequenceStatus.ACTIVE,
            started_at=time.time(),
            updated_at=time.time(),
        )

        # Store session
        self._sessions[user_id] = session

        # Call hook for custom logic
        self._on_session_created(session)

        logger.info(f"Created sequence session {session_id} for user {user_id}")
        return session_id

    def get_session(self, user_id: int) -> Optional[SequenceSession]:
        """
        Get existing session data.

        Args:
            user_id: User identifier

        Returns:
            SequenceSession object or None if no session exists
        """
        session = self._sessions.get(user_id)
        if session:
            self._on_session_accessed(session)
        return session

    def add_answer(self, user_id: int, answer: SequenceAnswer) -> bool:
        """
        Add answer to session.

        Args:
            user_id: User identifier
            answer: SequenceAnswer object

        Returns:
            True if answer was successfully added
        """
        session = self.get_session(user_id)
        if not session:
            logger.warning(f"No active session found for user {user_id}")
            return False

        try:
            session.add_answer(answer)
            self._sessions[user_id] = session

            # Call hook for custom logic
            self._on_answer_added(session, answer)

            logger.debug(
                f"Added answer for {answer.question_key} to session {session.session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error adding answer to session {session.session_id}: {e}")
            return False

    def advance_step(self, user_id: int) -> bool:
        """
        Advance to next step in sequence.

        Args:
            user_id: User identifier

        Returns:
            True if advanced successfully
        """
        session = self.get_session(user_id)
        if not session:
            logger.warning(f"No active session found for user {user_id}")
            return False

        try:
            session.current_step += 1
            session.updated_at = time.time()
            self._sessions[user_id] = session

            # Call hook for custom logic
            self._on_step_advanced(session)

            logger.debug(
                f"Advanced to step {session.current_step} in session {session.session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error advancing step in session {session.session_id}: {e}")
            return False

    def complete_session(self, user_id: int) -> bool:
        """
        Mark session as completed.

        Args:
            user_id: User identifier

        Returns:
            True if marked as completed
        """
        session = self.get_session(user_id)
        if not session:
            logger.warning(f"No active session found for user {user_id}")
            return False

        try:
            session.mark_completed()
            self._sessions[user_id] = session

            # Call hook for custom logic
            self._on_session_completed(session)

            logger.info(f"Completed sequence session {session.session_id}")
            return True

        except Exception as e:
            logger.error(f"Error completing session {session.session_id}: {e}")
            return False

    def abandon_session(self, user_id: int) -> bool:
        """
        Mark session as abandoned.

        Args:
            user_id: User identifier

        Returns:
            True if marked as abandoned
        """
        session = self.get_session(user_id)
        if not session:
            logger.warning(f"No active session found for user {user_id}")
            return False

        try:
            session.status = SequenceStatus.ABANDONED
            session.updated_at = time.time()
            self._sessions[user_id] = session

            # Call hook for custom logic
            self._on_session_abandoned(session)

            logger.info(f"Abandoned sequence session {session.session_id}")
            return True

        except Exception as e:
            logger.error(f"Error abandoning session {session.session_id}: {e}")
            return False

    def clear_session(self, user_id: int) -> bool:
        """
        Clear/delete session data.

        Args:
            user_id: User identifier

        Returns:
            True if session was cleared
        """
        if user_id not in self._sessions:
            logger.warning(f"No session found for user {user_id}")
            return False

        try:
            session = self._sessions[user_id]
            del self._sessions[user_id]

            # Call hook for custom logic
            self._on_session_cleared(session)

            logger.info(f"Cleared session {session.session_id} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error clearing session for user {user_id}: {e}")
            return False

    # Abstract hooks for custom implementations

    @abstractmethod
    def _on_session_created(self, session: SequenceSession) -> None:
        """
        Hook called when a session is created.

        Args:
            session: Created session
        """

    def _on_session_accessed(self, session: SequenceSession) -> None:
        """
        Hook called when a session is accessed.

        Args:
            session: Accessed session
        """

    def _on_answer_added(
        self, session: SequenceSession, answer: SequenceAnswer
    ) -> None:
        """
        Hook called when an answer is added.

        Args:
            session: Session that received the answer
            answer: Added answer
        """

    def _on_step_advanced(self, session: SequenceSession) -> None:
        """
        Hook called when session advances to next step.

        Args:
            session: Session that advanced
        """

    def _on_session_completed(self, session: SequenceSession) -> None:
        """
        Hook called when a session is completed.

        Args:
            session: Completed session
        """

    def _on_session_abandoned(self, session: SequenceSession) -> None:
        """
        Hook called when a session is abandoned.

        Args:
            session: Abandoned session
        """

    def _on_session_cleared(self, session: SequenceSession) -> None:
        """
        Hook called when a session is cleared.

        Args:
            session: Cleared session
        """

    # Utility methods

    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        return len(
            [s for s in self._sessions.values() if s.status == SequenceStatus.ACTIVE]
        )

    def get_completed_sessions_count(self) -> int:
        """Get count of completed sessions."""
        return len(
            [s for s in self._sessions.values() if s.status == SequenceStatus.COMPLETED]
        )

    def cleanup_abandoned_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old abandoned sessions.

        Args:
            max_age_hours: Maximum age in hours before cleanup

        Returns:
            Number of sessions cleaned up
        """
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_count = 0

        user_ids_to_remove = []
        for user_id, session in self._sessions.items():
            if (
                session.status in [SequenceStatus.ABANDONED, SequenceStatus.COMPLETED]
                and session.updated_at < cutoff_time
            ):
                user_ids_to_remove.append(user_id)

        for user_id in user_ids_to_remove:
            self.clear_session(user_id)
            cleaned_count += 1

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old sessions")

        return cleaned_count


__all__ = ["BaseSequenceManager"]
