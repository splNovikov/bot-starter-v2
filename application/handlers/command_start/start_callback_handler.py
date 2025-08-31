from aiogram.types import CallbackQuery

from application.services.user_utils import create_enhanced_context
from core.di.container import get_container
from core.sequence import SequenceInitiationService, create_translator
from core.services import t
from core.utils import get_logger

logger = get_logger()

# Constants for callback data
CALLBACK_PREFIX = "start_ready"
SEQUENCE_SEPARATOR = ":"
VALID_SEQUENCES = {"user_info"}  # Add more sequences as needed


async def start_callback_handler(callback: CallbackQuery) -> None:
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

        # Get sequence initiation service
        get_container()
        sequence_initiation_service = (
            SequenceInitiationService()
        )  # Stateless service, can be instantiated

        # Create translator and enhanced context with preferred_name
        translator = create_translator(callback.from_user)
        context = await create_enhanced_context(callback.from_user)

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
            callback.message, translator, context
        )

        if not success:
            await callback.message.answer(error_message, parse_mode="HTML")
            logger.error(
                f"Failed to start {sequence_name} sequence for user {callback.from_user.id}: {error_message}"
            )

    except Exception as e:
        logger.error(
            f"Error in start callback handler for user {callback.from_user.id}: {e}"
        )
        await callback.answer(t("errors.general_error", user=callback.from_user))
