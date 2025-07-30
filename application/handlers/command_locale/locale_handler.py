from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger
from core.services.localization import get_localization_service, t


logger = get_logger()

command_locale_router = Router(name="command_locale")

@command(
    "locale",
    description="Change bot language",
    category=HandlerCategory.CORE,
    usage="/locale",
    examples=["/locale"],
    aliases=["language", "lang"]
)
async def cmd_locale(message: Message) -> None:
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
            button_text = f"✓ {lang_name}" if lang_code == current_language else lang_name
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"locale:{lang_code}"
                )
            ])
        
        # Send message with keyboard
        current_lang_text = t("locale.current", user=message.from_user, language_name=current_language_name)
        select_text = t("locale.select", user=message.from_user)
        
        await message.answer(
            f"{current_lang_text}\n\n{select_text}",
            reply_markup=keyboard
        )
        
        logger.info(f"Locale selection menu sent to user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in locale command handler: {e}")
        error_message = t("errors.generic", user=message.from_user)
        await message.answer(error_message)


@command_locale_router.callback_query(F.data.startswith("locale:"))
async def handle_locale_callback(callback: CallbackQuery) -> None:
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
