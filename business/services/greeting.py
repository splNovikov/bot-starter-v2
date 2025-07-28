"""
User greeting business logic.

Handles user greeting functionality including username extraction
and personalized greeting message creation.
"""

from aiogram.types import Message, User

from core.utils.logger import get_logger
from business.services.localization import t

logger = get_logger()


def get_username(user: User) -> str:
    """Extract display-friendly username from Telegram user."""
    return user.first_name or user.username or "Anonymous"


def create_greeting_message(user: User) -> str:
    """Create a personalized greeting message for the user."""
    username = get_username(user)
    return t("greetings.hello", user=user, username=username)


async def send_greeting(message: Message) -> None:
    """Send a personalized greeting to the user."""
    try:
        greeting = create_greeting_message(message.from_user)
        await message.answer(greeting)
        
        # System log in English only
        username = get_username(message.from_user)
        logger.info(f"Sent greeting to user: {username} (ID: {message.from_user.id}, Chat: {message.chat.id})")
        
    except Exception as e:
        logger.error(f"Error sending greeting: {e}")
        error_message = t("errors.generic", user=message.from_user)
        await message.answer(error_message) 