"""
User interaction handlers for the Telegram bot.

Contains handlers for basic user commands like start, help, greet, 
and general message processing.
"""

from aiogram import Router
from aiogram.types import Message, CallbackQuery

from core.handlers.decorators import command, text_handler, message_handler
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger
from business.services.greeting import send_greeting, get_username
from business.services.help_service import generate_localized_help
from core.services.localization import t
from business.handlers.language_handlers import cmd_language, cmd_languages, handle_language_selection

# Create router for user handlers
user_router = Router(name="user_handlers")

logger = get_logger()


@command(
    "start",
    description="Get a welcome greeting message",
    category=HandlerCategory.CORE,
    usage="/start",
    examples=["/start"]
)
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await send_greeting(message)


@command(
    "greet",
    description="Send a friendly greeting message",
    category=HandlerCategory.USER, 
    usage="/greet",
    examples=["/greet", "/hi", "/hello"],
    aliases=["hi", "hello"]
)
async def cmd_greet(message: Message) -> None:
    """Handle /greet command and aliases."""
    await send_greeting(message)


@command(
    "help",
    description="Show available commands and usage information",
    category=HandlerCategory.CORE,
    usage="/help",
    examples=["/help"]
)
async def cmd_help(message: Message) -> None:
    """Handle /help command with localized output."""
    try:
        help_text = generate_localized_help(message.from_user)
        await message.answer(help_text, parse_mode="HTML")
        
        # System log in English only
        logger.info(f"Help command requested by user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error generating help text: {e}")
        error_msg = t("errors.help_generation_failed", user=message.from_user)
        await message.answer(error_msg)


@text_handler(
    "greeting_responder",
    description="Responds to text messages with greeting",
    category=HandlerCategory.USER,
    hidden=True
)
async def handle_other_messages(message: Message) -> None:
    """Handle all other text messages with a greeting."""
    await send_greeting(message)


@message_handler(
    "media_responder", 
    description="Handle non-text messages",
    category=HandlerCategory.USER,
    hidden=True
)
async def handle_media_messages(message: Message) -> None:
    """Handle media and other non-text messages."""
    try:
        # System log in English only
        username = get_username(message.from_user)
        logger.info(f"Non-text message received from {username} (ID: {message.from_user.id}): {message.content_type}")
        
        # User response in their language
        greeting = t("greetings.hello", user=message.from_user, username=get_username(message.from_user))
        response = t("greetings.media_response", user=message.from_user, greeting=greeting)
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"Error handling media message: {e}")
        error_msg = t("errors.generic", user=message.from_user)
        await message.answer(error_msg)


def initialize_registry():
    """Initialize the handlers registry with all user handlers."""
    from core.handlers.registry import get_registry
    
    # Get registry instance
    registry = get_registry()
    registry._router = user_router
    
    # Re-register all handlers with the router (this handles automatic registration)
    for handler in registry.get_all_handlers():
        if handler.metadata.enabled:
            registry._register_with_router(handler)
    
    # Register callback query handler for language selection
    user_router.callback_query.register(handle_language_selection)
    
    logger.info(f"Registry initialized with {len(registry.get_all_handlers())} handlers and router integration") 