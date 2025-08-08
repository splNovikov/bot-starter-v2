import asyncio

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from application.services import get_user_service
from core.services import t
from core.utils import get_logger

from .start_lib import (
    create_greeting_message,
    create_new_user_greeting,
    create_readiness_message,
)

logger = get_logger()


async def handle_start(message: Message) -> None:
    try:
        user_service = get_user_service()
        if not user_service:
            logger.error("User service not available")

            greeting = create_new_user_greeting(message.from_user)
            await message.answer(greeting, parse_mode="HTML")
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
        greeting = create_new_user_greeting(message.from_user)
        await message.answer(greeting, parse_mode="HTML")

        await asyncio.sleep(0.3)

        # Send readiness message with keyboard
        readiness_message = create_readiness_message(message.from_user)
        # Create keyboard with "Да, готов!" button
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t(
                            "handlers.start.greetings.ready_button",
                            user=message.from_user,
                        ),
                        callback_data="start_ready:user_info",
                    )
                ]
            ]
        )
        await message.answer(
            readiness_message, parse_mode="HTML", reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        error_message = t("errors.generic", user=message.from_user)
        await message.answer(error_message)
