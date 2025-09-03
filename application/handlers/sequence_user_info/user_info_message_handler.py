from aiogram.types import Message

from application.services.user_utils import create_enhanced_context
from application.services.validation_error_service import ValidationErrorService
from core.sequence import create_translator
from core.utils import get_logger
from core.utils.context_utils import get_sequence_service
from core.utils.date_validator import validate_birth_date

from .birth_date_handler import handle_birth_date_save
from .preferred_name_handler import handle_preferred_name_save

logger = get_logger()


async def user_info_message_handler(message: Message, **kwargs) -> None:
    """
    Handle text messages for user info sequence.

    Args:
        message: Message object
    """
    try:
        # Get sequence service from context (Clean Architecture)
        sequence_service = get_sequence_service(kwargs)

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

        # Create translator and enhanced context with preferred_name
        translator = create_translator(message.from_user)
        context = await create_enhanced_context(message.from_user, kwargs)

        # Custom validation with localization for birth_date
        if current_question_key == "birth_date":
            is_valid, error_type = validate_birth_date(message.text.strip())
            if not is_valid:
                localized_error = ValidationErrorService.localize_date_error(
                    error_type, translator, context
                )
                await message.answer(localized_error, parse_mode="HTML")
                return

        # Process the answer using existing infrastructure
        success, error_message, next_question_key = sequence_service.process_answer(
            message.from_user.id, message.text, message.from_user
        )

        if not success:
            # Handle infrastructure layer errors (basic validation failures)
            await message.answer(error_message, parse_mode="HTML")
            return

        # Handle preferred_name question logic - save user's input as preferred_name
        if current_question_key == "preferred_name":
            await handle_preferred_name_save(message.from_user, message.text)
        elif current_question_key == "birth_date":
            await handle_birth_date_save(message.from_user, message.text)
        else:
            logger.debug(
                f"Not preferred_name or birth_date question. Current question: {current_question_key}, User input: {message.text}"
            )

        # If sequence is complete, send completion message
        if sequence_service.is_sequence_complete(message.from_user.id):
            # Create translator and enhanced context with preferred_name
            translator = create_translator(message.from_user)
            context = await create_enhanced_context(message.from_user, kwargs)

            await sequence_service.send_completion_message(
                message, session, translator, context
            )
        elif next_question_key:
            # Send next question
            try:
                # Create translator and enhanced context with preferred_name
                translator = create_translator(message.from_user)
                context = await create_enhanced_context(message.from_user, kwargs)

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
