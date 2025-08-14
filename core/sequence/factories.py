"""
Core sequence factories.

Provides factory functions for creating sequence-related components
while maintaining dependency inversion principles.
"""

from typing import Callable

from aiogram.types import User

from ..utils.logger import get_logger
from .protocols import TranslatorProtocol

logger = get_logger()


# Global factory registry
_translator_factory: Callable[[User], TranslatorProtocol] = None


def set_translator_factory(factory: Callable[[User], TranslatorProtocol]) -> None:
    """
    Set the global translator factory.

    Args:
        factory: Factory function that creates TranslatorProtocol instances
    """
    global _translator_factory
    _translator_factory = factory


def _get_translator_factory() -> Callable[[User], TranslatorProtocol]:
    """
    Get the global translator factory.

    Returns:
        Factory function for creating translators

    Raises:
        NotImplementedError: If no factory has been set
    """
    if _translator_factory is None:
        raise NotImplementedError(
            "Translator factory not set. Call set_translator_factory() first."
        )
    return _translator_factory


def create_translator(user: User) -> TranslatorProtocol:
    """
    Create a translator instance using the global factory.

    Args:
        user: User object for the translator

    Returns:
        TranslatorProtocol instance

    Raises:
        NotImplementedError: If no factory has been set
    """
    factory = _get_translator_factory()
    return factory(user)
