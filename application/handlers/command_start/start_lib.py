from aiogram.types import User

from application.types.user import UserData
from core.services.localization import t


def get_username(user: User, user_data: UserData = None) -> str:
    """Get user's display name from user_data if available, otherwise fallback to Telegram user fields."""
    if user_data and user_data.display_name:
        return user_data.display_name
    return user.first_name or user.username or "Anonymous"


def create_greeting_message(user: User, user_data: UserData = None) -> str:
    """Create a generic greeting message."""
    username = get_username(user, user_data)
    return t("greetings.hello", user=user, username=username)
