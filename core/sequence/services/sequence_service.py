"""
Core sequence orchestration service.

Coordinates between session management, sequence provision, and integration
using the framework protocols for maximum flexibility and reusability.
"""

import time
from typing import Any, Optional, Tuple

from aiogram.types import InlineKeyboardMarkup, Message, User

from core.services.localization import t
from core.utils.logger import get_logger

from ..protocols import (
    SequenceManagerProtocol,
    SequenceProviderProtocol,
    SequenceQuestionRendererProtocol,
    SequenceResultHandlerProtocol,
    SequenceServiceProtocol,
)
from ..types import SequenceAnswer, SequenceQuestion, SequenceSession, SequenceStatus

logger = get_logger()


class SequenceService(SequenceServiceProtocol):
    """
    Core sequence orchestration service.

    Coordinates between session management, sequence provision, and integration
    following the dependency inversion principle for maximum flexibility.
    """

    def __init__(
        self,
        session_manager: SequenceManagerProtocol,
        sequence_provider: SequenceProviderProtocol,
        question_renderer: Optional[SequenceQuestionRendererProtocol] = None,
        result_handler: Optional[SequenceResultHandlerProtocol] = None,
    ):
        """
        Initialize sequence service with dependency injection.

        Args:
            session_manager: Session management implementation
            sequence_provider: Sequence provision implementation
            question_renderer: Optional question rendering implementation
            result_handler: Optional result handling implementation
        """
        self._session_manager = session_manager
        self._sequence_provider = sequence_provider
        self._question_renderer = question_renderer
        self._result_handler = result_handler

    def start_sequence(self, user_id: int, sequence_name: str) -> str:
        """
        Start a new sequence session.

        Args:
            user_id: User identifier
            sequence_name: Name of the sequence to start

        Returns:
            Session ID
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

    def process_answer(
        self, user_id: int, answer_text: str, user: User
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process user's answer to current question.

        Args:
            user_id: User identifier
            answer_text: User's answer text
            user: User object

        Returns:
            Tuple of (success, error_message, next_question_key)
        """
        session = self._session_manager.get_session(user_id)
        if not session or session.status != SequenceStatus.ACTIVE:
            return False, "No active sequence session found", None

        # Get current question
        current_question = self._get_current_question(session)
        if not current_question:
            return False, "No current question found", None

        # Validate answer
        is_valid, error_message = self._sequence_provider.validate_answer(
            session.sequence_name, current_question.key, answer_text
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
        success = self._session_manager.add_answer(user_id, answer)
        if not success:
            return False, "Failed to save answer", current_question.key

        # Advance to next step
        self._session_manager.advance_step(user_id)

        # Get next question key
        updated_session = self._session_manager.get_session(user_id)
        next_question_key = self._sequence_provider.get_next_question_key(
            updated_session, user
        )

        # Check if sequence is complete
        if not next_question_key:
            self._session_manager.complete_session(user_id)
            logger.info(
                f"Completed sequence {session.sequence_name} for user {user_id}"
            )

        return True, None, next_question_key

    async def send_question(
        self,
        message: Message,
        question_key: str,
        user: User,
        show_progress: bool = True,
    ) -> bool:
        """
        Send question to user via Telegram.

        Args:
            message: Message object for reply
            question_key: Question identifier
            user: User object
            show_progress: Whether to show progress indicator

        Returns:
            True if question was sent successfully
        """
        session = self._session_manager.get_session(user.id)
        if not session:
            await message.answer(t("sequence.errors.no_active_session", user=user))
            return False

        # Get question from sequence definition
        sequence_definition = self._sequence_provider.get_sequence_definition(
            session.sequence_name
        )
        if not sequence_definition:
            await message.answer(t("sequence.errors.sequence_not_found", user=user))
            return False

        question = sequence_definition.get_question_by_key(question_key)
        if not question:
            await message.answer(t("sequence.errors.question_not_found", user=user))
            return False

        try:
            # Use custom renderer if available
            if self._question_renderer:
                question_text, keyboard = await self._question_renderer.render_question(
                    question, session, show_progress, user
                )
            else:
                question_text, keyboard = await self._default_render_question(
                    question, session, show_progress
                )

            # Send question
            if keyboard:
                await message.answer(question_text, reply_markup=keyboard)
            else:
                await message.answer(question_text)

            logger.debug(f"Sent question {question_key} to user {user.id}")
            return True

        except Exception as e:
            logger.error(
                f"Error sending question {question_key} to user {user.id}: {e}"
            )
            await message.answer(t("sequence.errors.send_question_failed", user=user))
            return False

    async def send_completion_message(
        self, message: Message, session: SequenceSession, user: User
    ) -> bool:
        """
        Send completion message and summary.

        Args:
            message: Message object for reply
            session: Completed session
            user: User object

        Returns:
            True if message was sent successfully
        """
        try:
            sequence_definition = self._sequence_provider.get_sequence_definition(
                session.sequence_name
            )

            # Use custom renderer if available
            if self._question_renderer:
                completion_text = (
                    await self._question_renderer.render_completion_message(
                        session, sequence_definition, user
                    )
                )
            else:
                completion_text = await self._default_render_completion(
                    session, user, sequence_definition
                )

            await message.answer(completion_text)

            # Handle sequence completion with custom result handler
            if self._result_handler:
                await self._result_handler.handle_sequence_completion(session, user)

            logger.info(
                f"Sent completion message for sequence {session.sequence_name} to user {user.id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending completion message to user {user.id}: {e}")
            await message.answer(t("sequence.errors.completion_failed", user=user))
            return False

    def get_current_question_key(self, user_id: int, user: User) -> Optional[str]:
        """
        Get current question key for user's active session.

        Args:
            user_id: User identifier
            user: User object

        Returns:
            Current question key or None
        """
        session = self._session_manager.get_session(user_id)
        if not session or session.status != SequenceStatus.ACTIVE:
            return None

        return self._sequence_provider.get_next_question_key(session, user)

    def is_sequence_complete(self, user_id: int) -> bool:
        """
        Check if user's current sequence is complete.

        Args:
            user_id: User identifier

        Returns:
            True if sequence is complete
        """
        session = self._session_manager.get_session(user_id)
        return session is not None and session.is_complete()

    def get_sequence_progress(self, user_id: int) -> Tuple[int, int]:
        """
        Get sequence progress for user.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (current_step, total_steps)
        """
        session = self._session_manager.get_session(user_id)
        if not session:
            return 0, 0

        return session.current_step, session.total_questions or 0

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

    async def _default_render_question(
        self, question: SequenceQuestion, session: SequenceSession, show_progress: bool
    ) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """Default question rendering."""
        # Build question text
        question_text = question.question_text

        # Add progress indicator
        if show_progress and session.total_questions:
            progress = f"[{session.current_step + 1}/{session.total_questions}] "
            question_text = progress + question_text

        # Add help text if available
        if question.help_text:
            question_text += f"\n\n💡 {question.help_text}"

        # TODO: Add keyboard generation for choice questions
        keyboard = None

        return question_text, keyboard

    async def _default_render_completion(
        self,
        session: SequenceSession,
        user: User,
        sequence_definition: Optional[Any] = None,
    ) -> str:
        """Default completion message rendering."""
        sequence_name = session.sequence_name.replace("_", " ").title()

        base_message = t(
            "sequence.completion.generic", user=user, sequence_type=sequence_name
        )

        # Add scoring information for scored sequences
        if (
            sequence_definition
            and sequence_definition.scored
            and session.total_score is not None
        ):
            base_message += (
                f"\n\n🎯 Score: {session.total_score}/{session.max_possible_score or 0}"
            )

            # Add percentage if possible
            if session.max_possible_score and session.max_possible_score > 0:
                percentage = (session.total_score / session.max_possible_score) * 100
                base_message += f" ({percentage:.1f}%)"

        return base_message


__all__ = ["SequenceService"]
