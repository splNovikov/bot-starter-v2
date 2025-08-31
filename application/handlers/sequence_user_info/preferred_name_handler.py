"""
Data handling logic for user_info sequence.

This module contains centralized handlers for saving user data
during the user_info sequence.
"""

from aiogram.types import User

from core.di.container import get_container
from core.protocols.services import UserServiceProtocol
from core.utils import get_logger

logger = get_logger()


async def _save_preferred_name(user: User, preferred_name: str) -> bool:
    """
    Private function to save preferred_name to user metadata.

    Args:
        user: Telegram User object
        preferred_name: User's preferred name to save

    Returns:
        True if save was successful, False otherwise
    """
    logger.info(f"Saving preferred_name for user {user.id}: {preferred_name}")

    try:
        container = get_container()
        user_service = container.resolve(UserServiceProtocol)
        logger.debug(f"User service retrieved: {user_service is not None}")
    except Exception as e:
        logger.error(f"Failed to resolve user service: {e}")
        return False

    try:
        # Update user metadata with preferred_name
        logger.debug(
            f"Attempting to update user {user.id} with preferred_name: {preferred_name}"
        )
        updated_user = await user_service.update_user(
            user, {"preferred_name": preferred_name}
        )

        if updated_user:
            logger.info(
                f"Successfully saved preferred_name '{preferred_name}' for user {user.id}"
            )
            logger.debug(f"Updated user data: {updated_user}")
            return True
        else:
            logger.error(
                f"Failed to save preferred_name for user {user.id} - update_user returned None"
            )
            return False

    except Exception as e:
        logger.error(f"Error saving preferred_name for user {user.id}: {e}")
        logger.exception("Full exception details:")
        return False


async def handle_preferred_name_save(user: User, preferred_name: str) -> bool:
    """
    Handle saving preferred_name to user metadata.

    Args:
        user: Telegram User object
        preferred_name: User's preferred name to save

    Returns:
        True if save was successful, False otherwise
    """
    return await _save_preferred_name(user, preferred_name)


async def handle_confirm_user_name_save(user: User) -> bool:
    """
    Handle saving user's actual name as preferred_name when user confirms their name.

    Args:
        user: Telegram User object

    Returns:
        True if save was successful, False otherwise
    """
    try:
        container = get_container()
        user_service = container.resolve(UserServiceProtocol)
    except Exception as e:
        logger.error(f"Failed to resolve user service: {e}")
        return False

    # Get user's actual display name from Telegram
    actual_name = user_service.get_user_display_name(user)
    return await _save_preferred_name(user, actual_name)
