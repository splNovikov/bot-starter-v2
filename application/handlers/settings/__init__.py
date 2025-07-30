"""
Settings handlers package.

Contains configuration and preference handlers.
These handle user settings like language, profile, etc.
"""

from .locale_handler import locale_router

__all__ = [
    'locale_router'
] 