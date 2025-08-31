from aiogram.types import Message

from application.services.user_utils import create_enhanced_context
from core.di.container import get_container
from core.sequence import create_translator
from core.sequence.protocols import SequenceServiceProtocol
from core.utils import get_logger

from .preferred_name_handler import handle_preferred_name_save

logger = get_logger()


async def user_info_message_handler(message: Message) -> None:
    """
    Handle text messages for user info sequence.

    Args:
        message: Message object
    """
    try:
        container = get_container()
        sequence_service = container.resolve(SequenceServiceProtocol)

        # Get current session
        session = sequence_service.get_session(message.from_user.id)
        if not session:
            logger.warning(f"No active session for user {message.from_user.id}")
            return

        # Get current question key BEFORE processing the answer
        current_question_key = sequence_service.get_current_question_key(
            message.from_user.id
        )
        logger.debug(f"Current question key before processing: {current_question_key}")

        # Process the answer
        success, error_message, next_question_key = sequence_service.process_answer(
            message.from_user.id, message.text, message.from_user
        )

        if not success:
            await message.answer(error_message, parse_mode="HTML")
            return

        # Handle preferred_name question logic - save user's input as preferred_name
        if current_question_key == "preferred_name":
            await handle_preferred_name_save(message.from_user, message.text)
        else:
            logger.debug(
                f"Not preferred_name question. Current question: {current_question_key}, User input: {message.text}"
            )

        # If sequence is complete, send completion message
        if sequence_service.is_sequence_complete(message.from_user.id):
            # Create translator and enhanced context with preferred_name
            translator = create_translator(message.from_user)
            context = await create_enhanced_context(message.from_user)

            await sequence_service.send_completion_message(
                message, session, translator, context
            )
        elif next_question_key:
            # Send next question
            try:
                # Create translator and enhanced context with preferred_name
                translator = create_translator(message.from_user)
                context = await create_enhanced_context(message.from_user)

                await sequence_service.send_question(
                    message,
                    next_question_key,
                    translator,
                    context,
                    user_id=message.from_user.id,
                )
            except Exception as e:
                logger.error(f"Failed to send next question: {e}")
                await message.answer(
                    "❌ Error sending next question. Please try again."
                )

    except Exception as e:
        logger.error(f"Error in user info message handler: {e}")
        await message.answer("❌ An error occurred. Please try again.")
