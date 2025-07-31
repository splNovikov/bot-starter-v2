from aiogram.types import CallbackQuery

from core.services.localization import get_localization_service, t
from core.utils.logger import get_logger

logger = get_logger()

async def handle_locale_answer(callback: CallbackQuery) -> None:
    try:
        # Extract language code from callback data
        language_code = callback.data.split(":")[1]

        # Get localization service
        localization_service = get_localization_service()

        # Check if language is supported
        supported_languages = localization_service.get_supported_languages()
        if language_code not in supported_languages:
            error_message = t(
                "locale.unsupported",
                user=callback.from_user,
                language_name=language_code
            )
            await callback.answer(error_message, show_alert=True)
            return

        # Set user language
        success = localization_service.set_user_language(
            callback.from_user.id,
            language_code
        )

        if success:
            # Get language name for confirmation message
            language_name = supported_languages[language_code]
            success_message = t(
                "locale.changed",
                user=callback.from_user,
                language_name=language_name
            )

            # Update the message to show success
            await callback.message.edit_text(success_message)
            await callback.answer()

            logger.info(f"Language changed to {language_code} for user {callback.from_user.id}")
        else:
            error_message = t("locale.error", user=callback.from_user)
            await callback.answer(error_message, show_alert=True)

    except Exception as e:
        logger.error(f"Error in locale callback handler: {e}")
        error_message = t("errors.generic", user=callback.from_user)
        await callback.answer(error_message, show_alert=True)
