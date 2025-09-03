from aiogram.types import Message

from application.services.user_utils import create_enhanced_context, ensure_user_exists
from core.sequence import create_translator
from core.services import t
from core.utils.context_utils import get_sequence_service
from core.utils.logger import get_logger
from infrastructure.sequence import SequenceInitiationService

logger = get_logger()


async def user_info_command_handler(message: Message, **kwargs):
    try:
        # Ensure user exists in the system, creating if necessary
        context = {"user": message.from_user, "user_id": message.from_user.id}
        user_data = await ensure_user_exists(message.from_user, context)

        if not user_data:
            # User service unavailable or creation failed
            logger.error(f"Failed to ensure user {message.from_user.id} exists")
            error_message = t("errors.generic", user=message.from_user)
            await message.answer(error_message)
            return

        # Get sequence service from context (Clean Architecture)
        sequence_service = get_sequence_service(kwargs)
        sequence_initiation_service = SequenceInitiationService(sequence_service)

        # Create translator and enhanced context with preferred_name
        translator = create_translator(message.from_user)
        context = await create_enhanced_context(message.from_user, kwargs)

        (
            success,
            error_message,
        ) = await sequence_initiation_service.initiate_user_info_sequence(
            message, translator, context
        )

        if not success:
            await message.answer(error_message, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in user_info_command_handler: {e}")
        error_message = t("errors.generic", user=message.from_user)
        await message.answer(error_message)
