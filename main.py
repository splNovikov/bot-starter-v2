"""
Main bot entry point with enhanced error handling and configuration.

This module initializes the Telegram bot with aiogram 3.x, sets up routers,
middleware, and provides graceful shutdown handling. It includes comprehensive
logging and error recovery mechanisms for production deployment.
"""

# Standard library imports
import asyncio
import sys
from contextlib import asynccontextmanager

# Third-party imports
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Local application imports
from application.handlers import main_router, initialize_registry
from infrastructure import initialize_sequences
from config import config
from core.middleware.localization_middleware import LocalizationMiddleware
from core.middleware.logging_middleware import LoggingMiddleware
from core.utils.logger import setup_logger, get_logger

# Setup logging
setup_logger()
logger = get_logger()


@asynccontextmanager
async def lifespan_context():
    """
    Async context manager for bot lifespan management.
    
    Handles startup and cleanup operations gracefully.
    """
    logger.info("🚀 Bot is starting up...")
    
    try:
        # Initialize sequence system
        initialize_sequences()
        logger.info("✅ Sequence system initialized")
        
        # Initialize any other startup operations here
        logger.info("✅ Bot startup completed successfully")
        yield
        
    except Exception as e:
        logger.error(f"❌ Error during bot startup: {e}")
        raise
    
    finally:
        logger.info("🛑 Bot is shutting down...")
        # Cleanup operations here
        logger.info("✅ Bot shutdown completed")


async def create_bot() -> Bot:
    """
    Create and configure bot instance.
    
    Returns:
        Configured Bot instance
    """
    return Bot(
        token=config.token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN,
            link_preview_is_disabled=True
        )
    )


async def create_dispatcher() -> Dispatcher:
    """
    Create and configure dispatcher with routers and middleware.
    
    Returns:
        Configured Dispatcher instance
    """
    # Use in-memory storage for FSM (consider Redis for production)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register middleware in order
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(LocalizationMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LocalizationMiddleware())
    
    # Initialize registry to connect decorated handlers with aiogram router
    # This ensures @command decorators are properly registered for message handling
    initialize_registry()
    
    # Include main router (contains all registered handlers)
    dp.include_router(main_router)
    
    logger.info("✅ Dispatcher configured with main router and middleware")
    return dp


async def main():
    """
    Main bot execution function with comprehensive error handling.
    """
    try:
        async with lifespan_context():
            # Create bot and dispatcher
            bot = await create_bot()
            dp = await create_dispatcher()
            
            # Verify bot token and get bot info
            try:
                bot_info = await bot.get_me()
                logger.info(f"🤖 Bot @{bot_info.username} (ID: {bot_info.id}) started successfully")
                
                if config.api_base_url:
                    logger.info(f"🌐 API base URL configured: {config.api_base_url}")
                else:
                    logger.warning("⚠️ No API base URL configured")
                
            except Exception as e:
                logger.error(f"❌ Failed to get bot info: {e}")
                raise
            
            # Delete webhook if exists and start polling
            try:
                await bot.delete_webhook(drop_pending_updates=True)
                logger.info("🔄 Starting bot polling...")
                
                # Start polling with error handling
                await dp.start_polling(
                    bot,
                    allowed_updates=dp.resolve_used_update_types(),
                    skip_updates=True
                )
                
            except Exception as e:
                logger.error(f"❌ Error in polling: {e}")
                raise
                
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user (Ctrl+C)")
        
    except Exception as e:
        logger.error(f"💥 Critical error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        if sys.platform.startswith('win'):
            # Fix for Windows event loop policy
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Run the bot
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("👋 Application terminated by user")
        
    except Exception as e:
        logger.error(f"💥 Failed to start application: {e}")
        sys.exit(1) 
