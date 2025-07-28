"""
Logging middleware for tracking requests and responses.
Provides structured logging for all bot interactions.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from utils.logger import get_logger

logger = get_logger()


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging all incoming updates and responses.
    
    Features:
    - Request/response logging
    - Error tracking
    - Performance monitoring
    - User activity tracking
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process incoming update with logging.
        
        Args:
            handler: Next handler in the chain
            event: Telegram event object
            data: Handler data
            
        Returns:
            Handler result
        """
        
        # Extract update information
        if isinstance(event, Update):
            update_type = self._get_update_type(event)
            user_info = self._get_user_info(event)
            
            logger.info(
                f"Processing {update_type} from user {user_info['username']} "
                f"(ID: {user_info['user_id']}, Chat: {user_info['chat_id']})"
            )
            
            try:
                # Call next handler
                result = await handler(event, data)
                
                logger.debug(f"Successfully processed {update_type} for user {user_info['user_id']}")
                return result
                
            except Exception as e:
                logger.error(
                    f"Error processing {update_type} for user {user_info['user_id']}: {e}",
                    exc_info=True
                )
                raise
        else:
            # For non-Update events, just pass through with basic logging
            logger.debug(f"Processing event: {type(event).__name__}")
            return await handler(event, data)
    
    def _get_update_type(self, update: Update) -> str:
        """Extract update type from Update object."""
        if update.message:
            return "message"
        elif update.callback_query:
            return "callback_query"
        elif update.inline_query:
            return "inline_query"
        elif update.edited_message:
            return "edited_message"
        else:
            return "unknown"
    
    def _get_user_info(self, update: Update) -> Dict[str, Any]:
        """Extract user information from Update object."""
        user = None
        chat_id = None
        
        if update.message:
            user = update.message.from_user
            chat_id = update.message.chat.id
        elif update.callback_query:
            user = update.callback_query.from_user
            chat_id = update.callback_query.message.chat.id if update.callback_query.message else None
        elif update.inline_query:
            user = update.inline_query.from_user
        elif update.edited_message:
            user = update.edited_message.from_user
            chat_id = update.edited_message.chat.id
        
        return {
            "user_id": user.id if user else None,
            "username": user.first_name or user.username if user else "Unknown",
            "chat_id": chat_id
        } 