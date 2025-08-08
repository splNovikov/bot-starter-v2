from aiogram.types import CallbackQuery

from core.sequence import get_sequence_service
from core.services import t
from core.utils.logger import get_logger

logger = get_logger()

# Constants for callback data
CALLBACK_SEPARATOR = ":"
EXPECTED_PARTS_COUNT = 4
CALLBACK_PREFIX = "seq_answer"
SEQUENCE_NAME = "user_info"


async def handle_user_info_answer(callback: CallbackQuery) -> None:
    """
    Handle user info sequence answer callback.

    Args:
        callback: The callback query containing sequence answer information

    Expected callback data format: "seq_answer:user_info:question_key:answer_value"
    """
    try:
        # Validate callback data
        if not callback.data:
            logger.warning(f"Empty callback data from user {callback.from_user.id}")
            await callback.answer(t("errors.invalid_callback", user=callback.from_user))
            return

        # Parse and validate callback data
        parts = callback.data.split(CALLBACK_SEPARATOR)
        if len(parts) != EXPECTED_PARTS_COUNT:
            logger.warning(
                f"Invalid callback data format: {callback.data} from user {callback.from_user.id}"
            )
            await callback.answer(t("errors.invalid_callback", user=callback.from_user))
            return

        _, sequence_name, question_key, answer_value = parts

        # Validate sequence name
        if sequence_name != SEQUENCE_NAME:
            logger.warning(
                f"Invalid sequence name: {sequence_name} from user {callback.from_user.id}"
            )
            await callback.answer(t("errors.invalid_sequence", user=callback.from_user))
            return

        # Validate question key and answer value
        if not question_key or not answer_value:
            logger.warning(
                f"Invalid question key or answer value from user {callback.from_user.id}"
            )
            await callback.answer(t("errors.invalid_answer", user=callback.from_user))
            return

        # Get sequence service
        sequence_service = get_sequence_service()
        if not sequence_service:
            logger.error("Sequence service not available")
            await callback.answer(
                t("errors.service_unavailable", user=callback.from_user)
            )
            return

        # Process the answer
        success, error_message, next_question_key = sequence_service.process_answer(
            callback.from_user.id, answer_value, callback.from_user
        )

        if not success:
            logger.error(
                f"Failed to process answer for user {callback.from_user.id}: {error_message}"
            )
            await callback.answer(
                t("errors.answer_processing_failed", user=callback.from_user)
            )
            return

        # Answer the callback to remove loading state
        await callback.answer(t("sequence.answer_recorded", user=callback.from_user))

        # Check if sequence is complete
        if sequence_service.is_sequence_complete(callback.from_user.id):
            logger.info(f"Sequence completed for user {callback.from_user.id}")

            # Send completion message
            session = sequence_service.get_session(callback.from_user.id)
            if session:
                try:
                    await sequence_service.send_completion_message(
                        callback.message, session, callback.from_user
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to send completion message for user {callback.from_user.id}: {e}"
                    )
                    await callback.message.answer(
                        t("errors.completion_failed", user=callback.from_user)
                    )
            else:
                logger.error(
                    f"No session found for completed sequence for user {callback.from_user.id}"
                )
                await callback.message.answer(
                    t("errors.completion_failed", user=callback.from_user)
                )
        elif next_question_key:
            # Send next question
            try:
                await sequence_service.send_question(
                    callback.message, next_question_key, callback.from_user
                )
            except Exception as e:
                logger.error(
                    f"Failed to send next question for user {callback.from_user.id}: {e}"
                )
                await callback.message.answer(
                    t("errors.next_question_failed", user=callback.from_user)
                )
        else:
            logger.error(f"No next question available for user {callback.from_user.id}")
            await callback.message.answer(
                t("errors.next_question_failed", user=callback.from_user)
            )

    except Exception as e:
        logger.error(
            f"Unexpected error processing user info answer for user {callback.from_user.id}: {e}"
        )
        await callback.answer(t("errors.generic", user=callback.from_user))
