from aiogram.types import CallbackQuery

from core.di.container import get_container
from core.services.localization import LocalizationService, t
from core.utils.logger import get_logger

logger = get_logger()

# Constants for callback data
CALLBACK_SEPARATOR = ":"
EXPECTED_PARTS_COUNT = 2


async def locale_callback_handler(callback: CallbackQuery) -> None:
    """
    Handle locale selection callback for changing user language.

    Args:
        callback: The callback query containing language selection information

    Expected callback data format: "locale:language_code"
    """
    try:
        # Validate callback data
        if not callback.data:
            logger.warning(f"Empty callback data from user {callback.from_user.id}")
            await callback.answer(
                t("errors.invalid_callback", user=callback.from_user), show_alert=True
            )
            return

        # Parse and validate callback data
        parts = callback.data.split(CALLBACK_SEPARATOR)
        if len(parts) != EXPECTED_PARTS_COUNT:
            logger.warning(
                f"Invalid callback data format: {callback.data} from user {callback.from_user.id}"
            )
            await callback.answer(
                t("errors.invalid_callback", user=callback.from_user), show_alert=True
            )
            return

        language_code = parts[1]

        # Validate language code format
        if not language_code or len(language_code) != 2:
            logger.warning(
                f"Invalid language code format: {language_code} from user {callback.from_user.id}"
            )
            await callback.answer(
                t("errors.invalid_language", user=callback.from_user), show_alert=True
            )
            return

        # Get localization service
        container = get_container()
        localization_service = container.resolve(LocalizationService)

        # Check if language is supported
        supported_languages = localization_service.get_supported_languages()
        if not supported_languages:
            logger.error("No supported languages available")
            await callback.answer(
                t("errors.service_unavailable", user=callback.from_user),
                show_alert=True,
            )
            return

        if language_code not in supported_languages:
            logger.warning(
                f"Unsupported language requested: {language_code} from user {callback.from_user.id}"
            )
            error_message = t(
                "handlers.locale.unsupported",
                user=callback.from_user,
                language_name=language_code,
            )
            await callback.answer(error_message, show_alert=True)
            return

        # Set user language
        success = localization_service.set_user_language(
            callback.from_user.id, language_code
        )

        if success:
            # Get language name for confirmation message
            language_name = supported_languages[language_code]
            success_message = t(
                "handlers.locale.changed",
                user=callback.from_user,
                language_name=language_name,
            )

            # Update the message to show success
            try:
                await callback.message.edit_text(success_message)
                await callback.answer()
            except Exception as e:
                logger.warning(
                    f"Failed to update message for user {callback.from_user.id}: {e}"
                )
                # Still answer the callback to remove loading state
                await callback.answer()

            logger.info(
                f"Language changed to {language_code} for user {callback.from_user.id}"
            )
        else:
            logger.error(
                f"Failed to set language {language_code} for user {callback.from_user.id}"
            )
            error_message = t("handlers.locale.error", user=callback.from_user)
            await callback.answer(error_message, show_alert=True)

    except Exception as e:
        logger.error(
            f"Unexpected error in locale callback handler for user {callback.from_user.id}: {e}"
        )
        error_message = t("errors.generic", user=callback.from_user)
        await callback.answer(error_message, show_alert=True)
