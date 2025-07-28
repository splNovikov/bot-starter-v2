"""
User message handlers for the Telegram bot.
Handles user interactions and commands using aiogram Router system.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.logger import get_logger

# Create router instance
user_router = Router(name="user_handlers")
logger = get_logger()


@user_router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    Handle /start command.
    
    Args:
        message: Incoming message object
    """
    try:
        username = message.from_user.first_name or message.from_user.username or "Anonymous"
        
        logger.info(
            f"Start command received from user: {username} "
            f"(ID: {message.from_user.id}, Chat: {message.chat.id})"
        )
        
        await message.answer(f"Hello, {username}!")
        
    except Exception as e:
        logger.error(f"Error in start command handler: {e}")
        await message.answer("Sorry, something went wrong. Please try again.")


@user_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Handle /help command.
    
    Args:
        message: Incoming message object
    """
    try:
        help_text = (
            "🤖 <b>Available Commands:</b>\n\n"
            "/start - Get a greeting message\n"
            "/help - Show this help message\n\n"
            "Just send any message and I'll greet you!"
        )
        
        logger.info(f"Help command requested by user {message.from_user.id}")
        
        await message.answer(help_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in help command handler: {e}")
        await message.answer("Sorry, something went wrong. Please try again.")


@user_router.message(F.text)
async def handle_text_message(message: Message) -> None:
    """
    Handle any text message.
    
    Args:
        message: Incoming message object
    """
    try:
        username = message.from_user.first_name or message.from_user.username or "Anonymous"
        
        logger.info(
            f"Text message received from {username} "
            f"(ID: {message.from_user.id}): {message.text[:50]}..."
        )
        
        await message.answer(f"Hello, {username}!")
        
    except Exception as e:
        logger.error(f"Error in text message handler: {e}")
        await message.answer("Sorry, something went wrong. Please try again.")


@user_router.message()
async def handle_other_messages(message: Message) -> None:
    """
    Handle other types of messages (photos, documents, etc.)
    
    Args:
        message: Incoming message object
    """
    try:
        username = message.from_user.first_name or message.from_user.username or "Anonymous"
        
        logger.info(
            f"Non-text message received from {username} "
            f"(ID: {message.from_user.id}): {message.content_type}"
        )
        
        await message.answer(f"Hello, {username}! I can only respond to text messages right now.")
        
    except Exception as e:
        logger.error(f"Error in other messages handler: {e}")
        await message.answer("Sorry, something went wrong. Please try again.") 