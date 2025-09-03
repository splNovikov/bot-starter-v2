from aiogram import Router
from aiogram.types import CallbackQuery, Message

from core.handlers.decorators import callback_query, command
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
async def handle_start_command(message: Message, **kwargs) -> None:
    await start_command_handler(message, **kwargs)


@callback_query(
    "start_ready",
    "start_ready:",
    description="Handle start ready callback",
    category=HandlerCategory.CORE,
)
async def handle_start_callback(callback: CallbackQuery, **kwargs) -> None:
    await start_callback_handler(callback, **kwargs)
