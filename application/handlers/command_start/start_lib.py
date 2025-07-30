from aiogram.types import User

from core.services.localization import t

def get_username(user: User) -> str:
    return user.first_name or user.username or "Anonymous"


def create_greeting_message(user: User) -> str:
    username = get_username(user)
    return t("greetings.hello", user=user, username=username)
