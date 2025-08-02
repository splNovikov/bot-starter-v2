from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from core.services.localization import get_localization_service, t
from core.utils.logger import get_logger

logger = get_logger()


async def handle_locale(message: Message) -> None:
    try:
        # Get localization service
        localization_service = get_localization_service()

        # Get current user language
        current_language = localization_service.get_user_language(message.from_user)
        current_language_name = t("_language_name", language=current_language)

        # Get supported languages
        supported_languages = localization_service.get_supported_languages()

        # Create inline keyboard with language options
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        for lang_code, lang_name in supported_languages.items():
            # Mark current language with a checkmark
            button_text = (
                f"✓ {lang_name}" if lang_code == current_language else lang_name
            )
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=button_text, callback_data=f"locale:{lang_code}"
                    )
                ]
            )

        # Send message with keyboard
        current_lang_text = t(
            "locale.current",
            user=message.from_user,
            language_name=current_language_name,
        )
        select_text = t("locale.select", user=message.from_user)

        await message.answer(
            f"{current_lang_text}\n\n{select_text}", reply_markup=keyboard
        )

        logger.info(f"Locale selection menu sent to user {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in locale command handler: {e}")
        error_message = t("errors.generic", user=message.from_user)
        await message.answer(error_message)
