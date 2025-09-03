import asyncio

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from application.services.user_utils import ensure_user_exists
from core.services import t
from core.utils import get_logger

from .start_lib import (
    create_greeting_message,
    create_new_user_greeting,
    create_readiness_message,
)

logger = get_logger()


async def start_command_handler(message: Message, **kwargs) -> None:
    try:
        # Ensure user exists in the system, creating if necessary
        user_data = await ensure_user_exists(message.from_user, kwargs)

        if not user_data:
            # User service unavailable or creation failed - show generic greeting
            logger.error(f"Failed to ensure user {message.from_user.id} exists")
            greeting = create_new_user_greeting(message.from_user)
            await message.answer(greeting, parse_mode="HTML")
            return

        if user_data and user_data.user_info_sequence_passed:
            # User exists - show personalized greeting
            logger.info(f"Existing user {message.from_user.id} found in API")

            greeting = create_greeting_message(user_data)
            await message.answer(greeting)
            return

        # Run sequence for new users and users who haven't passed user_info sequence
        greeting = create_new_user_greeting(message.from_user)
        await message.answer(greeting, parse_mode="HTML")

        await asyncio.sleep(0.3)

        # Send readiness message with keyboard
        readiness_message = create_readiness_message(message.from_user)
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
