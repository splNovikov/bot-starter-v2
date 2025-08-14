"""
Button question renderer for sequence framework.

Provides rendering of sequence questions with inline keyboard buttons
for choice-based questions and custom completion messages.
"""

from typing import Any, Mapping, Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.sequence.protocols import SequenceQuestionRendererProtocol, TranslatorProtocol
from core.sequence.types import (
    QuestionType,
    SequenceDefinition,
    SequenceQuestion,
    SequenceSession,
)
from core.utils.logger import get_logger

logger = get_logger()


class ButtonQuestionRenderer(SequenceQuestionRendererProtocol):
    """
    Button question renderer implementation.

    Renders sequence questions with inline keyboard buttons for choice-based questions
    and provides custom completion message formatting with localization support.
    """

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
            question: SequenceQuestion to render
            session: Current session for context
            translator: Translation service
            context: Optional context for localization
            show_progress: Whether to include progress indicator
            visible_questions_count: Number of visible questions for progress calculation

        Returns:
            Tuple of (message_text, keyboard_markup)
        """
        # Build question text using localization
        question_text = self._get_localized_text(
            question.question_text_key or "question.text",
            translator,
            context,
        )

        # Add progress indicator if requested
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
            keyboard = self._create_choice_keyboard(
                question, session, translator, context
            )

        return question_text, keyboard

    async def render_completion_message(
        self,
        session: SequenceSession,
        sequence_definition: SequenceDefinition,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        Render sequence completion message.

        Args:
            session: Completed session
            sequence_definition: Sequence definition
            translator: Translation service
            context: Optional context for localization

        Returns:
            Formatted completion message
        """
        # Get the completion message template using localization
        completion_template = self._get_localized_text(
            sequence_definition.completion_message_key or "sequence.completion",
            translator,
            context,
        )

        # For single question sequences, replace placeholders
        if sequence_definition.is_single_question():
            return self._render_single_question_completion(completion_template)

        # For multi-question sequences, generate summary
        return self._render_multi_question_completion(
            session, sequence_definition, completion_template, translator, context
        )

    async def send_question_message(
        self, message, question_text: str, keyboard=None, edit_existing: bool = False
    ) -> bool:
        """
        Send or edit a question message with proper Telegram formatting.

        Args:
            message: Telegram message object
            question_text: Text of the question
            keyboard: Optional keyboard markup
            edit_existing: Whether to edit existing message or send new one

        Returns:
            True if message was sent/edited successfully
        """
        try:
            if edit_existing:
                if keyboard:
                    await message.edit_text(
                        question_text, reply_markup=keyboard, parse_mode="HTML"
                    )
                else:
                    await message.edit_text(question_text, parse_mode="HTML")
            else:
                if keyboard:
                    await message.answer(
                        question_text, reply_markup=keyboard, parse_mode="HTML"
                    )
                else:
                    await message.answer(question_text, parse_mode="HTML")
            return True
        except Exception as e:
            logger.error(f"Error sending/editing question message: {e}")
            return False

    async def send_completion_message(self, message, completion_text: str) -> bool:
        """
        Send completion message with proper Telegram formatting.

        Args:
            message: Telegram message object
            completion_text: Completion message text

        Returns:
            True if message was sent successfully
        """
        try:
            await message.answer(completion_text, parse_mode="HTML")
            return True
        except Exception as e:
            logger.error(f"Error sending completion message: {e}")
            return False

    def _create_choice_keyboard(
        self,
        question: SequenceQuestion,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> InlineKeyboardMarkup:
        """
        Create inline keyboard for choice questions.

        Args:
            question: Question with options
            session: Current session
            translator: Translation service
            context: Optional context for localization

        Returns:
            InlineKeyboardMarkup with choice buttons
        """
        buttons = []

        for option in question.options:
            # Create button text with emoji if available, using localization
            button_text = self._get_localized_text(
                option.label_key or f"option.{option.value}", translator, context
            )

            if option.emoji:
                button_text = f"{option.emoji} {button_text}"

            # Create callback data
            callback_data = (
                f"seq_answer:{session.sequence_name}:{question.key}:{option.value}"
            )

            # Add button to list
            buttons.append(
                InlineKeyboardButton(text=button_text, callback_data=callback_data)
            )

        # Create keyboard with buttons arranged in rows of 2
        keyboard_buttons = []
        for i in range(0, len(buttons), 2):
            row = buttons[i : i + 2]
            keyboard_buttons.append(row)

        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    def _render_single_question_completion(
        self,
        template: str,
    ) -> str:
        """
        Render completion message for single-question sequences.

        Args:
            template: Completion message template

        Returns:
            Formatted completion message
        """
        # For single-question sequences, just return the template
        return template

    def _render_multi_question_completion(
        self,
        session: SequenceSession,
        sequence_definition: SequenceDefinition,
        template: str,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        Render completion message for multi-question sequences.

        Args:
            session: Completed session
            sequence_definition: Sequence definition
            template: Completion message template
            translator: Translation service
            context: Optional context for localization

        Returns:
            Formatted completion message
        """
        # Start with the template
        message = template + "\n\n"

        # Add summary of answers
        for question in sequence_definition.questions:
            answer = session.get_answer(question.key)
            if answer:
                # Get display value for the answer
                display_value = self._get_display_value(
                    question, answer.answer_value, translator, context
                )
                question_text = question.question_text or self._get_localized_text(
                    question.question_text_key or f"question.{question.key}",
                    translator,
                    context,
                )
                message += f"• {question_text} {display_value}\n"

        return message

    def _get_display_value(
        self,
        question: SequenceQuestion,
        answer_value: str,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        Get display value for an answer.

        Args:
            question: Question that was answered
            answer_value: Raw answer value
            translator: Translation service
            context: Optional context for localization

        Returns:
            Display value with emoji if available
        """
        # For choice questions, get the label from options
        if question.question_type == QuestionType.SINGLE_CHOICE and question.options:
            for option in question.options:
                if option.value == answer_value:
                    display_text = self._get_localized_text(
                        option.label_key or f"option.{option.value}",
                        translator,
                        context,
                    )
                    if option.emoji:
                        display_text = f"{option.emoji} {display_text}"
                    return display_text

        # For other question types, return the raw value
        return answer_value

    def _get_localized_text(
        self,
        key: str,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        Get localized text using translator.

        Args:
            key: Translation key
            translator: Translation service
            context: Optional context for localization

        Returns:
            Localized text
        """
        try:
            return translator.translate(key, context)
        except Exception as e:
            logger.error(f"Failed to translate key '{key}': {e}")
            return f"Error: {key}"
