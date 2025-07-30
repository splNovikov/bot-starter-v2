from aiogram import Router
from aiogram.types import Message

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger
from .greeting import send_greeting


logger = get_logger()

command_start_router = Router(name="command_start")

@command(
    "start",
    description="Get a welcome greeting message",
    category=HandlerCategory.CORE,
    usage="/start",
    examples=["/start"]
)
async def cmd_start(message: Message) -> None:
    await send_greeting(message) 
