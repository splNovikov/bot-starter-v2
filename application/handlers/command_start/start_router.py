from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory

from .start_callback_handler import start_callback_handler
from .start_command_handler import start_command_handler

start_router = Router(name="start_router")


@command(
    "start",
    description="Get a welcome greeting message",
    category=HandlerCategory.CORE,
    usage="/start",
    examples=["/start"],
)
async def handle_start_command(message: Message) -> None:
    await start_command_handler(message)


@start_router.callback_query(F.data.startswith("start_ready:"))
async def handle_start_callback(callback: CallbackQuery) -> None:
    await start_callback_handler(callback)
