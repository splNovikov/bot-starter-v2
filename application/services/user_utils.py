"""
User utilities for common user management operations.

This module provides utility functions for user existence checking,
creation, and other common user-related operations across handlers.
"""

from aiogram.types import User

from application.types import UserData
from core.utils.context_utils import get_user_service
from core.utils.logger import get_logger

logger = get_logger()


async def ensure_user_exists(user: User, context: dict = None) -> UserData | None:
    """
    Ensure user exists in the system, creating them if necessary.

    This function checks if a user exists in the API and creates them
    if they don't exist. This is used across multiple handlers to
    maintain consistent user management behavior.

    Args:
        user: Telegram User object from the message

    Returns:
        UserData object if user exists or was created successfully,
        None if user service is unavailable or creation failed

    Raises:
        Exception: Propagates any unexpected exceptions for proper error handling
    """
    try:
        # Get user service from context (Clean Architecture)
        if context is None:
            logger.error("Context is required for service resolution")
            return None
        user_service = get_user_service(context)
    except Exception as e:
        logger.error(f"Failed to resolve user service: {e}")
        return None

    try:
        # Try to fetch user from API
        user_data = await user_service.get_user(user)

        if not user_data:
            # User not found - try to create user in database
            logger.info(f"User {user.id} not found - attempting to create")
            user_data = await user_service.create_user(user)

            if user_data:
                logger.info(f"Successfully created user {user.id}")
            else:
                logger.warning(f"Failed to create user {user.id}")
        else:
            logger.debug(f"User {user.id} already exists")

        return user_data

    except Exception as e:
        logger.error(f"Error ensuring user {user.id} exists: {e}")
        raise  # Re-raise for proper error handling in calling code


async def create_enhanced_context(user: User, kwargs: dict = None) -> dict:
    """
    Create enhanced context with preferred_name from user data.

    This function creates a context dictionary that includes both the basic
    user information and the preferred_name from saved user data, ensuring
    consistency between database fields and context parameters.

    Args:
        user: Telegram User object
        kwargs: Context dictionary with services

    Returns:
        Dictionary with user context including preferred_name
    """
    context = {"user": user, "user_id": user.id}

    # Always get Telegram display name for presumably_user_name
    try:
        # Get user service from context (Clean Architecture)
        if kwargs is None:
            context["presumably_user_name"] = "Anonymous"
        else:
            user_service = get_user_service(kwargs)
            telegram_display_name = user_service.get_user_display_name(user)
            context["presumably_user_name"] = (
                telegram_display_name  # Always Telegram name
            )
    except Exception as e:
        logger.error(f"Failed to resolve user service: {e}")
        context["presumably_user_name"] = "Anonymous"

    try:
        # Get user data to extract preferred_name
        user_data = await ensure_user_exists(user, kwargs)

        if user_data and user_data.preferred_name:
            # Use saved preferred_name (consistent with database field)
            context["preferred_name"] = user_data.preferred_name
        else:
            # Fallback to Telegram display name for preferred_name too
            context["preferred_name"] = context["presumably_user_name"]

    except Exception as e:
        logger.warning(f"Could not get enhanced context for user {user.id}: {e}")
        # Fallback: preferred_name = presumably_user_name (Telegram display name)
        context["preferred_name"] = context["presumably_user_name"]

    return context
