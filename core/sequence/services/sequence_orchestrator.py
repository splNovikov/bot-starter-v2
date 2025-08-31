"""
Sequence orchestration service.

Coordinates between specialized sequence services following SOLID principles
and dependency inversion for maximum flexibility and maintainability.
"""

import time
from typing import Any, Mapping, Optional, Tuple

from aiogram.types import Message, User

from core.di.protocols import Injectable
from core.utils.logger import get_logger

from ..protocols import (
    SequenceCompletionServiceProtocol,
    SequenceProgressServiceProtocol,
    SequenceProviderProtocol,
    SequenceQuestionServiceProtocol,
    SequenceSessionServiceProtocol,
    TranslatorProtocol,
)
from ..types import SequenceAnswer, SequenceQuestion, SequenceSession, SequenceStatus

logger = get_logger()


class SequenceOrchestrator(Injectable):
    """
    Sequence orchestration service.

    Coordinates between specialized services following the Single Responsibility
    Principle and dependency inversion principle for better maintainability.
    """

    def __init__(
        self,
        session_service: SequenceSessionServiceProtocol,
        question_service: SequenceQuestionServiceProtocol,
        progress_service: SequenceProgressServiceProtocol,
        completion_service: SequenceCompletionServiceProtocol,
        sequence_provider: SequenceProviderProtocol,
    ):
        """
        Initialize sequence service with specialized service dependencies.

        Args:
            session_service: Session management service
            question_service: Question handling service
            progress_service: Progress tracking service
            completion_service: Completion handling service
            sequence_provider: Sequence provision implementation
        """
        self._session_service = session_service
        self._question_service = question_service
        self._progress_service = progress_service
        self._completion_service = completion_service
        self._sequence_provider = sequence_provider

    def start_sequence(self, user_id: int, sequence_name: str) -> str:
        """
        Start a new sequence session.

        Args:
            user_id: User identifier
            sequence_name: Name of the sequence to start

        Returns:
            Session ID
        """
        return self._session_service.start_session(user_id, sequence_name)

    def get_session(self, user_id: int) -> Optional[SequenceSession]:
        """
        Get current session for user.

        Args:
            user_id: User identifier

        Returns:
            SequenceSession object or None
        """
        return self._session_service.get_session(user_id)

    def process_answer(
        self,
        user_id: int,
        answer_text: str,
        user: User,
        question_key: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process user's answer to current question.

        Args:
            user_id: User identifier
            answer_text: User's answer text
            user: User object
            question_key: Optional specific question key to answer (for callbacks)

        Returns:
            Tuple of (success, error_message, next_question_key)
        """
        session = self._session_service.get_session(user_id)
        if not session or session.status != SequenceStatus.ACTIVE:
            return False, "No active sequence session found", None

        # Get the question to answer
        if question_key:
            # Use the specific question key (for callbacks)
            sequence_definition = self._sequence_provider.get_sequence_definition(
                session.sequence_name
            )
            if not sequence_definition:
                return False, "Sequence definition not found", None
            current_question = sequence_definition.get_question_by_key(question_key)
            if not current_question:
                return False, f"Question '{question_key}' not found", None
        else:
            # Use current question based on session step
            current_question = self._get_current_question(session)
            if not current_question:
                return False, "No current question found", None

        # Validate answer using question service
        is_valid, error_message = self._question_service.validate_answer(
            current_question, answer_text
        )

        if not is_valid:
            return False, error_message, current_question.key

        # Create answer object
        answer = SequenceAnswer(
            question_key=current_question.key,
            answer_value=answer_text,
            answered_at=time.time(),
        )

        # For scored sequences, check correctness and calculate score
        sequence_definition = self._sequence_provider.get_sequence_definition(
            session.sequence_name
        )
        if (
            sequence_definition
            and sequence_definition.scored
            and current_question.correct_answer
        ):
            answer.is_correct = self._check_correct_answer(
                current_question, answer_text
            )
            if answer.is_correct and current_question.points:
                answer.points_earned = current_question.points
            else:
                answer.points_earned = 0

        # Add answer to session
        success = self._session_service.add_answer(user_id, answer)
        if not success:
            return False, "Failed to save answer", current_question.key

        # Advance to next step
        self._session_service.advance_step(user_id)

        # Get next question key (this will handle conditional logic)
        updated_session = self._session_service.get_session(user_id)
        next_question_key = self._sequence_provider.get_next_question_key(
            updated_session
        )

        # Check if sequence is complete
        if not next_question_key:
            self._session_service.complete_session(user_id)
            logger.info(
                f"Completed sequence {session.sequence_name} for user {user_id}"
            )

        return True, None, next_question_key

    async def send_question(
        self,
        message: Message,
        question_key: str,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        user_id: Optional[int] = None,
    ) -> bool:
        """
        Send question to user via platform.

        Args:
            message: Message object for reply
            question_key: Question identifier
            translator: Translation service
            context: Optional context for localization
            show_progress: Whether to show progress indicator
            user_id: Optional user ID (if not provided, uses message.from_user.id)

        Returns:
            True if question was sent successfully
        """
        # Use provided user_id or fallback to message.from_user.id
        target_user_id = user_id or message.from_user.id

        session = self._session_service.get_session(target_user_id)
        if not session:
            await message.answer(
                translator.translate("sequence.errors.no_active_session", context)
            )
            return False

        # Get question from sequence definition
        sequence_definition = self._sequence_provider.get_sequence_definition(
            session.sequence_name
        )
        if not sequence_definition:
            await message.answer(
                translator.translate("sequence.errors.sequence_not_found", context)
            )
            return False

        question = sequence_definition.get_question_by_key(question_key)
        if not question:
            await message.answer(
                translator.translate("sequence.errors.question_not_found", context)
            )
            return False

        # Calculate visible questions count for progress
        visible_questions_count = (
            self._progress_service.get_visible_questions_count(session)
            if show_progress
            else None
        )

        return await self._question_service.send_question(
            message,
            question,
            session,
            translator,
            context,
            show_progress,
            visible_questions_count,
        )

    async def edit_question(
        self,
        message: Message,
        question_key: str,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        user_id: Optional[int] = None,
    ) -> bool:
        """
        Edit existing message with new question (for callback queries).

        Args:
            message: Message object to edit
            question_key: Question identifier
            translator: Translation service
            context: Optional context for localization
            show_progress: Whether to show progress indicator
            user_id: Optional user ID (if not provided, uses message.from_user.id)

        Returns:
            True if question was edited successfully
        """
        # Use provided user_id or fallback to message.from_user.id
        target_user_id = user_id or message.from_user.id

        session = self._session_service.get_session(target_user_id)
        if not session:
            await message.answer(
                translator.translate("sequence.errors.no_active_session", context)
            )
            return False

        # Get question from sequence definition
        sequence_definition = self._sequence_provider.get_sequence_definition(
            session.sequence_name
        )
        if not sequence_definition:
            await message.answer(
                translator.translate("sequence.errors.sequence_not_found", context)
            )
            return False

        question = sequence_definition.get_question_by_key(question_key)
        if not question:
            await message.answer(
                translator.translate("sequence.errors.question_not_found", context)
            )
            return False

        # Calculate visible questions count for progress
        visible_questions_count = (
            self._progress_service.get_visible_questions_count(session)
            if show_progress
            else None
        )

        return await self._question_service.edit_question(
            message,
            question,
            session,
            translator,
            context,
            show_progress,
            visible_questions_count,
        )

    async def send_completion_message(
        self,
        message: Message,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        """
        Send completion message and summary.

        Args:
            message: Message object for reply
            session: Completed session
            translator: Translation service
            context: Optional context for localization

        Returns:
            True if message was sent successfully
        """
        # Send completion message
        success = await self._completion_service.send_completion_message(
            message, session, translator, context
        )

        if success:
            # Handle sequence completion
            await self._completion_service.handle_completion(session, message.from_user)

        return success

    def get_current_question_key(self, user_id: int) -> Optional[str]:
        """
        Get current question key for user's active session.

        Args:
            user_id: User identifier

        Returns:
            Current question key or None
        """
        session = self._session_service.get_session(user_id)
        if not session or session.status != SequenceStatus.ACTIVE:
            return None

        return self._sequence_provider.get_next_question_key(session)

    def is_sequence_complete(self, user_id: int) -> bool:
        """
        Check if user's current sequence is complete.

        Args:
            user_id: User identifier

        Returns:
            True if sequence is complete
        """
        session = self._session_service.get_session(user_id)
        return self._progress_service.is_complete(session)

    def get_sequence_progress(self, user_id: int) -> Tuple[int, int]:
        """
        Get sequence progress for user.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (current_step, total_visible_steps)
        """
        session = self._session_service.get_session(user_id)
        if not session:
            return 0, 0

        return self._progress_service.get_progress(session)

    def get_visible_questions_count(self, session: SequenceSession) -> int:
        """
        Get count of visible questions for the session.

        Args:
            session: Sequence session

        Returns:
            Number of visible questions
        """
        return self._progress_service.get_visible_questions_count(session)

    # Private helper methods

    def _get_current_question(
        self, session: SequenceSession
    ) -> Optional[SequenceQuestion]:
        """Get current question for session."""
        sequence_definition = self._sequence_provider.get_sequence_definition(
            session.sequence_name
        )
        if not sequence_definition:
            return None

        return self._sequence_provider.get_current_question(
            session.sequence_name, session.current_step
        )

    def _check_correct_answer(
        self, question: SequenceQuestion, answer_text: str
    ) -> bool:
        """Check if answer is correct for scored sequences."""
        if not question.correct_answer:
            return False

        # Handle different answer types
        if isinstance(question.correct_answer, list):
            # Multiple correct answers
            return answer_text.lower().strip() in [
                a.lower().strip() for a in question.correct_answer
            ]
        else:
            # Single correct answer
            return (
                answer_text.lower().strip() == question.correct_answer.lower().strip()
            )
