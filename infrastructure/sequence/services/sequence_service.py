"""Core sequence orchestration service."""

import time
from typing import Any, Mapping, Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, User

from core.sequence.protocols import (
    SequenceManagerProtocol,
    SequenceProviderProtocol,
    SequenceQuestionRendererProtocol,
    SequenceResultHandlerProtocol,
    SequenceServiceProtocol,
    TranslatorProtocol,
)
from core.sequence.types import (
    QuestionType,
    SequenceAnswer,
    SequenceQuestion,
    SequenceSession,
    SequenceStatus,
)
from core.utils.logger import get_logger

logger = get_logger()


class SequenceService(SequenceServiceProtocol):
    """Core sequence orchestration service."""

    def __init__(
        self,
        session_manager: SequenceManagerProtocol,
        sequence_provider: SequenceProviderProtocol,
        question_renderer: SequenceQuestionRendererProtocol | None = None,
        result_handler: SequenceResultHandlerProtocol | None = None,
    ):
        """Initialize sequence service with dependency injection."""
        self._session_manager = session_manager
        self._sequence_provider = sequence_provider
        self._question_renderer = question_renderer
        self._result_handler = result_handler

    def start_sequence(self, user_id: int, sequence_name: str) -> str:
        """Start a new sequence session."""
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
        """Get current session for user."""
        return self._session_manager.get_session(user_id)

    def process_answer(
        self,
        user_id: int,
        answer_text: str,
        user: User,
        question_key: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Process user's answer to current question."""
        session = self._session_manager.get_session(user_id)
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

        # Validate answer
        is_valid, error_message = self._validate_answer(current_question, answer_text)
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

        # Get next question key (this will handle conditional logic)
        updated_session = self._session_manager.get_session(user_id)
        next_question_key = self._sequence_provider.get_next_question_key(
            updated_session
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
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        user_id: Optional[int] = None,
    ) -> bool:
        """Send question to user via platform."""
        # Use provided user_id or fallback to message.from_user.id
        target_user_id = user_id or message.from_user.id

        session = self._session_manager.get_session(target_user_id)
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

        try:
            question_text, keyboard = await self._render_question(
                question, session, translator, context, show_progress
            )

            # Send question
            if self._question_renderer:
                # Use renderer's platform-specific sending method
                success = await self._question_renderer.send_question_message(
                    message, question_text, keyboard, edit_existing=False
                )
                if not success:
                    raise Exception("Failed to send question via renderer")
            else:
                # Fallback to default sending
                if keyboard:
                    await message.answer(question_text, reply_markup=keyboard)
                else:
                    await message.answer(question_text)

            logger.debug(f"Sent question {question.key} to user {message.from_user.id}")
            return True

        except Exception as e:
            logger.error(
                f"Error sending question {question.key} to user {message.from_user.id}: {e}"
            )
            await message.answer(
                translator.translate("sequence.errors.send_question_failed", context)
            )
            return False

    async def edit_question(
        self,
        message: Message,
        question_key: str,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        user_id: Optional[int] = None,
    ) -> bool:
        """Edit existing message with new question (for callback queries)."""
        # Use provided user_id or fallback to message.from_user.id
        target_user_id = user_id or message.from_user.id

        session = self._session_manager.get_session(target_user_id)
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

        try:
            question_text, keyboard = await self._render_question(
                question, session, translator, context, show_progress
            )

            # Edit the message
            if self._question_renderer:
                # Use renderer's platform-specific sending method
                success = await self._question_renderer.send_question_message(
                    message, question_text, keyboard, edit_existing=True
                )
                if not success:
                    raise Exception("Failed to edit question via renderer")
            else:
                # Fallback to default editing
                if keyboard:
                    await message.edit_text(question_text, reply_markup=keyboard)
                else:
                    await message.edit_text(question_text)

            logger.debug(
                f"Edited question {question.key} for user {message.from_user.id}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Error editing question {question.key} for user {message.from_user.id}: {e}"
            )
            await message.answer(
                translator.translate("sequence.errors.send_question_failed", context)
            )
            return False

    def get_current_question_key(self, user_id: int) -> Optional[str]:
        """Get current question key for user's active session."""
        session = self._session_manager.get_session(user_id)
        if not session or session.status != SequenceStatus.ACTIVE:
            return None

        return self._sequence_provider.get_next_question_key(session)

    def is_sequence_complete(self, user_id: int) -> bool:
        """Check if user's current sequence is complete."""
        session = self._session_manager.get_session(user_id)
        return session is not None and session.is_complete()

    def get_sequence_progress(self, user_id: int) -> Tuple[int, int]:
        """Get sequence progress for user."""
        session = self._session_manager.get_session(user_id)
        if not session:
            return 0, 0

        visible_questions_count = self._get_visible_questions_count(session)
        return session.current_step, visible_questions_count

    def get_visible_questions_count(self, session: SequenceSession) -> int:
        """Get count of visible questions for the session."""
        return self._get_visible_questions_count(session)

    async def send_completion_message(
        self,
        message: Message,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        """Send completion message and summary."""
        try:
            completion_text = await self._render_completion_message(
                session, translator, context
            )

            # Send completion message
            if self._question_renderer:
                # Use renderer's platform-specific sending method
                success = await self._question_renderer.send_completion_message(
                    message, completion_text
                )
                if not success:
                    raise Exception("Failed to send completion message via renderer")
            else:
                # Fallback to default sending
                await message.answer(completion_text)

            # Handle sequence completion with custom result handler
            if self._result_handler:
                await self._result_handler.handle_sequence_completion(
                    session, message.from_user
                )

            logger.info(
                f"Sent completion message for sequence {session.sequence_name} to user {message.from_user.id}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Error sending completion message to user {message.from_user.id}: {e}"
            )
            await message.answer(
                translator.translate("sequence.errors.completion_failed", context)
            )
            return False

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

    def _get_visible_questions_count(self, session: SequenceSession) -> int:
        """Get count of visible questions for the session."""
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

    def _validate_answer(
        self,
        question: SequenceQuestion,
        answer_text: str,
    ) -> Tuple[bool, Optional[str]]:
        """Validate user's answer to a question."""
        # This is a simplified validation - can be extended based on question type
        if not answer_text or not answer_text.strip():
            return False, "Answer cannot be empty"

        # Additional validation logic can be added here based on question type
        return True, None

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

    async def _render_question(
        self,
        question: SequenceQuestion,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
    ) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """Render question text and keyboard."""
        # Use custom renderer if available
        if self._question_renderer:
            visible_questions_count = (
                self._get_visible_questions_count(session) if show_progress else None
            )
            return await self._question_renderer.render_question(
                question,
                session,
                translator,
                context,
                show_progress,
                visible_questions_count,
            )
        else:
            return await self._default_render_question(
                question, session, translator, context, show_progress
            )

    async def _default_render_question(
        self,
        question: SequenceQuestion,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
    ) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """Default question rendering implementation."""
        # Build question text
        if question.question_text:
            question_text = question.question_text
        elif question.question_text_key:
            # Use translator with context - translator handles parameter extraction
            question_text = translator.translate(question.question_text_key, context)
        else:
            question_text = f"Question: {question.key}"

        # Add progress indicator
        if show_progress:
            visible_questions_count = self._get_visible_questions_count(session)
            progress = f"[{session.current_step + 1}/{visible_questions_count}] "
            question_text = progress + question_text

        # Add help text if available
        if question.help_text:
            question_text += f"\n\n💡 {question.help_text}"

        # Generate keyboard for choice questions
        keyboard = None
        if (
            question.question_type in [QuestionType.SINGLE_CHOICE, QuestionType.BOOLEAN]
            and question.options
        ):
            keyboard_buttons = []
            for option in question.options:
                # Get label text (either direct or from localization)
                if option.label:
                    label = option.label
                elif option.label_key:
                    label = translator.translate(option.label_key, context)
                else:
                    label = option.value

                # Add emoji if available
                if option.emoji:
                    label = f"{option.emoji} {label}"

                button = InlineKeyboardButton(
                    text=label,
                    callback_data=f"sequence_answer:{question.key}:{option.value}",
                )
                keyboard_buttons.append([button])

            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        return question_text, keyboard

    async def _render_completion_message(
        self,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """Render completion message text."""
        # Get sequence definition for additional context
        sequence_definition = self._sequence_provider.get_sequence_definition(
            session.sequence_name
        )

        # Use custom renderer if available
        if self._question_renderer:
            return await self._question_renderer.render_completion_message(
                session, sequence_definition, translator, context
            )
        else:
            return await self._default_render_completion(
                session, translator, context, sequence_definition
            )

    async def _default_render_completion(
        self,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        sequence_definition: Optional[Any] = None,
    ) -> str:
        """Default completion message rendering implementation."""
        sequence_name = session.sequence_name.replace("_", " ").title()

        base_message = translator.translate(
            "sequence.completion.generic", context, sequence_type=sequence_name
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
