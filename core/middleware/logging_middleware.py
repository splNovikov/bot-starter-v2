"""
Logging middleware for the Telegram bot.
Provides comprehensive request/response logging for debugging and monitoring.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, InlineQuery, Message, TelegramObject

from core.utils.logger import get_logger

logger = get_logger()


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging all bot interactions.

    Provides structured logging for requests, responses, and errors
    to help with debugging and monitoring bot performance.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Process event with logging.

        Args:
            handler: Next handler in the chain
            event: Telegram event (Message, CallbackQuery, etc.)
            data: Additional handler data

        Returns:
            Handler result
        """
        try:
            # Get event type and user info
            event_type = self._get_event_type(event)
            user_info = self._get_user_info(event)

            logger.info(
                f"Processing {event_type} from user {user_info['username']} "
                f"(ID: {user_info['user_id']}, Chat: {user_info['chat_id']})"
            )

            # Call next handler
            result = await handler(event, data)

            logger.debug(
                f"Successfully processed {event_type} for user {user_info['user_id']}"
            )
            return result

        except Exception as e:
            event_type = self._get_event_type(event)
            user_info = self._get_user_info(event)

            logger.error(
                f"Error processing {event_type} for user {user_info['user_id']}: {e}",
                exc_info=True,
            )
            raise

    def _get_event_type(self, event: TelegramObject) -> str:
        """Get the type of the event."""
        if isinstance(event, Message):
            return "message"
        elif isinstance(event, CallbackQuery):
            return "callback_query"
        elif isinstance(event, InlineQuery):
            return "inline_query"
        else:
            return event.__class__.__name__.lower()

    def _get_user_info(self, event: TelegramObject) -> Dict[str, Any]:
        """Extract user information from the event."""
        user = None
        chat_id = None

        if isinstance(event, Message):
            user = event.from_user
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            chat_id = event.message.chat.id if event.message else None
        elif isinstance(event, InlineQuery):
            user = event.from_user
            chat_id = None  # Inline queries don't have chat context

        # Simple username extraction without dependencies
        username = "Unknown"
        if user:
            if user.first_name and user.last_name:
                username = f"{user.first_name} {user.last_name}"
            elif user.first_name:
                username = user.first_name
            elif user.username:
                username = f"@{user.username}"
            else:
                username = "Anonymous"

        return {
            "user_id": user.id if user else None,
            "username": username,
            "chat_id": chat_id,
        }
