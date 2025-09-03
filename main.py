"""
Main bot entry point with Clean Architecture and enhanced error handling.

This module initializes the Telegram bot with aiogram 3.x following Clean Architecture
principles using the Application Facade pattern. It provides clean separation between
core infrastructure and application logic, making the application easily maintainable
and testable.

Architecture:
- Core layer: Defines protocols and abstractions
- Application layer: Business logic through ApplicationFacade
- Infrastructure layer: External concerns (HTTP, sequence management)
- Main: Orchestrates through facades, avoiding tight coupling

Key benefits:
- Application module can be completely replaced without changing main.py
- Clean dependency flow: Main -> Application Facade -> Core protocols
- All business logic isolated in application layer
"""

# Standard library imports
import asyncio
from contextlib import asynccontextmanager
import sys

# Third-party imports
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Clean Architecture imports - only core and application facade
from application import create_application_facade
from config import config
from core.facade import ApplicationFacadeProtocol
from core.middleware import (
    ApplicationFacadeMiddleware,
    CallbackMiddleware,
    LocalizationMiddleware,
    LoggingMiddleware,
)
from core.protocols.services import HttpClientProtocol, UserServiceProtocol
from core.sequence.protocols import SequenceServiceProtocol
from core.utils.logger import get_logger, setup_logger

# Setup logging
setup_logger()
logger = get_logger()


@asynccontextmanager
async def lifespan_context():
    """
    Async context manager for bot lifespan management.

    Handles startup and cleanup operations gracefully using application facade
    following Clean Architecture principles.
    """
    logger.info("🚀 Bot is starting up...")

    app_facade: ApplicationFacadeProtocol = None

    try:
        # Create application facade (Clean Architecture entry point)
        app_facade = create_application_facade()
        logger.info("✅ Application facade created")

        # Setup DI container through facade
        container = app_facade.get_di_container()
        logger.info("✅ DI container configured via facade")

        # Verify core services can be resolved
        container.resolve(UserServiceProtocol)
        container.resolve(SequenceServiceProtocol)
        container.resolve(HttpClientProtocol)
        logger.info("✅ Core services resolved from DI container")

        # Initialize infrastructure through facade
        app_facade.initialize_infrastructure()
        logger.info("✅ Infrastructure initialized via facade")

        # Initialize handlers through facade
        app_facade.initialize_handlers()
        logger.info("✅ Application handlers initialized via facade")

        logger.info("✅ Bot startup completed successfully")
        yield app_facade

    except Exception as e:
        logger.error(f"❌ Error during bot startup: {e}")
        raise

    finally:
        logger.info("🛑 Bot is shutting down...")

        # Dispose application facade (handles all cleanup)
        if app_facade:
            try:
                await app_facade.dispose()
                logger.info("✅ Application facade disposed")
            except Exception as e:
                logger.error(f"❌ Error disposing application facade: {e}")

        # Cleanup through facade
        try:
            if app_facade:
                await app_facade.cleanup_infrastructure()
                logger.info("✅ Infrastructure cleaned up successfully")
        except Exception as e:
            logger.error(f"❌ Error cleaning up infrastructure: {e}")

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
            parse_mode=ParseMode.MARKDOWN, link_preview_is_disabled=True
        ),
    )


async def create_dispatcher(app_facade: ApplicationFacadeProtocol) -> Dispatcher:
    """
    Create and configure dispatcher with routers and middleware.

    Args:
        app_facade: Application facade for accessing routers

    Returns:
        Configured Dispatcher instance
    """
    # Use in-memory storage for FSM (consider Redis for production)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register middleware in order - ApplicationFacadeMiddleware first
    facade_middleware = ApplicationFacadeMiddleware(app_facade)
    callback_middleware = CallbackMiddleware(app_facade)

    dp.message.middleware(facade_middleware)
    dp.callback_query.middleware(facade_middleware)
    dp.callback_query.middleware(callback_middleware)

    # Other middleware after facade
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(LocalizationMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LocalizationMiddleware())

    # Get main router through facade (Clean Architecture)
    main_router = app_facade.get_main_router()
    dp.include_router(main_router)

    logger.info("✅ Dispatcher configured with main router and middleware via facade")
    return dp


async def main():
    """
    Main bot execution function with comprehensive error handling.
    Uses Clean Architecture with application facade pattern.
    """
    try:
        async with lifespan_context() as app_facade:
            # Create bot and dispatcher (Clean Architecture)
            bot = await create_bot()
            dp = await create_dispatcher(app_facade)

            # Verify bot token and get bot info
            try:
                bot_info = await bot.get_me()
                logger.info(
                    f"🤖 Bot @{bot_info.username} (ID: {bot_info.id}) started successfully"
                )

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
                    skip_updates=True,
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
        if sys.platform.startswith("win"):
            # Fix for Windows event loop policy
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Run the bot
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("👋 Application terminated by user")

    except Exception as e:
        logger.error(f"💥 Failed to start application: {e}")
        sys.exit(1)
