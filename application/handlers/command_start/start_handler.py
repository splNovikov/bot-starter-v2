from aiogram.types import Message

from application.services import get_user_service
from core.sequence import get_sequence_initiation_service
from core.services import t
from core.utils import get_logger

from .start_lib import (
    create_greeting_message,
    get_username,
)

logger = get_logger()


async def handle_start(message: Message) -> None:
    """
    Handle /start command with conditional logic based on user existence.

    - If user exists in API: Show personalized greeting
    - If user not found (404): Start user_info sequence
    - If API error/timeout: Show generic greeting
    """
    try:
        user_service = get_user_service()
        if not user_service:
            logger.error("User service not available")
            greeting = create_greeting_message(message.from_user)
            await message.answer(greeting)
            return

        # Try to fetch user from API
        user_data = await user_service.get_user(message.from_user)

        if user_data:
            # User exists - show personalized greeting
            logger.info(f"Existing user {message.from_user.id} found in API")
            greeting = create_greeting_message(message.from_user, user_data)
            await message.answer(greeting)

        else:
            # User not found - start user_info sequence
            logger.info(
                f"New user {message.from_user.id} - starting user_info sequence"
            )

            # Send welcome message for new users
            greeting = create_greeting_message(message.from_user)
            await message.answer(greeting)

            # Use sequence initiation service
            sequence_initiation_service = get_sequence_initiation_service()
            
            success, error_message = await sequence_initiation_service.initiate_user_info_sequence(
                message, message.from_user
            )
            
            if not success:
                logger.error(f"Failed to start user_info sequence: {error_message}")
                # Error message already sent by the service

        username = get_username(message.from_user)
        logger.info(
            f"Processed /start for user: {username} "
            f"(ID: {message.from_user.id}, Chat: {message.chat.id})"
        )

    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        error_message = t("errors.generic", user=message.from_user)
        await message.answer(error_message)
