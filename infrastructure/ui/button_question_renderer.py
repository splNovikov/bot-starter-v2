"""
Button question renderer for sequence framework.

Provides rendering of sequence questions with inline keyboard buttons
for choice-based questions and custom completion messages.
"""

from typing import Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, User

from core.sequence.protocols import SequenceQuestionRendererProtocol
from core.sequence.types import (
    QuestionType,
    SequenceDefinition,
    SequenceQuestion,
    SequenceSession,
)
from core.services.localization import t
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
        show_progress: bool = True,
        user: Optional[User] = None,
    ) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """
        Render question text and keyboard.

        Args:
            question: SequenceQuestion to render
            session: Current session for context
            show_progress: Whether to include progress indicator
            user: User object for localization context

        Returns:
            Tuple of (message_text, keyboard_markup)
        """
        # Build question text using localization
        question_text = self._get_localized_text(
            question.question_text_key,
            question.question_text,
            "Question text not found",
            user,
        )

        # Add progress indicator if requested
        if show_progress and session.total_questions:
            progress = f"[{session.current_step + 1}/{session.total_questions}] "
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
            keyboard = self._create_choice_keyboard(question, session, user)

        return question_text, keyboard

    async def render_completion_message(
        self,
        session: SequenceSession,
        sequence_definition: SequenceDefinition,
        user: Optional[User] = None,
    ) -> str:
        """
        Render sequence completion message.

        Args:
            session: Completed session
            sequence_definition: Sequence definition
            user: User object for localization context

        Returns:
            Formatted completion message
        """
        # Get the completion message template using localization
        completion_template = self._get_localized_text(
            sequence_definition.completion_message_key,
            sequence_definition.completion_message,
            "Sequence completed!",
            user,
        )

        # For single question sequences, replace placeholders
        if sequence_definition.is_single_question():
            return self._render_single_question_completion(
                session, completion_template, user
            )

        # For multi-question sequences, generate summary
        return self._render_multi_question_completion(
            session, sequence_definition, completion_template, user
        )

    def _create_choice_keyboard(
        self,
        question: SequenceQuestion,
        session: SequenceSession,
        user: Optional[User] = None,
    ) -> InlineKeyboardMarkup:
        """
        Create inline keyboard for choice questions.

        Args:
            question: Question with options
            session: Current session
            user: User object for localization context

        Returns:
            InlineKeyboardMarkup with choice buttons
        """
        buttons = []

        for option in question.options:
            # Create button text with emoji if available, using localization
            button_text = self._get_localized_text(
                option.label_key, option.label, option.value.title(), user
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
        self, session: SequenceSession, template: str, user: Optional[User] = None
    ) -> str:
        """
        Render completion message for single-question sequences.

        Args:
            session: Completed session
            template: Completion message template
            user: User object for localization context

        Returns:
            Formatted completion message
        """
        # Get the answer value
        # pnovikov: I commented the unused code
        # answer = list(session.answers.values())[0]
        # answer_value = answer.answer_value

        # Replace placeholders in template
        message = template

        return message

    def _render_multi_question_completion(
        self,
        session: SequenceSession,
        sequence_definition: SequenceDefinition,
        template: str,
        user: Optional[User] = None,
    ) -> str:
        """
        Render completion message for multi-question sequences.

        Args:
            session: Completed session
            sequence_definition: Sequence definition
            template: Completion message template
            user: User object for localization context

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
                    question, answer.answer_value, user
                )
                question_text = question.question_text or self._get_localized_text(
                    question.question_text_key, "", "Question", user
                )
                message += f"• {question_text} {display_value}\n"

        return message

    def _get_display_value(
        self, question: SequenceQuestion, answer_value: str, user: Optional[User] = None
    ) -> str:
        """
        Get display value for an answer.

        Args:
            question: Question that was answered
            answer_value: Raw answer value
            user: User object for localization context

        Returns:
            Display value with emoji if available
        """
        # For choice questions, get the label from options
        if question.question_type == QuestionType.SINGLE_CHOICE and question.options:
            for option in question.options:
                if option.value == answer_value:
                    display_text = self._get_localized_text(
                        option.label_key, option.label, option.value.title(), user
                    )
                    if option.emoji:
                        display_text = f"{option.emoji} {display_text}"
                    return display_text

        # For other question types, return the raw value
        return answer_value

    def _get_localized_text(
        self,
        key: Optional[str],
        fallback: Optional[str],
        default: str,
        user: Optional[User] = None,
    ) -> str:
        """
        Get localized text using key, fallback, or default.

        Args:
            key: Localization key
            fallback: Fallback text if key is not available
            default: Default text if neither key nor fallback is available
            user: User object for localization context

        Returns:
            Localized text
        """
        if key and user:
            try:
                return t(key, user=user)
            except:
                pass

        if fallback:
            return fallback

        return default
