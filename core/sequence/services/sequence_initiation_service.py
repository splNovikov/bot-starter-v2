"""
Sequence initiation service.

Provides reusable functionality for starting sequences across different commands.
"""

from typing import Optional, Tuple

from aiogram.types import Message, User

from core.sequence import get_sequence_service
from core.utils.logger import get_logger

logger = get_logger()


class SequenceInitiationService:
    """
    Service for initiating sequences across different commands.
    
    Encapsulates the common pattern of starting a sequence and sending
    the first question to the user.
    """

    @staticmethod
    async def initiate_sequence(
        message: Message,
        sequence_name: str,
        user: User,
        send_welcome_message: bool = False,
        welcome_message: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Initiate a sequence for a user.
        
        Args:
            message: Message object for reply
            sequence_name: Name of the sequence to start
            user: User object
            send_welcome_message: Whether to send a welcome message before the sequence
            welcome_message: Custom welcome message (optional)
            
        Returns:
            Tuple of (success, error_message)
        """
        sequence_service = get_sequence_service()
        if not sequence_service:
            error_msg = "❌ Sequence service is not available. Please try again later."
            logger.error("Sequence service not available during initiation")
            return False, error_msg

        try:
            # Start the sequence
            sequence_service.start_sequence(user.id, sequence_name)
            logger.info(f"Started sequence '{sequence_name}' for user {user.id}")

            # Get the first question
            next_question_key = sequence_service.get_current_question_key(
                user.id, user
            )
            
            if not next_question_key:
                error_msg = f"❌ Failed to start {sequence_name} sequence. Please try again."
                logger.error(f"Failed to get first question for sequence '{sequence_name}' for user {user.id}")
                return False, error_msg

            # Send welcome message if requested
            if send_welcome_message:
                if welcome_message:
                    await message.answer(welcome_message)
                else:
                    # Default welcome message
                    await message.answer(f"🎯 Starting {sequence_name.replace('_', ' ').title()} sequence...")

            # Send the first question
            success = await sequence_service.send_question(
                message, next_question_key, user
            )
            
            if not success:
                error_msg = f"❌ Failed to send first question for {sequence_name} sequence."
                logger.error(f"Failed to send first question for sequence '{sequence_name}' to user {user.id}")
                return False, error_msg

            logger.info(f"Successfully initiated sequence '{sequence_name}' for user {user.id}")
            return True, None

        except Exception as e:
            error_msg = f"❌ An error occurred while starting the {sequence_name} sequence. Please try again."
            logger.error(
                f"Error starting {sequence_name} sequence for user {user.id}: {e}"
            )
            return False, error_msg

    @staticmethod
    async def initiate_user_info_sequence(message: Message, user: User) -> Tuple[bool, Optional[str]]:
        """
        Initiate the user_info sequence specifically.
        
        Args:
            message: Message object for reply
            user: User object
            
        Returns:
            Tuple of (success, error_message)
        """
        return await SequenceInitiationService.initiate_sequence(
            message=message,
            sequence_name="user_info",
            user=user,
            send_welcome_message=False  # No welcome message for user_info sequence
        )

    @staticmethod
    async def initiate_sequence_with_welcome(
        message: Message,
        sequence_name: str,
        user: User,
        welcome_message: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Initiate a sequence with a welcome message.
        
        Args:
            message: Message object for reply
            sequence_name: Name of the sequence to start
            user: User object
            welcome_message: Custom welcome message (optional)
            
        Returns:
            Tuple of (success, error_message)
        """
        return await SequenceInitiationService.initiate_sequence(
            message=message,
            sequence_name=sequence_name,
            user=user,
            send_welcome_message=True,
            welcome_message=welcome_message,
        )


# Global instance for easy access
_sequence_initiation_service: Optional[SequenceInitiationService] = None


def get_sequence_initiation_service() -> SequenceInitiationService:
    """
    Get the global sequence initiation service instance.
    
    Returns:
        SequenceInitiationService instance
    """
    global _sequence_initiation_service
    if _sequence_initiation_service is None:
        _sequence_initiation_service = SequenceInitiationService()
    return _sequence_initiation_service


__all__ = [
    "SequenceInitiationService",
    "get_sequence_initiation_service",
] 