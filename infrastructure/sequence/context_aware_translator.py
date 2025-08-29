"""
Context-aware translator implementation.

Provides universal implementation of TranslatorProtocol that can work with any context data.
"""

from typing import Any, Mapping, Optional

from aiogram.types import User

from core.sequence.protocols import TranslatorProtocol
from core.services import t
from core.utils.logger import get_logger

logger = get_logger()


class ContextAwareTranslator(TranslatorProtocol):
    """
    Context-aware translator implementation.

    Uses pre-populated context data to provide localized text
    with proper parameter substitution. Context should contain
    all necessary parameters like preferred_name, presumably_user_name etc.
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

        # Extract parameters from context
        if context:
            # Add all context parameters directly
            # Note: enhanced context already contains preferred_name and presumably_user_name
            for k, v in context.items():
                if k != "user":  # Skip user object itself
                    params[k] = v

        # Add additional keyword arguments
        params.update(kwargs)

        try:
            result = t(key, user=self._user, **params)
            return result
        except Exception as e:
            logger.error(f"Translation failed for key '{key}': {e}")
            raise
