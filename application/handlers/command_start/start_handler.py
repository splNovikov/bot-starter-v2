from aiogram.types import Message

from application.services import get_user_service
from core.sequence import get_sequence_initiation_service
from core.services import t
from core.utils import get_logger

from .start_lib import create_greeting_message

logger = get_logger()


async def handle_start(message: Message) -> None:
    try:
        user_service = get_user_service()
        if not user_service:
            logger.error("User service not available")

            greeting = create_greeting_message(message.from_user)
            await message.answer(greeting)
            return

        # Try to fetch user from API
        user_data = await user_service.get_user(message.from_user)

        if not user_data:
            # User not found - try to create user in database
            logger.info(f"User {message.from_user.id} not found - attempting to create")

            await user_service.create_user(message.from_user)

        if user_data and user_data.user_info_sequence_passed:
            # User exists - show personalized greeting
            logger.info(f"Existing user {message.from_user.id} found in API")

            greeting = create_greeting_message(message.from_user, user_data)
            await message.answer(greeting)
            return

        # Run sequence for new users and users who haven't passed user_info sequence
        greeting = create_greeting_message(message.from_user)
        await message.answer(greeting)

        # Use sequence initiation service
        sequence_initiation_service = get_sequence_initiation_service()

        (
            success,
            error_message,
        ) = await sequence_initiation_service.initiate_user_info_sequence(
            message, message.from_user
        )

        if not success:
            logger.error(f"Failed to start user_info sequence: {error_message}")

    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        error_message = t("errors.generic", user=message.from_user)
        await message.answer(error_message)
