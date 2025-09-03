"""
Data handling logic for birth date information in user_info sequence.

This module contains centralized handlers for saving user birth date data
during the user_info sequence.
"""

from aiogram.types import User

from core.utils import get_logger
from core.utils.context_utils import get_user_service
from core.utils.date_validator import parse_birth_date_to_iso

logger = get_logger()


async def _save_birth_date(user: User, birth_date_text: str) -> bool:
    """
    Private function to save birth date to user metadata.

    Args:
        user: Telegram User object
        birth_date_text: User's birth date in DD.MM.YYYY format

    Returns:
        True if save was successful, False otherwise
    """
    logger.info(f"Saving birth date for user {user.id}: {birth_date_text}")

    try:
        # Get user service from context (Clean Architecture)
        user_service = get_user_service(kwargs)
        logger.debug(f"User service retrieved: {user_service is not None}")
    except Exception as e:
        logger.error(f"Failed to resolve user service: {e}")
        return False

    try:
        # Parse and convert date to ISO format
        iso_date = parse_birth_date_to_iso(birth_date_text)
        logger.debug(
            f"Converted birth date '{birth_date_text}' to ISO format: {iso_date}"
        )

        # Update user metadata with birth date
        logger.debug(f"Attempting to update user {user.id} with birth date: {iso_date}")
        updated_user = await user_service.update_user(user, {"birth_date": iso_date})

        if updated_user:
            logger.info(
                f"Successfully saved birth date '{birth_date_text}' (ISO: {iso_date}) for user {user.id}"
            )
            logger.debug(f"Updated user data: {updated_user}")
            return True
        else:
            logger.error(
                f"Failed to save birth date for user {user.id} - update_user returned None"
            )
            return False

    except ValueError as e:
        logger.error(f"Invalid birth date format for user {user.id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error saving birth date for user {user.id}: {e}")
        logger.exception("Full exception details:")
        return False


async def handle_birth_date_save(user: User, birth_date_text: str) -> bool:
    """
    Handle saving birth date to user metadata.

    Args:
        user: Telegram User object
        birth_date_text: User's birth date in DD.MM.YYYY format

    Returns:
        True if save was successful, False otherwise
    """
    return await _save_birth_date(user, birth_date_text)
