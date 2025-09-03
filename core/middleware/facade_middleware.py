"""
Application facade middleware for dependency injection.

Provides ApplicationFacade in handler context, enabling handlers to access
services through proper DI instead of using deprecated global functions.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.facade.application_facade import ApplicationFacadeProtocol
from core.utils.logger import get_logger

logger = get_logger()


class ApplicationFacadeMiddleware(BaseMiddleware):
    """
    Middleware that injects ApplicationFacade into handler context.

    This middleware provides clean access to application services through
    the facade pattern, replacing deprecated global functions.
    """

    def __init__(self, app_facade: ApplicationFacadeProtocol):
        """
        Initialize facade middleware.

        Args:
            app_facade: Application facade instance to inject
        """
        self.app_facade = app_facade
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Process event with application facade injection.

        Args:
            handler: Next handler in the chain
            event: Telegram event (Message, CallbackQuery, etc.)
            data: Additional handler data

        Returns:
            Handler result
        """
        # Inject application facade into data context
        data["app_facade"] = self.app_facade

        logger.debug("ApplicationFacade injected into handler context")

        # Call next handler
        return await handler(event, data)
