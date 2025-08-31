"""
Data handling logic for gender information in user_info sequence.

This module contains centralized handlers for saving user gender data
during the user_info sequence.
"""

from aiogram.types import User

from core.di.container import get_container
from core.protocols.services import UserServiceProtocol
from core.utils import get_logger

logger = get_logger()


async def _save_gender(user: User, gender: str) -> bool:
    """
    Private function to save gender to user metadata.

    Args:
        user: Telegram User object
        gender: User's gender to save

    Returns:
        True if save was successful, False otherwise
    """
    logger.info(f"Saving gender for user {user.id}: {gender}")

    try:
        container = get_container()
        user_service = container.resolve(UserServiceProtocol)
        logger.debug(f"User service retrieved: {user_service is not None}")
    except Exception as e:
        logger.error(f"Failed to resolve user service: {e}")
        return False

    try:
        # Update user metadata with gender
        logger.debug(f"Attempting to update user {user.id} with gender: {gender}")
        updated_user = await user_service.update_user(user, {"gender": gender})

        if updated_user:
            logger.info(f"Successfully saved gender '{gender}' for user {user.id}")
            logger.debug(f"Updated user data: {updated_user}")
            return True
        else:
            logger.error(
                f"Failed to save gender for user {user.id} - update_user returned None"
            )
            return False

    except Exception as e:
        logger.error(f"Error saving gender for user {user.id}: {e}")
        logger.exception("Full exception details:")
        return False


async def handle_gender_save(user: User, gender: str) -> bool:
    """
    Handle saving gender to user metadata.

    Args:
        user: Telegram User object
        gender: User's gender to save

    Returns:
        True if save was successful, False otherwise
    """
    return await _save_gender(user, gender)
