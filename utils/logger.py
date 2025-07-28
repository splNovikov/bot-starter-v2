"""
Logging configuration using loguru.
Provides structured logging with proper formatting and error handling.
"""

import sys
from loguru import logger
from config import config


def setup_logger() -> None:
    """
    Configure loguru logger with custom format and settings.
    
    Features:
    - Colored output for console
    - Proper log levels
    - Exception tracing
    - Structured format
    """
    # Remove default logger
    logger.remove()
    
    # Add console logger with custom format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=config.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Add file logger for errors
    logger.add(
        "logs/bot_errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="10 MB",
        retention="1 month",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    logger.info("Logger configured successfully")


def get_logger():
    """Get configured logger instance."""
    return logger 