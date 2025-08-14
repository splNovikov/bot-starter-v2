"""
Application services module.

Contains business logic services specific to the application domain.
"""

from .user_service import UserService, get_user_service, set_user_service
from .user_utils import ensure_user_exists

__all__ = ["UserService", "get_user_service", "set_user_service", "ensure_user_exists"]
