"""
Configuration module for the Telegram bot.
Handles environment variables and application settings.
"""

from dataclasses import dataclass
import os

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

    # API settings
    api_base_url: str = "https://api.example.com"
    api_timeout: int = 30

    @classmethod
    def from_env(cls) -> "BotConfig":
        """Create BotConfig instance from environment variables."""
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("BOT_TOKEN environment variable is required")

        return cls(
            token=token,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            default_language=os.getenv("DEFAULT_LANGUAGE", "en"),
            locales_dir=os.getenv("LOCALES_DIR", "locales"),
            api_base_url=os.getenv("API_BASE_URL", "https://api.example.com"),
            api_timeout=int(os.getenv("API_TIMEOUT", "30")),
        )


# Global config instance
config = BotConfig.from_env()
