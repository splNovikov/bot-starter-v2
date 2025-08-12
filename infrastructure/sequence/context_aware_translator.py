"""
Context-aware translator implementation.

Provides universal implementation of TranslatorProtocol that can work with any context data.
"""

from typing import Any, Mapping, Optional

from aiogram.types import User

from application.services import get_user_service
from core.sequence.protocols import TranslatorProtocol
from core.services import t
from core.utils.logger import get_logger

logger = get_logger()


class ContextAwareTranslator(TranslatorProtocol):
    """
    Context-aware translator implementation.

    Extracts parameters from any context data and provides
    localized text with proper parameter substitution.
    """

    def __init__(self, user: User):
        """
        Initialize translator with Telegram user.

        Args:
            user: Telegram User object
        """
        self._user = user

    def translate(
        self, key: str, context: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> str:
        """
        Translate a key with context and parameters.

        Args:
            key: Translation key
            context: Optional context mapping with any data
            **kwargs: Additional parameters

        Returns:
            Translated string

        Raises:
            Exception: If translation fails
        """
        params = {}

        # Extract user information from context
        if context:
            if "user" in context:
                user = context["user"]
                user_service = get_user_service()
                if user_service:
                    params["presumably_user_name"] = user_service.get_user_display_name(
                        user
                    )
                else:
                    params["presumably_user_name"] = "Anonymous"

            # Add other context parameters
            for k, v in context.items():
                if k != "user":
                    params[k] = v

        # Add additional keyword arguments
        params.update(kwargs)

        try:
            result = t(key, user=self._user, **params)
            return result
        except Exception as e:
            logger.error(f"Translation failed for key '{key}': {e}")
            raise
