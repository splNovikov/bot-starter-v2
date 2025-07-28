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
    
    @classmethod
    def from_env(cls) -> "BotConfig":
        """Create BotConfig instance from environment variables."""
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        return cls(
            token=token,
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )


# Global config instance
config = BotConfig.from_env() 