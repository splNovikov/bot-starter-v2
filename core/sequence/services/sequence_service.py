"""Core sequence orchestration service."""

import time
from typing import Any, Mapping, Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, User

from core.utils.logger import get_logger

from ..protocols import (
    SequenceManagerProtocol,
    SequenceProviderProtocol,
    SequenceQuestionRendererProtocol,
    SequenceResultHandlerProtocol,
    SequenceServiceProtocol,
    TranslatorProtocol,
)
from ..types import (
    QuestionType,
    SequenceAnswer,
    SequenceQuestion,
    SequenceSession,
    SequenceStatus,
)

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

        existing_session = self._session_manager.get_session(user_id)
        if existing_session:
            self._session_manager.clear_session(user_id)

        session_id = self._session_manager.create_session(user_id, sequence_name)

        session = self._session_manager.get_session(user_id)
        if session:
            session.total_questions = len(sequence_definition.questions)
            session.metadata["sequence_definition"] = sequence_definition.name

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

        if question_key:
            sequence_definition = self._sequence_provider.get_sequence_definition(
                session.sequence_name
            )
            if not sequence_definition:
                return False, "Sequence definition not found", None
            current_question = sequence_definition.get_question_by_key(question_key)
            if not current_question:
                return False, f"Question '{question_key}' not found", None
        else:
            current_question = self._get_current_question(session)
            if not current_question:
                return False, "No current question found", None

        is_valid, error_message = self._sequence_provider.validate_answer(
            session.sequence_name, current_question.key, answer_text
        )

        if not is_valid:
            return False, error_message, current_question.key

        answer = SequenceAnswer(
            question_key=current_question.key,
            answer_value=answer_text,
            answered_at=time.time(),
        )

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

        success = self._session_manager.add_answer(user_id, answer)
        if not success:
            return False, "Failed to save answer", current_question.key

        self._session_manager.advance_step(user_id)

        updated_session = self._session_manager.get_session(user_id)
        next_question_key = self._sequence_provider.get_next_question_key(
            updated_session
        )

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
        target_user_id = user_id or message.from_user.id

        session = self._session_manager.get_session(target_user_id)
        if not session:
            await message.answer(
                translator.translate("sequence.errors.no_active_session", context)
            )
            return False

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
            visible_questions_count = (
                self.get_visible_questions_count(session) if show_progress else None
            )

            if self._question_renderer:
                question_text, keyboard = await self._question_renderer.render_question(
                    question,
                    session,
                    translator,
                    context,
                    show_progress,
                    visible_questions_count,
                )
            else:
                question_text, keyboard = await self._default_render_question(
                    question,
                    session,
                    translator,
                    context,
                    show_progress,
                    visible_questions_count,
                )

            if self._question_renderer:
                success = await self._question_renderer.send_question_message(
                    message, question_text, keyboard, edit_existing=False
                )
                if not success:
                    raise Exception("Failed to send question via renderer")
            else:
                if keyboard:
                    await message.answer(question_text, reply_markup=keyboard)
                else:
                    await message.answer(question_text)

            return True

        except Exception as e:
            logger.error(
                f"Error sending question {question_key} to user {target_user_id}: {e}"
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
        target_user_id = user_id or message.from_user.id

        session = self._session_manager.get_session(target_user_id)
        if not session:
            await message.answer(
                translator.translate("sequence.errors.no_active_session", context)
            )
            return False

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
            visible_questions_count = (
                self.get_visible_questions_count(session) if show_progress else None
            )

            if self._question_renderer:
                question_text, keyboard = await self._question_renderer.render_question(
                    question,
                    session,
                    translator,
                    context,
                    show_progress,
                    visible_questions_count,
                )
            else:
                question_text, keyboard = await self._default_render_question(
                    question,
                    session,
                    translator,
                    context,
                    show_progress,
                    visible_questions_count,
                )

            if self._question_renderer:
                success = await self._question_renderer.send_question_message(
                    message, question_text, keyboard, edit_existing=True
                )
                if not success:
                    raise Exception("Failed to edit question via renderer")
            else:
                if keyboard:
                    await message.edit_text(question_text, reply_markup=keyboard)
                else:
                    await message.edit_text(question_text)

            return True

        except Exception as e:
            logger.error(
                f"Error editing question {question_key} for user {target_user_id}: {e}"
            )
            await message.answer(
                translator.translate("sequence.errors.send_question_failed", context)
            )
            return False

    async def send_completion_message(
        self,
        message: Message,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        """Send completion message and summary."""
        try:
            sequence_definition = self._sequence_provider.get_sequence_definition(
                session.sequence_name
            )

            if self._question_renderer:
                completion_text = (
                    await self._question_renderer.render_completion_message(
                        session, sequence_definition, translator, context
                    )
                )
            else:
                completion_text = await self._default_render_completion(
                    session, translator, context, sequence_definition
                )

            if self._question_renderer:
                success = await self._question_renderer.send_completion_message(
                    message, completion_text
                )
                if not success:
                    raise Exception("Failed to send completion message via renderer")
            else:
                await message.answer(completion_text)

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
        sequence_definition = self._sequence_provider.get_sequence_definition(
            session.sequence_name
        )
        if not sequence_definition:
            return 0

        visible_count = 0
        for question in sequence_definition.questions:
            if self._sequence_provider.should_show_question(question, session):
                visible_count += 1

        return visible_count

    def _get_visible_questions_count(self, session: SequenceSession) -> int:
        """Get count of visible questions for the session (internal use)."""
        return self.get_visible_questions_count(session)

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

        if isinstance(question.correct_answer, list):
            return answer_text.lower().strip() in [
                a.lower().strip() for a in question.correct_answer
            ]
        else:
            return (
                answer_text.lower().strip() == question.correct_answer.lower().strip()
            )

    async def _default_render_question(
        self,
        question: SequenceQuestion,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        visible_questions_count: Optional[int] = None,
    ) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """Default question rendering."""
        if question.question_text:
            question_text = question.question_text
        elif question.question_text_key:
            question_text = translator.translate(question.question_text_key, context)
        else:
            question_text = f"Question: {question.key}"

        if show_progress and visible_questions_count is not None:
            progress = f"[{session.current_step + 1}/{visible_questions_count}] "
            question_text = progress + question_text

        if question.help_text:
            question_text += f"\n\n💡 {question.help_text}"

        keyboard = None
        if (
            question.question_type in [QuestionType.SINGLE_CHOICE, QuestionType.BOOLEAN]
            and question.options
        ):
            keyboard_buttons = []
            for option in question.options:
                if option.label:
                    label = option.label
                elif option.label_key:
                    label = translator.translate(option.label_key, context)
                else:
                    label = option.value

                if option.emoji:
                    label = f"{option.emoji} {label}"

                button = InlineKeyboardButton(
                    text=label,
                    callback_data=f"sequence_answer:{question.key}:{option.value}",
                )
                keyboard_buttons.append([button])

            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        return question_text, keyboard

    async def _default_render_completion(
        self,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        sequence_definition: Optional[Any] = None,
    ) -> str:
        """Default completion message rendering."""
        sequence_name = session.sequence_name.replace("_", " ").title()

        base_message = translator.translate(
            "sequence.completion.generic", context, sequence_type=sequence_name
        )

        if (
            sequence_definition
            and sequence_definition.scored
            and session.total_score is not None
        ):
            base_message += (
                f"\n\n🎯 Score: {session.total_score}/{session.max_possible_score or 0}"
            )

            if session.max_possible_score and session.max_possible_score > 0:
                percentage = (session.total_score / session.max_possible_score) * 100
                base_message += f" ({percentage:.1f}%)"

        return base_message


__all__ = ["SequenceService"]
