"""
Core middleware package.

Provides reusable middleware components for the Telegram bot framework.
"""

from .logging_middleware import LoggingMiddleware

__all__ = ["LoggingMiddleware"]
