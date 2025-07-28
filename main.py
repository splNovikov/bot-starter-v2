#!/usr/bin/env python3
"""
Modern Telegram Bot using aiogram v3.x with Router system.

Features:
- Router-based architecture for scalability
- Comprehensive logging with loguru
- Environment configuration with python-dotenv
- Async/await patterns for performance
- Proper error handling and graceful shutdown
- Middleware support for cross-cutting concerns
- Well-typed handlers registry system
"""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from business.handlers import user_router
from core.middleware import LoggingMiddleware
from core.middleware.localization_middleware import LocalizationMiddleware
from core.utils import setup_logger, get_logger


class TelegramBot:
    """
    Main bot application class.
    
    Encapsulates bot initialization, configuration, and lifecycle management.
    """
    
    def __init__(self):
        """Initialize bot application."""
        self.logger = get_logger()
        self.bot: Bot | None = None
        self.dp: Dispatcher | None = None
        self._shutdown_event = asyncio.Event()
    
    async def _create_bot(self) -> Bot:
        """Create and configure bot instance."""
        return Bot(
            token=config.token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
                protect_content=False,
                allow_sending_without_reply=True
            )
        )
    
    async def _create_dispatcher(self) -> Dispatcher:
        """Create and configure dispatcher with routers and middleware."""
        # Create dispatcher with memory storage for FSM
        dp = Dispatcher(
            storage=MemoryStorage(),
            name="main_dispatcher"
        )
        
        # Register middleware
        dp.message.middleware(LoggingMiddleware())
        dp.callback_query.middleware(LoggingMiddleware())
        
        # Register localization middleware
        dp.message.middleware(LocalizationMiddleware())
        dp.callback_query.middleware(LocalizationMiddleware())
        
        # Include routers
        dp.include_router(user_router)
        
        return dp
    
    async def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            self._shutdown_event.set()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if sys.platform != "win32":
            signal.signal(signal.SIGHUP, signal_handler)
    
    @asynccontextmanager
    async def _bot_context(self) -> AsyncGenerator[tuple[Bot, Dispatcher], None]:
        """Context manager for bot lifecycle."""
        try:
            # Create bot and dispatcher
            self.bot = await self._create_bot()
            self.dp = await self._create_dispatcher()
            
            # Get bot info
            bot_info = await self.bot.get_me()
            self.logger.info(f"Bot initialized: @{bot_info.username} ({bot_info.first_name})")
            
            # Setup webhook deletion (ensures polling mode)
            await self.bot.delete_webhook(drop_pending_updates=True)
            
            yield self.bot, self.dp
            
        except Exception as e:
            self.logger.error(f"Error during bot initialization: {e}")
            raise
        finally:
            # Cleanup
            if self.bot:
                await self.bot.session.close()
                self.logger.info("Bot session closed")
    
    async def start(self) -> None:
        """Start the bot application."""
        self.logger.info("Starting Telegram bot application...")
        
        try:
            # Setup signal handlers
            await self._setup_signal_handlers()
            
            async with self._bot_context() as (bot, dp):
                # Start polling with error handling
                self.logger.info("Starting polling...")
                
                # Create polling task
                polling_task = asyncio.create_task(
                    dp.start_polling(
                        bot,
                        allowed_updates=dp.resolve_used_update_types(),
                        drop_pending_updates=True
                    )
                )
                
                # Wait for shutdown signal
                await self._shutdown_event.wait()
                
                # Cancel polling
                polling_task.cancel()
                try:
                    await polling_task
                except asyncio.CancelledError:
                    self.logger.info("Polling cancelled")
                
        except Exception as e:
            self.logger.error(f"Critical error in bot application: {e}")
            raise
        finally:
            self.logger.info("Bot application stopped")


async def main() -> None:
    """Main application entry point."""
    # Setup logging
    setup_logger()
    logger = get_logger()
    
    try:
        logger.info("Initializing Telegram bot...")
        
        # Create and start bot application
        app = TelegramBot()
        await app.start()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1) 