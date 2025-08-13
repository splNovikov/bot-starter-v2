from aiogram.types import Message

from application.services import get_user_service
from core.sequence import create_translator, get_sequence_service
from core.utils import get_logger

logger = get_logger()


async def user_info_message_handler(message: Message) -> None:
    """
    Handle text messages for user info sequence.

    Args:
        message: Message object
    """
    try:
        sequence_service = get_sequence_service()
        if not sequence_service:
            logger.error("Sequence service not available")
            return

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
            logger.info(
                f"User {message.from_user.id} entered preferred_name: {message.text}"
            )

            user_service = get_user_service()
            logger.debug(f"User service retrieved: {user_service is not None}")

            if user_service:
                try:
                    # Update user metadata with preferred_name
                    logger.debug(
                        f"Attempting to update user {message.from_user.id} with preferred_name: {message.text}"
                    )
                    updated_user = await user_service.update_user(
                        message.from_user, {"preferred_name": message.text}
                    )

                    if updated_user:
                        logger.info(
                            f"Successfully saved preferred_name '{message.text}' for user {message.from_user.id}"
                        )
                        logger.debug(f"Updated user data: {updated_user}")
                    else:
                        logger.error(
                            f"Failed to save preferred_name for user {message.from_user.id} - update_user returned None"
                        )
                except Exception as e:
                    logger.error(
                        f"Error saving preferred_name for user {message.from_user.id}: {e}"
                    )
                    logger.exception("Full exception details:")
            else:
                logger.error("User service not available for saving preferred_name")
        else:
            logger.debug(
                f"Not preferred_name question. Current question: {current_question_key}, User input: {message.text}"
            )

        # If sequence is complete, send completion message
        if sequence_service.is_sequence_complete(message.from_user.id):
            # Create translator and context using global factory
            translator = create_translator(message.from_user)
            context = {"user": message.from_user}

            await sequence_service.send_completion_message(
                message, session, translator, context
            )
        elif next_question_key:
            # Send next question
            try:
                # Create translator and context using global factory
                translator = create_translator(message.from_user)
                context = {"user": message.from_user}

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
