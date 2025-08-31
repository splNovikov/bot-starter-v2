"""
Sequence session management service.

Handles the creation, management, and lifecycle of sequence sessions,
following the Single Responsibility Principle.
"""

from typing import Optional

from core.di.protocols import Injectable
from core.utils.logger import get_logger

from ..protocols import (
    SequenceManagerProtocol,
    SequenceProviderProtocol,
    SequenceSessionServiceProtocol,
)
from ..types import SequenceAnswer, SequenceSession

logger = get_logger()


class SequenceSessionService(SequenceSessionServiceProtocol, Injectable):
    """
    Service for managing sequence sessions.

    Provides session lifecycle management including creation, progression,
    and completion handling.
    """

    def __init__(
        self,
        session_manager: SequenceManagerProtocol,
        sequence_provider: SequenceProviderProtocol,
    ):
        """
        Initialize session service with dependencies.

        Args:
            session_manager: Session management implementation
            sequence_provider: Sequence provision implementation
        """
        self._session_manager = session_manager
        self._sequence_provider = sequence_provider

    def start_session(self, user_id: int, sequence_name: str) -> str:
        """
        Start a new sequence session.

        Args:
            user_id: User identifier
            sequence_name: Name of the sequence to start

        Returns:
            Session ID

        Raises:
            ValueError: If sequence is not found
        """
        # Check if sequence exists
        sequence_definition = self._sequence_provider.get_sequence_definition(
            sequence_name
        )
        if not sequence_definition:
            raise ValueError(f"Sequence '{sequence_name}' not found")

        # Clear any existing session
        existing_session = self._session_manager.get_session(user_id)
        if existing_session:
            self._session_manager.clear_session(user_id)
            logger.info(f"Cleared existing session for user {user_id}")

        # Create new session
        session_id = self._session_manager.create_session(user_id, sequence_name)

        # Set total questions for progress tracking
        session = self._session_manager.get_session(user_id)
        if session:
            session.total_questions = len(sequence_definition.questions)
            session.metadata["sequence_definition"] = sequence_definition.name

            # For scored sequences, set max possible score
            if sequence_definition.scored:
                session.max_possible_score = (
                    sequence_definition.get_total_possible_score()
                )

        logger.info(f"Started sequence '{sequence_name}' for user {user_id}")
        return session_id

    def get_session(self, user_id: int) -> Optional[SequenceSession]:
        """
        Get current session for user.

        Args:
            user_id: User identifier

        Returns:
            SequenceSession object or None
        """
        return self._session_manager.get_session(user_id)

    def add_answer(self, user_id: int, answer: SequenceAnswer) -> bool:
        """
        Add answer to current session.

        Args:
            user_id: User identifier
            answer: Answer to add

        Returns:
            True if answer was added successfully
        """
        return self._session_manager.add_answer(user_id, answer)

    def advance_step(self, user_id: int) -> bool:
        """
        Advance session to next step.

        Args:
            user_id: User identifier

        Returns:
            True if advanced successfully
        """
        return self._session_manager.advance_step(user_id)

    def complete_session(self, user_id: int) -> bool:
        """
        Mark session as complete.

        Args:
            user_id: User identifier

        Returns:
            True if completed successfully
        """
        return self._session_manager.complete_session(user_id)

    def clear_session(self, user_id: int) -> bool:
        """
        Clear existing session for user.

        Args:
            user_id: User identifier

        Returns:
            True if cleared successfully
        """
        return self._session_manager.clear_session(user_id)
