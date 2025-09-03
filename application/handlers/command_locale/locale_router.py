from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger

from .locale_callback_handler import locale_callback_handler
from .locale_command_handler import locale_command_handler

logger = get_logger()

locale_router = Router(name="locale_router")


@command(
    "locale",
    description="Change bot language",
    category=HandlerCategory.CORE,
    usage="/locale",
    examples=["/locale"],
    aliases=["language", "lang"],
)
async def handle_locale_command(message: Message, **kwargs) -> None:
    await locale_command_handler(message, **kwargs)


@locale_router.callback_query(F.data.startswith("locale:"))
async def handle_locale_callback(callback: CallbackQuery, **kwargs) -> None:
    await locale_callback_handler(callback, **kwargs)
