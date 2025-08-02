"""
Configuration module for the Telegram bot.
Handles environment variables and application settings.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class BotConfig:
    """Configuration class for bot settings."""

    token: str
    log_level: str = "INFO"

    # Localization settings
    default_language: str = "en"
    locales_dir: str = "locales"
    supported_languages: list[str] = None

    # API settings
    api_base_url: str = "https://api.example.com"
    api_timeout: int = 30

    @classmethod
    def from_env(cls) -> "BotConfig":
        """Create BotConfig instance from environment variables."""
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("BOT_TOKEN environment variable is required")

        # Parse supported languages from environment variable
        supported_languages_str = os.getenv("SUPPORTED_LANGUAGES", "en,es,ru")
        supported_languages = [
            lang.strip() for lang in supported_languages_str.split(",")
        ]

        return cls(
            token=token,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            default_language=os.getenv("DEFAULT_LANGUAGE", "en"),
            locales_dir=os.getenv("LOCALES_DIR", "locales"),
            supported_languages=supported_languages,
            api_base_url=os.getenv("API_BASE_URL", "https://api.example.com"),
            api_timeout=int(os.getenv("API_TIMEOUT", "30")),
        )


# Global config instance
config = BotConfig.from_env()
