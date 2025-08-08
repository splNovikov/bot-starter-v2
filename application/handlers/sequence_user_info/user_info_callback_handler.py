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


async def user_info_callback_handler(callback: CallbackQuery) -> None:
    """
    Handle user info sequence answer callback.

    Args:
        callback: The callback query containing sequence answer information

    Expected callback data format: "seq_answer:user_info:question_key:answer_value"
    """
    logger.debug(
        f"Processing callback data: {callback.data} for user {callback.from_user.id}"
    )
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
        logger.debug(
            f"Processing button answer '{answer_value}' for question '{question_key}' for user {callback.from_user.id}"
        )

        # Get the current session to validate the question key
        session = sequence_service.get_session(callback.from_user.id)
        if not session:
            logger.error(f"No active session for user {callback.from_user.id}")
            await callback.answer(
                t("sequence.errors.no_active_session", user=callback.from_user)
            )
            return

        # Get the sequence definition to validate the question
        sequence_definition = (
            sequence_service._sequence_provider.get_sequence_definition(
                session.sequence_name
            )
        )
        if not sequence_definition:
            logger.error(f"Sequence definition not found for {session.sequence_name}")
            await callback.answer(
                t("sequence.errors.sequence_not_found", user=callback.from_user)
            )
            return

        # Validate that the question key is valid for this sequence
        question = sequence_definition.get_question_by_key(question_key)
        if not question:
            logger.error(f"Question '{question_key}' not found in sequence")
            await callback.answer(
                t("sequence.errors.question_not_found", user=callback.from_user)
            )
            return

        # Log the current session state before processing
        logger.debug(
            f"Current session step: {session.current_step}, Current question: {question_key}"
        )

        # Process the answer using the specific question key from the callback
        success, error_message, next_question_key = sequence_service.process_answer(
            callback.from_user.id, answer_value, callback.from_user, question_key
        )
        logger.debug(
            f"Button answer processed: success={success}, next_question={next_question_key}"
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
            logger.debug(f"Sequence completed for user {callback.from_user.id}")

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
            # Edit message with next question
            logger.debug(
                f"Editing message with next question '{next_question_key}' for user {callback.from_user.id}"
            )
            try:
                await sequence_service.edit_question(
                    callback.message, next_question_key, callback.from_user
                )
            except Exception as e:
                logger.error(
                    f"Failed to edit message with next question for user {callback.from_user.id}: {e}"
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
    # Callback handler completed
