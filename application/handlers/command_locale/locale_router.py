from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger

from .locale_handler import handle_locale
from .locale_callback_handler import handle_locale_callback

logger = get_logger()

locale_router = Router(name="locale_router")

@command(
    "locale",
    description="Change bot language",
    category=HandlerCategory.CORE,
    usage="/locale",
    examples=["/locale"],
    aliases=["language", "lang"]
)
async def cmd_locale(message: Message) -> None:
    await handle_locale(message)

@locale_router.callback_query(F.data.startswith("locale:"))
async def locale_callback(callback: CallbackQuery) -> None:
    await handle_locale_callback(callback)
