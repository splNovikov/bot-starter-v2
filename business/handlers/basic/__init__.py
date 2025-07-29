"""
Basic handlers package.

Contains fundamental command handlers that every user needs.
These are essential commands like /start and /help.
"""

from .start_handler import start_router

__all__ = [
    'start_router'
] 