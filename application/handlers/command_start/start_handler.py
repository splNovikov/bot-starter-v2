from aiogram.types import Message

from core.services.localization import t
from core.utils.logger import get_logger

from .start_lib import create_greeting_message, get_username

logger = get_logger()


async def handle_start(message: Message) -> None:
    try:
        greeting = create_greeting_message(message.from_user)
        await message.answer(greeting)

        username = get_username(message.from_user)
        logger.info(
            f"Sent greeting to user: {username} "
            f"(ID: {message.from_user.id}, Chat: {message.chat.id})"
        )

    except Exception as e:
        logger.error(f"Error sending greeting: {e}")
        error_message = t("errors.generic", user=message.from_user)
        await message.answer(error_message)
