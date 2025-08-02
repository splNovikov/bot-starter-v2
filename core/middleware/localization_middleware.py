"""
Localization middleware for automatic language detection and user preference management.

This middleware automatically detects user language from Telegram locale and
integrates with the LocalizationService for seamless localization support.

See core/docs/middleware.md for comprehensive documentation on middleware development.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User

from core.services.localization import get_localization_service
from core.utils.logger import get_logger

logger = get_logger()


class LocalizationMiddleware(BaseMiddleware):
    """
    Middleware for automatic language detection and user preference management.

    Features:
    - Automatic language detection from Telegram user locale
    - User language preference caching
    - Context injection for easy access to localization service
    - Logging of language detection events
    """

    def __init__(self):
        """Initialize localization middleware."""
        self.localization_service = get_localization_service()
        logger.info("Localization middleware initialized")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Process incoming update and inject localization context.

        Args:
            handler: Next handler in the chain
            event: Telegram update event (Message, CallbackQuery, etc.)
            data: Context data dictionary

        Returns:
            Result from the next handler
        """
        user = self._extract_user(event)

        if user:
            # Detect and cache user language
            user_language = self.localization_service.get_user_language(user)

            # Inject localization context into handler data
            data["user_language"] = user_language
            data["localization_service"] = self.localization_service
            data["t"] = lambda key, **params: self.localization_service.t(
                key, user=user, **params
            )

            # Log language detection (debug level to avoid spam)
            logger.debug(
                f"Language detected for user {user.id} "
                f"({user.first_name or user.username or 'Unknown'}): {user_language}"
            )
        else:
            # No user context available, provide fallback localization
            data["user_language"] = self.localization_service.fallback_language
            data["localization_service"] = self.localization_service
            data["t"] = lambda key, **params: self.localization_service.t(key, **params)

            logger.debug("No user context available, using default language")

        # Continue to next handler
        return await handler(event, data)

    def _extract_user(self, event: TelegramObject) -> User | None:
        """
        Extract user object from various event types.

        Args:
            event: Telegram event object

        Returns:
            User object if available, None otherwise
        """
        if isinstance(event, Message):
            return event.from_user
        elif isinstance(event, CallbackQuery):
            return event.from_user
        elif hasattr(event, "from_user"):
            return event.from_user
        else:
            logger.debug(f"Cannot extract user from event type: {type(event)}")
            return None


class UserLanguageManager:
    """
    Helper class for managing user language preferences.

    This can be extended to persist language preferences to a database
    or external storage system.
    """

    def __init__(self):
        """Initialize user language manager."""
        self.localization_service = get_localization_service()
        logger.info("User language manager initialized")

    async def set_user_language(self, user_id: int, language_code: str) -> bool:
        """
        Set language preference for a user.

        Args:
            user_id: Telegram user ID
            language_code: Preferred language code

        Returns:
            True if language was set successfully, False otherwise
        """
        success = self.localization_service.set_user_language(user_id, language_code)

        if success:
            logger.info(f"User {user_id} language preference set to: {language_code}")
        else:
            logger.warning(f"Failed to set language {language_code} for user {user_id}")

        return success

    def get_user_language(self, user: User) -> str:
        """
        Get current language for a user.

        Args:
            user: Telegram user object

        Returns:
            Current language code for the user
        """
        return self.localization_service.get_user_language(user)

    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages.

        Returns:
            Dictionary mapping language codes to language names
        """
        return self.localization_service.get_supported_languages()


# Global user language manager instance
_user_language_manager: UserLanguageManager | None = None


def get_user_language_manager() -> UserLanguageManager:
    """Get the global user language manager instance."""
    global _user_language_manager
    if _user_language_manager is None:
        _user_language_manager = UserLanguageManager()
    return _user_language_manager
