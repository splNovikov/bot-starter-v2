"""
User message handlers for the Telegram bot.

See business/docs/handlers.md for comprehensive documentation on adding new handlers.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from core.handlers.decorators import command, text_handler, message_handler
from core.handlers.types import HandlerCategory
from core.handlers.registry import get_registry
from core.utils.logger import get_logger

from business.services.greeting import send_greeting, get_username, create_greeting_message

user_router = Router(name="user_handlers")
logger = get_logger()


@command(
    "start", 
    description="Get a welcome greeting message",
    category=HandlerCategory.CORE,
    usage="/start",
    examples=["/start"],
    tags=["welcome", "introduction"]
)
async def cmd_start(message: Message) -> None:
    """Handle /start command - entry point for new users."""
    await send_greeting(message)


@command(
    "greet",
    description="Send a friendly greeting message", 
    category=HandlerCategory.USER,
    usage="/greet",
    examples=["/greet", "/hi", "/hello"],
    aliases=["hi", "hello"],
    tags=["greeting", "social"]
)
async def cmd_greet(message: Message) -> None:
    """Handle /greet command and its aliases."""
    await send_greeting(message)


@command(
    "help",
    description="Show available commands and usage information",
    category=HandlerCategory.CORE,
    usage="/help",
    examples=["/help"]
)
async def cmd_help(message: Message) -> None:
    """Handle /help command with auto-generated help from registry."""
    try:
        registry = get_registry()
        help_text = registry.generate_help_text()
        
        logger.info(f"Help command requested by user {message.from_user.id}")
        
        await message.answer(help_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in help command handler: {e}")
        await message.answer("Sorry, something went wrong. Please try again.")


@text_handler(
    "greeting_responder",
    description="Respond to any text message with a greeting",
    category=HandlerCategory.USER,
    hidden=True
)
async def handle_text_message(message: Message) -> None:
    """Handle any text message that isn't caught by command handlers."""
    await send_greeting(message)


@message_handler(
    "media_responder", 
    description="Handle non-text messages (photos, documents, etc.)",
    category=HandlerCategory.USER,
    hidden=True
)
async def handle_other_messages(message: Message) -> None:
    """Handle non-text messages like photos, documents, voice messages, etc."""
    try:
        username = get_username(message.from_user)
        
        logger.info(
            f"Non-text message received from {username} "
            f"(ID: {message.from_user.id}): {message.content_type}"
        )
        
        greeting_message = create_greeting_message(username)
        response = f"{greeting_message} I can only respond to text messages right now."
        
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"Error in media message handler: {e}")
        await message.answer("Sorry, something went wrong. Please try again.")


def initialize_registry():
    """Initialize the global registry with the router."""
    registry = get_registry()
    registry._router = user_router
    
    # Re-register all handlers with the router
    for handler in registry.get_all_handlers():
        if handler.metadata.enabled:
            registry._register_with_router(handler)
    
    logger.info(f"Registry initialized with {len(registry.get_all_handlers())} handlers and router integration") 