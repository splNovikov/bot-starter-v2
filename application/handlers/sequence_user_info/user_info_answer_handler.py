from aiogram.types import CallbackQuery

from core.sequence import get_sequence_service
from core.utils.logger import get_logger

logger = get_logger()


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
            callback.from_user.id, answer_value, callback.from_user
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
                await sequence_service.send_completion_message(
                    callback.message, session, callback.from_user
                )
        elif next_question_key:
            # Send next question
            await sequence_service.send_question(
                callback.message, next_question_key, callback.from_user
            )
        else:
            await callback.message.answer(
                "❌ Failed to get next question. Please try again."
            )

    except Exception as e:
        logger.error(
            f"Error processing user info answer for user {callback.from_user.id}: {e}"
        )
        await callback.answer("❌ An error occurred while processing your answer.")
