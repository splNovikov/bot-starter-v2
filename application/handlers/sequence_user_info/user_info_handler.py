from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from core.sequence import sequence_handler, get_sequence_service
from core.utils.logger import get_logger


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


@sequence_user_info_router.callback_query(F.data.startswith("seq_answer:user_info:"))
async def handle_user_info_answer(callback: CallbackQuery):
    sequence_service = get_sequence_service()
    if not sequence_service:
        await callback.answer("❌ Sequence service is not available.")
        return
    
    try:
        # Parse callback data: seq_answer:user_info:question_key:answer_value
        parts = callback.data.split(":")
        if len(parts) != 4:
            await callback.answer("❌ Invalid callback data.")
            return
        
        _, sequence_name, question_key, answer_value = parts
        
        # Process the answer
        success, error_message, next_question_key = sequence_service.process_answer(
            callback.from_user.id, 
            answer_value, 
            callback.from_user
        )
        
        if not success:
            await callback.answer(f"❌ {error_message}")
            return
        
        # Answer the callback
        await callback.answer("✅ Answer recorded!")
        
        # Check if sequence is complete
        if sequence_service.is_sequence_complete(callback.from_user.id):
            # Send completion message
            session = sequence_service.get_session(callback.from_user.id)
            if session:
                await sequence_service.send_completion_message(callback.message, session, callback.from_user)
        elif next_question_key:
            # Send next question
            await sequence_service.send_question(callback.message, next_question_key, callback.from_user)
        else:
            await callback.message.answer("❌ Failed to get next question. Please try again.")
            
    except Exception as e:
        logger.error(f"Error processing user info answer for user {callback.from_user.id}: {e}")
        await callback.answer("❌ An error occurred while processing your answer.")
