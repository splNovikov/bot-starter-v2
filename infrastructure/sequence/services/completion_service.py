"""
Sequence completion handling service.

Handles completion messages and result processing for finished sequences,
following the Single Responsibility Principle.
"""

from typing import Any, Mapping, Optional

from aiogram.types import Message, User

from core.di.protocols import Injectable
from core.sequence.protocols import (
    SequenceCompletionServiceProtocol,
    SequenceProviderProtocol,
    SequenceQuestionRendererProtocol,
    SequenceResultHandlerProtocol,
    TranslatorProtocol,
)
from core.sequence.types import SequenceSession
from core.utils.logger import get_logger

logger = get_logger()


class SequenceCompletionService(SequenceCompletionServiceProtocol, Injectable):
    """
    Service for handling sequence completion.

    Provides completion message rendering and result processing
    with customizable handling through optional handlers.
    """

    def __init__(
        self,
        sequence_provider: SequenceProviderProtocol,
        question_renderer: Optional[SequenceQuestionRendererProtocol] = None,
        result_handler: Optional[SequenceResultHandlerProtocol] = None,
    ):
        """
        Initialize completion service with dependencies.

        Args:
            sequence_provider: Sequence provision implementation
            question_renderer: Optional custom question renderer
            result_handler: Optional custom result handler
        """
        self._sequence_provider = sequence_provider
        self._question_renderer = question_renderer
        self._result_handler = result_handler

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
        try:
            completion_text = await self.render_completion_message(
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

    async def handle_completion(
        self,
        session: SequenceSession,
        user: User,
    ) -> bool:
        """
        Handle sequence completion with custom result handler.

        Args:
            session: Completed session
            user: User who completed the sequence

        Returns:
            True if completion was handled successfully
        """
        try:
            # Handle sequence completion with custom result handler
            if self._result_handler:
                await self._result_handler.handle_sequence_completion(session, user)

            logger.info(
                f"Handled completion for sequence {session.sequence_name} by user {user.id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error handling completion for user {user.id}: {e}")
            return False

    async def render_completion_message(
        self,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        Render completion message text.

        Args:
            session: Completed session
            translator: Translation service
            context: Optional context for localization

        Returns:
            Completion message text
        """
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

    def get_completion_summary(self, session: SequenceSession) -> dict:
        """
        Get completion summary data.

        Args:
            session: Completed session

        Returns:
            Dictionary with completion summary
        """
        summary = {
            "sequence_name": session.sequence_name,
            "user_id": session.user_id,
            "total_questions": len(session.answers),
            "start_time": session.created_at,
            "completion_time": session.completed_at,
            "duration": (session.completed_at - session.created_at)
            if session.completed_at
            else 0,
        }

        # Add scoring information if available
        if session.total_score is not None:
            summary.update(
                {
                    "total_score": session.total_score,
                    "max_possible_score": session.max_possible_score,
                    "percentage": (
                        (session.total_score / session.max_possible_score) * 100
                        if session.max_possible_score and session.max_possible_score > 0
                        else 0
                    ),
                }
            )

        return summary
