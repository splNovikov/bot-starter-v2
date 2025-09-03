from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from core.sequence import sequence_handler
from core.utils.logger import get_logger

from .user_info_callback_handler import user_info_callback_handler
from .user_info_command_handler import user_info_command_handler
from .user_info_message_handler import user_info_message_handler

logger = get_logger()

sequence_user_info_router = Router(name="sequence_user_info")


@sequence_handler(
    "user_info",
    sequence_name="user_info",
    questions=[
        "confirm_user_name",
        "preferred_name",
        "gender",
        "birth_date",
        "eyes_color",
        "marital_status",
    ],
    description="Collect user information (name, gender, birth date, eyes color, marital status)",
    show_progress=True,
    allow_restart=True,
    generate_summary=True,
)
async def handle_user_info_command(message: Message):
    await user_info_command_handler(message)


@sequence_user_info_router.callback_query(F.data.startswith("seq_answer:user_info:"))
async def handle_user_info_callback(callback: CallbackQuery, **kwargs):
    await user_info_callback_handler(callback, **kwargs)


@sequence_user_info_router.message(F.text)
async def handle_user_info_message(message: Message, **kwargs):
    await user_info_message_handler(message, **kwargs)
