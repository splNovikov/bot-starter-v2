"""
Callback middleware for ensuring ApplicationFacade is available in callback handlers.

This middleware specifically handles callback query handlers that may not receive
context through the standard aiogram middleware chain.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from core.facade.application_facade import ApplicationFacadeProtocol
from core.utils.logger import get_logger

logger = get_logger()


class CallbackMiddleware(BaseMiddleware):
    """
    Middleware that ensures ApplicationFacade is available in callback handlers.

    This middleware is specifically designed for callback query handlers that
    may not receive context through the standard aiogram middleware chain.
    """

    def __init__(self, app_facade: ApplicationFacadeProtocol):
        """
        Initialize callback middleware.

        Args:
            app_facade: Application facade instance to inject
        """
        self.app_facade = app_facade
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        """
        Process callback query with application facade injection.

        Args:
            handler: Next handler in the chain
            event: CallbackQuery event
            data: Additional handler data

        Returns:
            Handler result
        """
        # Ensure app_facade is in data context
        if "app_facade" not in data:
            data["app_facade"] = self.app_facade
            logger.debug("ApplicationFacade injected into callback context")

        # Call next handler
        return await handler(event, data)
