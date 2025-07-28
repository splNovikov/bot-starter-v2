"""
Greeting business service for the Telegram bot.

See business/docs/services.md for comprehensive documentation on creating business services.
"""

from aiogram.types import Message, User
from core.utils.logger import get_logger

logger = get_logger()


def get_username(user: User) -> str:
    """Extract a display-friendly username from a Telegram user."""
    return user.first_name or user.username or "Anonymous"


def create_greeting_message(username: str) -> str:
    """Generate a greeting message for a user."""
    return f"Hello, {username}!"


async def send_greeting(message: Message) -> None:
    """Complete greeting workflow - extract user info, create message, and send response."""
    try:
        username = get_username(message.from_user)
        greeting_message = create_greeting_message(username)
        
        logger.info(
            f"Sending greeting to user: {username} "
            f"(ID: {message.from_user.id}, Chat: {message.chat.id})"
        )
        
        await message.answer(greeting_message)
        
    except Exception as e:
        logger.error(f"Error sending greeting: {e}")
        await message.answer("Sorry, something went wrong. Please try again.")
        raise 