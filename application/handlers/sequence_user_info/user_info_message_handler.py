from aiogram.types import Message

from core.sequence import get_sequence_service
from core.sequence.types import SequenceStatus
from core.services import t
from core.utils.logger import get_logger

logger = get_logger()


async def user_info_message_handler(message: Message) -> None:
    """
    Handle text input for user info sequence.

    Args:
        message: The message containing text input
    """
    logger.debug(
        f"Text handler triggered for user {message.from_user.id} with text: '{message.text}'"
    )

    try:
        # Get sequence service
        sequence_service = get_sequence_service()
        if not sequence_service:
            logger.error("Sequence service not available")
            await message.answer(
                t("errors.service_unavailable", user=message.from_user)
            )
            return

        # Check if user has an active sequence session
        session = sequence_service.get_session(message.from_user.id)
        if not session or session.status != SequenceStatus.ACTIVE:
            # Not in an active sequence, ignore the message
            return

        # Process the text answer
        logger.debug(
            f"Processing text answer '{message.text}' for user {message.from_user.id}"
        )
        success, error_message, next_question_key = sequence_service.process_answer(
            message.from_user.id, message.text, message.from_user
        )
        logger.debug(
            f"Text answer processed: success={success}, next_question={next_question_key}"
        )

        if not success:
            logger.error(
                f"Failed to process text answer for user {message.from_user.id}: {error_message}"
            )
            await message.answer(
                t("errors.answer_processing_failed", user=message.from_user)
            )
            return

        # Check if sequence is complete
        if sequence_service.is_sequence_complete(message.from_user.id):
            logger.debug(f"Sequence completed for user {message.from_user.id}")

            # Send completion message
            try:
                await sequence_service.send_completion_message(
                    message, session, message.from_user
                )
            except Exception as e:
                logger.error(
                    f"Failed to send completion message for user {message.from_user.id}: {e}"
                )
                await message.answer(
                    t("errors.completion_failed", user=message.from_user)
                )
        elif next_question_key:
            # Send next question
            logger.debug(
                f"Sending next question '{next_question_key}' to user {message.from_user.id}"
            )
            try:
                await sequence_service.send_question(
                    message, next_question_key, message.from_user
                )
            except Exception as e:
                logger.error(
                    f"Failed to send next question for user {message.from_user.id}: {e}"
                )
                await message.answer(
                    t("errors.next_question_failed", user=message.from_user)
                )
        else:
            logger.error(f"No next question available for user {message.from_user.id}")
            await message.answer(
                t("errors.next_question_failed", user=message.from_user)
            )

    except Exception as e:
        logger.error(
            f"Unexpected error processing user info text for user {message.from_user.id}: {e}"
        )
        await message.answer(t("errors.generic", user=message.from_user))
