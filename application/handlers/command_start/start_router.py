from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory

from .start_handler import handle_start
from .start_ready_handler import handle_start_ready

start_router = Router(name="start_router")


@command(
    "start",
    description="Get a welcome greeting message",
    category=HandlerCategory.CORE,
    usage="/start",
    examples=["/start"],
)
async def cmd_start(message: Message) -> None:
    await handle_start(message)


@start_router.callback_query(F.data.startswith("start_ready:"))
async def start_ready_callback(callback: CallbackQuery) -> None:
    await handle_start_ready(callback)
