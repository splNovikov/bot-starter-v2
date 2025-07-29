"""
User interaction handlers for the Telegram bot.

Contains the essential /start handler for bot initialization and user greeting.
This module maintains clean architecture with proper separation of concerns.
"""

# Third-party imports
from aiogram import Router
from aiogram.types import Message

# Local application imports
from core.handlers.decorators import command
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger
from business.services.greeting import send_greeting

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
    """
    Handle /start command.
    
    Sends a personalized greeting message to the user when they start the bot.
    This is the primary entry point for user interaction.
    
    Args:
        message: The incoming message from the user
    """
    await send_greeting(message)


def initialize_registry():
    """
    Initialize the handlers registry with the user router.
    
    This function connects the registry system to the aiogram router and ensures
    all registered handlers are properly connected for message handling.
    
    Raises:
        RuntimeError: If registry initialization fails
    """
    try:
        from core.handlers.registry import get_registry
        
        # Get registry instance and assign router
        registry = get_registry()
        registry._router = user_router
        
        # Re-register all enabled handlers with the router
        enabled_handlers = [
            handler for handler in registry.get_all_handlers() 
            if handler.metadata.enabled
        ]
        
        for handler in enabled_handlers:
            registry._register_with_router(handler)
        
        logger.info(
            f"Registry initialized successfully with {len(enabled_handlers)} "
            f"enabled handlers out of {len(registry.get_all_handlers())} total"
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize registry: {e}")
        raise RuntimeError(f"Registry initialization failed: {e}") from e 