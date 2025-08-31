"""
Dependency Injection container and related utilities.

Provides a simple, type-safe DI container for managing service dependencies
and promoting better testability and maintainability.
"""

from .container import DIContainer, get_container, set_container
from .protocols import Disposable, Injectable

__all__ = [
    "DIContainer",
    "get_container",
    "set_container",
    "Injectable",
    "Disposable",
]
