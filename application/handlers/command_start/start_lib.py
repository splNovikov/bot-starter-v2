from aiogram.types import User

from application.types.user import UserData
from core.services.localization import t


def get_username(user: User, user_data: UserData = None) -> str:
    """Get user's display name from user_data if available, otherwise fallback to Telegram user fields."""
    if user_data and user_data.name:
        return user_data.name
    return user.first_name or user.username or "Anonymous"


def create_greeting_message(user: User, user_data: UserData = None) -> str:
    """Create a generic greeting message."""
    username = get_username(user, user_data)
    return t("handlers.start.greetings.hello", user=user, username=username)


def create_new_user_greeting(user: User) -> str:
    """Create a greeting message for new users."""
    return t("handlers.start.greetings.new_user", user=user)


def create_readiness_message(user: User) -> str:
    """Create a readiness message for new users."""
    return t("handlers.start.greetings.readiness", user=user)
