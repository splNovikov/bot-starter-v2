from aiogram.types import Message

from core.sequence import get_sequence_service
from core.utils.logger import get_logger

logger = get_logger()

async def handle_user_info(message: Message):
    sequence_service = get_sequence_service()
    if not sequence_service:
        await message.answer("❌ Sequence service is not available. Please try again later.")
        return
    
    try:
        # Start the sequence
        sequence_service.start_sequence(message.from_user.id, "user_info")
        
        # Get the first question
        next_question_key = sequence_service.get_current_question_key(message.from_user.id, message.from_user)
        if next_question_key:
            # Send the first question
            await sequence_service.send_question(message, next_question_key, message.from_user)
        else:
            await message.answer("❌ Failed to start user info sequence. Please try again.")
            
    except Exception as e:
        logger.error(f"Error starting user info sequence for user {message.from_user.id}: {e}")
        await message.answer("❌ An error occurred while starting the sequence. Please try again.")
