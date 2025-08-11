from aiogram.types import Message

from core.sequence import create_translator, get_sequence_initiation_service
from core.utils.logger import get_logger

logger = get_logger()


async def user_info_command_handler(message: Message):
    sequence_initiation_service = get_sequence_initiation_service()

    # Create translator and context (infrastructure/application responsibility)
    translator = create_translator(message.from_user)
    context = {"user": message.from_user, "user_id": message.from_user.id}

    (
        success,
        error_message,
    ) = await sequence_initiation_service.initiate_user_info_sequence(
        message, translator, context
    )

    if not success:
        await message.answer(error_message, parse_mode="HTML")
