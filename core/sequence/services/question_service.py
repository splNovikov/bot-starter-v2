"""
Sequence question handling service.

Handles question rendering, validation, and platform-specific sending,
following the Single Responsibility Principle.
"""

from typing import Any, Mapping, Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from core.di.protocols import Injectable
from core.utils.logger import get_logger

from ..protocols import (
    SequenceProviderProtocol,
    SequenceQuestionRendererProtocol,
    SequenceQuestionServiceProtocol,
    TranslatorProtocol,
)
from ..types import QuestionType, SequenceQuestion, SequenceSession

logger = get_logger()


class SequenceQuestionService(SequenceQuestionServiceProtocol, Injectable):
    """
    Service for handling sequence questions.

    Provides question rendering, validation, and platform-specific sending
    with customizable rendering through optional renderer injection.
    """

    def __init__(
        self,
        sequence_provider: SequenceProviderProtocol,
        question_renderer: Optional[SequenceQuestionRendererProtocol] = None,
    ):
        """
        Initialize question service with dependencies.

        Args:
            sequence_provider: Sequence provision implementation
            question_renderer: Optional custom question renderer
        """
        self._sequence_provider = sequence_provider
        self._question_renderer = question_renderer

    async def send_question(
        self,
        message: Message,
        question: SequenceQuestion,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        visible_questions_count: Optional[int] = None,
    ) -> bool:
        """
        Send question to user via platform.

        Args:
            message: Message object for reply
            question: Question to send
            session: Current session
            translator: Translation service
            context: Optional context for localization
            show_progress: Whether to show progress indicator
            visible_questions_count: Number of visible questions for progress

        Returns:
            True if question was sent successfully
        """
        try:
            question_text, keyboard = await self.render_question(
                question,
                session,
                translator,
                context,
                show_progress,
                visible_questions_count,
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
        question: SequenceQuestion,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        visible_questions_count: Optional[int] = None,
    ) -> bool:
        """
        Edit existing message with new question.

        Args:
            message: Message object to edit
            question: Question to display
            session: Current session
            translator: Translation service
            context: Optional context for localization
            show_progress: Whether to show progress indicator
            visible_questions_count: Number of visible questions for progress

        Returns:
            True if question was edited successfully
        """
        try:
            question_text, keyboard = await self.render_question(
                question,
                session,
                translator,
                context,
                show_progress,
                visible_questions_count,
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

    async def render_question(
        self,
        question: SequenceQuestion,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        visible_questions_count: Optional[int] = None,
    ) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """
        Render question text and keyboard.

        Args:
            question: Question to render
            session: Current session
            translator: Translation service
            context: Optional context for localization
            show_progress: Whether to show progress indicator
            visible_questions_count: Number of visible questions for progress

        Returns:
            Tuple of (question_text, keyboard)
        """
        # Use custom renderer if available
        if self._question_renderer:
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
                question,
                session,
                translator,
                context,
                show_progress,
                visible_questions_count,
            )

    def validate_answer(
        self,
        question: SequenceQuestion,
        answer_text: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate user's answer to a question.

        Args:
            question: Question being answered
            answer_text: User's answer text

        Returns:
            Tuple of (is_valid, error_message)
        """
        # This is a simplified validation - can be extended based on question type
        if not answer_text or not answer_text.strip():
            return False, "Answer cannot be empty"

        # Additional validation logic can be added here based on question type
        return True, None

    async def _default_render_question(
        self,
        question: SequenceQuestion,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        visible_questions_count: Optional[int] = None,
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
        if show_progress and visible_questions_count is not None:
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
