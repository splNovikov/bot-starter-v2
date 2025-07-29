"""
Language management handlers for the Telegram bot.

Provides commands for users to view supported languages and change their language preferences.
"""

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger
from core.services.localization import t, get_localization_service

logger = get_logger()


@command(
    "language",
    description="View and change your language preference",
    category=HandlerCategory.USER,
    usage="/language",
    examples=["/language", "/lang"],
    aliases=["lang"],
    tags=["language", "localization", "settings"]
)
async def cmd_language(message: Message) -> None:
    """Handle /language command - show current language and options to change."""
    try:
        localization_service = get_localization_service()
        current_language = localization_service.get_user_language(message.from_user)
        supported_languages = localization_service.get_supported_languages()
        
        # Create inline keyboard with language options
        keyboard_buttons = []
        for lang_code, lang_name in supported_languages.items():
            # Mark current language with a checkmark
            button_text = f"✅ {lang_name}" if lang_code == current_language else lang_name
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"set_language:{lang_code}"
                )
            ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        # Create message text
        current_lang_name = supported_languages.get(current_language, current_language.upper())
        message_text = t(
            "commands.language.current_and_options",
            user=message.from_user,
            current_language=current_lang_name
        )
        
        logger.info(f"Language command requested by user {message.from_user.id}")
        
        await message.answer(message_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in language command handler: {e}")
        error_message = t("errors.generic", user=message.from_user)
        await message.answer(error_message)


# This will be registered manually with the user_router
async def handle_language_selection(callback_query: CallbackQuery) -> None:
    """Handle language selection from inline keyboard."""
    try:
        # Extract language code from callback data
        language_code = callback_query.data.split(":", 1)[1]
        
        localization_service = get_localization_service()
        user_id = callback_query.from_user.id
        
        # Set user language
        success = localization_service.set_user_language(user_id, language_code)
        
        if success:
            # Get language name for confirmation
            supported_languages = localization_service.get_supported_languages()
            language_name = supported_languages.get(language_code, language_code.upper())
            
            # Send confirmation in the new language
            confirmation_message = t(
                "commands.language.changed_successfully",
                user=callback_query.from_user,
                language_name=language_name
            )
            
            logger.info(f"User {user_id} changed language to: {language_code}")
        else:
            # Send error message
            confirmation_message = t(
                "commands.language.change_failed",
                user=callback_query.from_user
            )
            
            logger.warning(f"Failed to change language to {language_code} for user {user_id}")
        
        # Edit the original message to show the result
        await callback_query.message.edit_text(confirmation_message)
        
        # Answer the callback query
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in language selection handler: {e}")
        error_message = t("errors.generic", user=callback_query.from_user)
        
        try:
            await callback_query.message.edit_text(error_message)
            await callback_query.answer()
        except Exception:
            # If editing fails, just answer the callback query
            await callback_query.answer(error_message, show_alert=True)


@command(
    "languages",
    description="Show all supported languages",
    category=HandlerCategory.USER,  
    usage="/languages",
    examples=["/languages"],
    tags=["language", "localization", "info"]
)
async def cmd_languages(message: Message) -> None:
    """Handle /languages command - show all supported languages."""
    try:
        localization_service = get_localization_service()
        supported_languages = localization_service.get_supported_languages()
        current_language = localization_service.get_user_language(message.from_user)
        
        # Build languages list
        languages_list = []
        for lang_code, lang_name in supported_languages.items():
            if lang_code == current_language:
                languages_list.append(f"✅ {lang_name} ({lang_code})")
            else:
                languages_list.append(f"   {lang_name} ({lang_code})")
        
        languages_text = "\n".join(languages_list)
        
        message_text = t(
            "commands.language.supported_languages",
            user=message.from_user,
            languages_list=languages_text
        )
        
        logger.info(f"Languages command requested by user {message.from_user.id}")
        
        await message.answer(message_text)
        
    except Exception as e:
        logger.error(f"Error in languages command handler: {e}")
        error_message = t("errors.generic", user=message.from_user)
        await message.answer(error_message) 