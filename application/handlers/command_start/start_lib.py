from aiogram.types import User

from application.services import get_user_service
from application.types.user import UserData
from core.services.localization import t


def get_username(user_data: UserData = None) -> str:
    if user_data and user_data.preferred_name:
        return user_data.preferred_name

    # Fallback to direct access if user service is not available
    return "Anonymous"


def create_greeting_message(user_data: UserData = None) -> str:
    """Create a generic greeting message."""
    preferred_name = get_username(user_data)
    return t("handlers.start.greetings.hello", preferred_name=preferred_name)


def create_new_user_greeting(user: User) -> str:
    """Create a greeting message for new users."""
    return t("handlers.start.greetings.new_user", user=user)


def create_readiness_message(user: User) -> str:
    """Create a readiness message for new users."""
    return t("handlers.start.greetings.readiness", user=user)
