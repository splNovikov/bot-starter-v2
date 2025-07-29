"""
Localization service for the Telegram bot.

Provides centralized text localization with support for multiple languages,
parameter substitution, user preferences, and automatic language detection.

This is a core infrastructure service that can be reused across different
business domains and applications.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache
from aiogram.types import User

from core.utils.logger import get_logger
from config import config

logger = get_logger()


class LocalizationService:
    """
    Centralized localization service for bot messages.
    
    Features:
    - JSON-based translations with lazy loading
    - Parameter substitution in messages
    - User language preference support
    - Automatic fallback to default language
    - Caching for performance
    """
    
    def __init__(self, locales_dir: str = "locales", default_language: str = "en"):
        """
        Initialize localization service.
        
        Args:
            locales_dir: Directory containing locale JSON files
            default_language: Default language code to fall back to
        """
        self.locales_dir = Path(locales_dir)
        self.default_language = default_language
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._user_languages: Dict[int, str] = {}
        self.locales_dir.mkdir(exist_ok=True)
        
        logger.info(f"Localization service initialized with directory: {self.locales_dir}")
    
    @lru_cache(maxsize=32)
    def _load_language(self, language_code: str) -> Dict[str, Any]:
        """
        Load translations for a specific language with caching.
        
        Args:
            language_code: Language code (e.g., 'en', 'es', 'ru')
            
        Returns:
            Dictionary containing translations for the language
        """
        locale_file = self.locales_dir / f"{language_code}.json"
        
        if not locale_file.exists():
            if language_code != self.default_language:
                logger.warning(f"Locale file not found: {locale_file}, falling back to {self.default_language}")
                return self._load_language(self.default_language)
            else:
                logger.error(f"Default locale file not found: {locale_file}")
                return {}
        
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                logger.debug(f"Loaded {len(translations)} translations for language: {language_code}")
                return translations
                
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading locale file {locale_file}: {e}")
            if language_code != self.default_language:
                return self._load_language(self.default_language)
            return {}
    
    def get_user_language(self, user: User) -> str:
        """
        Get the preferred language for a user.
        
        Priority:
        1. Stored user preference
        2. Telegram user language_code
        3. Default language
        
        Args:
            user: Telegram user object
            
        Returns:
            Language code for the user
        """
        user_id = user.id
        
        if user_id in self._user_languages:
            return self._user_languages[user_id]
        
        if user.language_code:
            language_code = user.language_code.split('-')[0].lower()
            locale_file = self.locales_dir / f"{language_code}.json"
            if locale_file.exists():
                logger.debug(f"Detected language {language_code} for user {user_id}")
                return language_code
        
        logger.debug(f"Using default language {self.default_language} for user {user_id}")
        return self.default_language
    
    def set_user_language(self, user_id: int, language_code: str) -> bool:
        """
        Set language preference for a user.
        
        Args:
            user_id: Telegram user ID
            language_code: Preferred language code
            
        Returns:
            True if language was set successfully, False if language not supported
        """
        locale_file = self.locales_dir / f"{language_code}.json"
        if not locale_file.exists():
            logger.warning(f"Cannot set unsupported language {language_code} for user {user_id}")
            return False
        
        self._user_languages[user_id] = language_code
        logger.info(f"Set language {language_code} for user {user_id}")
        return True
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages.
        
        Returns:
            Dictionary mapping language codes to language names
        """
        supported = {}
        
        for locale_file in self.locales_dir.glob("*.json"):
            language_code = locale_file.stem
            
            # Try to get language name from the translation file
            try:
                translations = self._load_language(language_code)
                language_name = translations.get('_language_name', language_code.upper())
                supported[language_code] = language_name
            except Exception:
                supported[language_code] = language_code.upper()
        
        return supported
    
    def t(self, key: str, user: Optional[User] = None, language: Optional[str] = None, raw: bool = False, **params) -> Any:
        """
        Translate a message key to the appropriate language.
        
        Args:
            key: Translation key (can be nested with dots, e.g., 'messages.greeting')
            user: Telegram user object for language detection
            language: Override language code
            raw: Return raw translation data without string formatting
            **params: Parameters for string formatting
            
        Returns:
            Translated and formatted message, or raw translation data if raw=True
        """
        if language:
            target_language = language
        elif user:
            target_language = self.get_user_language(user)
        else:
            target_language = self.default_language
        
        translations = self._load_language(target_language)
        
        value = translations
        for key_part in key.split('.'):
            if isinstance(value, dict) and key_part in value:
                value = value[key_part]
            else:
                if target_language != self.default_language:
                    logger.warning(f"Translation key '{key}' not found in {target_language}, trying {self.default_language}")
                    return self.t(key, language=self.default_language, raw=raw, **params)
                else:
                    logger.error(f"Translation key '{key}' not found in default language {self.default_language}")
                    return f"[{key}]" if not raw else None
        
        if raw:
            return value
        
        if not isinstance(value, str):
            logger.error(f"Translation key '{key}' does not resolve to a string: {type(value)}")
            return f"[{key}]"
        
        try:
            return value.format(**params)
        except (KeyError, ValueError) as e:
            logger.error(f"Error formatting translation '{key}' with params {params}: {e}")
            return value


# Global localization service instance
_localization_service: Optional[LocalizationService] = None


def get_localization_service() -> LocalizationService:
    """Get the global localization service instance."""
    global _localization_service
    if _localization_service is None:
        _localization_service = LocalizationService(
            locales_dir=config.locales_dir,
            default_language=config.default_language
        )
    return _localization_service


def t(key: str, user: Optional[User] = None, language: Optional[str] = None, raw: bool = False, **params) -> Any:
    """
    Convenience function for translation.
    
    Args:
        key: Translation key
        user: Telegram user object for language detection  
        language: Override language code
        raw: Return raw translation data without string formatting
        **params: Parameters for string formatting
        
    Returns:
        Translated and formatted message, or raw translation data if raw=True
    """
    return get_localization_service().t(key, user, language, raw, **params) 