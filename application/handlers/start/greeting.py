"""
User greeting business logic.

Handles user greeting functionality including username extraction
and personalized greeting message creation with proper error handling
and localization support.
"""

# Third-party imports
from aiogram.types import Message, User

# Local application imports  
from core.services.localization import t
from core.utils.logger import get_logger

logger = get_logger()


def get_username(user: User) -> str:
    return user.first_name or user.username or "Anonymous"


def create_greeting_message(user: User) -> str:
    username = get_username(user)
    return t("greetings.hello", user=user, username=username)


async def send_greeting(message: Message) -> None:
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
