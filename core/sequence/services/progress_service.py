"""
Sequence progress tracking service.

Handles progress calculation and monitoring for sequence sessions,
following the Single Responsibility Principle.
"""

from typing import Tuple

from core.di.protocols import Injectable
from core.utils.logger import get_logger

from ..protocols import SequenceProgressServiceProtocol, SequenceProviderProtocol
from ..types import SequenceSession

logger = get_logger()


class SequenceProgressService(SequenceProgressServiceProtocol, Injectable):
    """
    Service for tracking sequence progress.

    Provides progress calculation and monitoring functionality
    for sequence sessions.
    """

    def __init__(self, sequence_provider: SequenceProviderProtocol):
        """
        Initialize progress service with dependencies.

        Args:
            sequence_provider: Sequence provision implementation
        """
        self._sequence_provider = sequence_provider

    def get_progress(self, session: SequenceSession) -> Tuple[int, int]:
        """
        Get sequence progress for session.

        Args:
            session: Sequence session

        Returns:
            Tuple of (current_step, total_visible_steps)
        """
        if not session:
            return 0, 0

        visible_questions_count = self.get_visible_questions_count(session)
        return session.current_step, visible_questions_count

    def get_visible_questions_count(self, session: SequenceSession) -> int:
        """
        Get count of visible questions for the session.

        Args:
            session: Sequence session

        Returns:
            Number of visible questions
        """
        sequence_definition = self._sequence_provider.get_sequence_definition(
            session.sequence_name
        )
        if not sequence_definition:
            return 0

        visible_count = 0
        for question in sequence_definition.questions:
            # Check if question should be shown based on current session state
            if self._sequence_provider.should_show_question(question, session):
                visible_count += 1

        return visible_count

    def is_complete(self, session: SequenceSession) -> bool:
        """
        Check if sequence is complete.

        Args:
            session: Sequence session

        Returns:
            True if sequence is complete
        """
        return session is not None and session.is_complete()

    def get_completion_percentage(self, session: SequenceSession) -> float:
        """
        Get completion percentage for session.

        Args:
            session: Sequence session

        Returns:
            Completion percentage (0.0 to 100.0)
        """
        if not session:
            return 0.0

        current_step, total_steps = self.get_progress(session)

        if total_steps == 0:
            return 0.0

        return (current_step / total_steps) * 100.0

    def get_remaining_questions_count(self, session: SequenceSession) -> int:
        """
        Get count of remaining questions in session.

        Args:
            session: Sequence session

        Returns:
            Number of remaining questions
        """
        if not session:
            return 0

        current_step, total_steps = self.get_progress(session)
        return max(0, total_steps - current_step)

    def is_first_question(self, session: SequenceSession) -> bool:
        """
        Check if current question is the first one.

        Args:
            session: Sequence session

        Returns:
            True if this is the first question
        """
        return session is not None and session.current_step == 0

    def is_last_question(self, session: SequenceSession) -> bool:
        """
        Check if current question is the last one.

        Args:
            session: Sequence session

        Returns:
            True if this is the last question
        """
        if not session:
            return False

        current_step, total_steps = self.get_progress(session)
        return current_step + 1 >= total_steps
