from aiogram.types import Message

from core.sequence import get_sequence_initiation_service
from core.utils.logger import get_logger

logger = get_logger()


async def handle_user_info(message: Message):
    sequence_initiation_service = get_sequence_initiation_service()
    
    success, error_message = await sequence_initiation_service.initiate_user_info_sequence(
        message, message.from_user
    )
    
    if not success:
        await message.answer(error_message)
