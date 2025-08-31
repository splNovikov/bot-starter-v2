from aiogram.types import CallbackQuery

from application.services.user_utils import create_enhanced_context
from core.di.container import get_container
from core.sequence import create_translator
from core.sequence.protocols import SequenceServiceProtocol
from core.utils import get_logger

from .gender_handler import handle_gender_save
from .preferred_name_handler import handle_confirm_user_name_save

logger = get_logger()

# Constants for callback data
CALLBACK_SEPARATOR = ":"
EXPECTED_PARTS_COUNT = 4
CALLBACK_PREFIX = "seq_answer"
SEQUENCE_NAME = "user_info"


async def user_info_callback_handler(callback: CallbackQuery) -> None:
    """
    Handle callback queries for user info sequence.

    Args:
        callback: Callback query object
    """
    try:
        # Parse callback data
        if not callback.data:
            logger.warning(f"Empty callback data from user {callback.from_user.id}")
            await callback.answer("Invalid callback data")
            return

        # Expected format: "seq_answer:sequence_name:question_key:answer_value"
        parts = callback.data.split(CALLBACK_SEPARATOR)
        if len(parts) != EXPECTED_PARTS_COUNT or parts[0] != CALLBACK_PREFIX:
            logger.warning(
                f"Invalid callback data format: {callback.data} from user {callback.from_user.id}"
            )
            await callback.answer("Invalid callback format")
            return

        _, sequence_name, question_key, answer_value = parts

        # Validate sequence name
        if sequence_name != SEQUENCE_NAME:
            logger.warning(
                f"Invalid sequence name: {sequence_name} from user {callback.from_user.id}"
            )
            await callback.answer("Invalid sequence")
            return

        # Validate question key and answer value
        if not question_key or not answer_value:
            logger.warning(
                f"Invalid question key or answer value from user {callback.from_user.id}"
            )
            await callback.answer("Invalid answer")
            return

        logger.debug(
            f"Processing callback data: {callback.data} for user {callback.from_user.id}"
        )

        # Get sequence service
        container = get_container()
        sequence_service = container.resolve(SequenceServiceProtocol)

        # Get current session
        session = sequence_service.get_session(callback.from_user.id)
        if not session:
            logger.error(f"No active session for user {callback.from_user.id}")
            await callback.answer("No active session")
            return

        # Validate that the question key is valid for this sequence
        sequence_definition = (
            sequence_service._sequence_provider.get_sequence_definition(
                session.sequence_name
            )
        )
        if not sequence_definition:
            logger.error(f"Sequence definition not found for {session.sequence_name}")
            await callback.answer("Sequence not found")
            return

        question = sequence_definition.get_question_by_key(question_key)
        if not question:
            logger.error(f"Question '{question_key}' not found in sequence")
            await callback.answer("Question not found")
            return

        # Log the current session state before processing
        logger.debug(
            f"Current session step: {session.current_step}, Current question: {question_key}"
        )

        # Process the button answer
        logger.debug(
            f"Processing button answer '{answer_value}' for question '{question_key}' for user {callback.from_user.id}"
        )

        success, error_message, next_question_key = sequence_service.process_answer(
            callback.from_user.id, answer_value, callback.from_user, question_key
        )

        if not success:
            logger.error(
                f"Failed to process answer for user {callback.from_user.id}: {error_message}"
            )
            await callback.answer("Answer processing failed")
            return

        # Handle confirm_user_name question logic - save "John_Doe" when user confirms their name
        if question_key == "confirm_user_name" and answer_value.lower() == "true":
            await handle_confirm_user_name_save(callback.from_user)
        # Handle gender question logic - save user's selected gender
        elif question_key == "gender":
            await handle_gender_save(callback.from_user, answer_value)
        else:
            logger.debug(
                f"Not a handled question. Question: {question_key}, Answer: {answer_value}"
            )

        # Answer the callback to remove loading state
        await callback.answer("✅ Answer recorded!")

        # Check if sequence is complete
        if sequence_service.is_sequence_complete(callback.from_user.id):
            logger.debug(f"Sequence completed for user {callback.from_user.id}")

            # Create translator and enhanced context with preferred_name
            translator = create_translator(callback.from_user)
            context = await create_enhanced_context(callback.from_user)

            # Send completion message
            try:
                await sequence_service.send_completion_message(
                    callback.message, session, translator, context
                )
            except Exception as e:
                logger.error(f"Failed to send completion message: {e}")
                await callback.message.answer("❌ Error sending completion message.")

        elif next_question_key:
            # Edit message with next question
            logger.debug(
                f"Editing message with next question '{next_question_key}' for user {callback.from_user.id}"
            )
            try:
                # Create translator and enhanced context with preferred_name
                translator = create_translator(callback.from_user)
                context = await create_enhanced_context(callback.from_user)

                await sequence_service.edit_question(
                    callback.message,
                    next_question_key,
                    translator,
                    context,
                    user_id=callback.from_user.id,
                )
            except Exception as e:
                logger.error(f"Failed to edit question: {e}")
                await callback.message.answer("❌ Error loading next question.")
        else:
            logger.error(f"No next question available for user {callback.from_user.id}")
            await callback.message.answer("❌ No next question available")

    except Exception as e:
        logger.error(f"Error in user info callback handler: {e}")
        await callback.answer("❌ An error occurred.")
