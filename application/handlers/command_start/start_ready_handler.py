from aiogram.types import CallbackQuery

from core.sequence import get_sequence_initiation_service
from core.services import t
from core.utils import get_logger

logger = get_logger()

# Constants for callback data
CALLBACK_PREFIX = "start_ready"
SEQUENCE_SEPARATOR = ":"
VALID_SEQUENCES = {"user_info"}  # Add more sequences as needed


async def handle_start_ready(callback: CallbackQuery) -> None:
    """
    Handle the start ready callback for initiating user sequences.

    Args:
        callback: The callback query containing sequence information

    Expected callback data format: "start_ready:sequence_name"
    """
    try:
        # Validate callback data format
        if not callback.data:
            logger.warning(f"Empty callback data from user {callback.from_user.id}")
            await callback.answer(t("errors.invalid_callback", user=callback.from_user))
            return

        # Parse and validate callback data
        parts = callback.data.split(SEQUENCE_SEPARATOR)
        if len(parts) != 2 or parts[0] != CALLBACK_PREFIX:
            logger.warning(
                f"Invalid callback data format: {callback.data} from user {callback.from_user.id}"
            )
            await callback.answer(t("errors.invalid_callback", user=callback.from_user))
            return

        sequence_name = parts[1]

        # Validate sequence name
        if sequence_name not in VALID_SEQUENCES:
            logger.warning(
                f"Invalid sequence name: {sequence_name} from user {callback.from_user.id}"
            )
            await callback.answer(t("errors.invalid_sequence", user=callback.from_user))
            return

        # Remove the keyboard immediately to prevent multiple clicks
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception as e:
            logger.warning(
                f"Failed to remove keyboard for user {callback.from_user.id}: {e}"
            )
            # Continue execution even if keyboard removal fails

        # Add a small visual confirmation to the message
        try:
            current_text = callback.message.text
            confirmation_text = t(
                "handlers.start.greetings.ready_confirmation", user=callback.from_user
            )
            updated_text = current_text + f"\n\n{confirmation_text}"
            await callback.message.edit_text(updated_text, parse_mode="HTML")
        except Exception as e:
            logger.warning(
                f"Failed to update message for user {callback.from_user.id}: {e}"
            )
            # Continue execution even if message update fails

        # Answer the callback to remove loading state
        await callback.answer(
            t("handlers.start.greetings.sequence_starting", user=callback.from_user)
        )

        # Get sequence initiation service
        sequence_initiation_service = get_sequence_initiation_service()

        if not sequence_initiation_service:
            logger.error("Sequence initiation service not available")
            await callback.message.answer(
                t("errors.service_unavailable", user=callback.from_user)
            )
            return

        # Initiate the user info sequence
        (
            success,
            error_message,
        ) = await sequence_initiation_service.initiate_user_info_sequence(
            callback.message, callback.from_user
        )

        if not success:
            logger.error(
                f"Failed to start {sequence_name} sequence for user {callback.from_user.id}: {error_message}"
            )
            await callback.message.answer(
                t("errors.sequence_initiation_failed", user=callback.from_user)
            )
        else:
            logger.info(
                f"Successfully initiated {sequence_name} sequence for user {callback.from_user.id}"
            )

    except Exception as e:
        logger.error(
            f"Unexpected error in start ready handler for user {callback.from_user.id}: {e}"
        )
        await callback.answer(t("errors.generic", user=callback.from_user))
