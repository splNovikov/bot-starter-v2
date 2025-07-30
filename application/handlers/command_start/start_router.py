from aiogram import Router
from aiogram.types import Message

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory

from .start_handler import handle_start

start_router = Router(name="start_router")

@command(
    "start",
    description="Get a welcome greeting message",
    category=HandlerCategory.CORE,
    usage="/start",
    examples=["/start"]
)
async def cmd_start(message: Message) -> None:
    await handle_start(message)
