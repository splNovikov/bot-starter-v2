from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from core.sequence import sequence_handler
from core.utils.logger import get_logger

from .user_info_handler import handle_user_info
from .user_info_answer_handler import handle_user_info_answer

logger = get_logger()

sequence_user_info_router = Router(name="sequence_user_info")

@sequence_handler(
    "user_info",
    sequence_name="user_info",
    questions=["eyes_color", "marital_status"],
    description="Collect user information (eyes color, marital status)",
    show_progress=True,
    allow_restart=True,
    generate_summary=True
)
async def cmd_user_info(message: Message):
    await handle_user_info(message)

@sequence_user_info_router.callback_query(F.data.startswith("seq_answer:user_info:"))
async def user_info_callback(callback: CallbackQuery):
    await handle_user_info_answer(callback)
