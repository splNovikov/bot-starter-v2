"""
Start command handler.

Handles the /start command which is the primary entry point for user interaction.
This is a fundamental command that every user needs.
"""

# Third-party imports
from aiogram import Router
from aiogram.types import Message

# Local application imports
from core.handlers.decorators import command
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger
from business.services.greeting import send_greeting

# Create router for start handler
start_router = Router(name="start_handler")

logger = get_logger()


@command(
    "start",
    description="Get a welcome greeting message",
    category=HandlerCategory.CORE,
    usage="/start",
    examples=["/start"]
)
async def cmd_start(message: Message) -> None:
    """
    Handle /start command.
    
    Sends a personalized greeting message to the user when they start the bot.
    This is the primary entry point for user interaction.
    
    Args:
        message: The incoming message from the user
    """
    await send_greeting(message) 