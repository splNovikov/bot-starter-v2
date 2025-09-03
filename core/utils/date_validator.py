"""
Date validation utilities.

This module provides date validation functions that can be used across the application.
Pure functions without dependencies on localization or other layers.
"""

from datetime import datetime
from enum import Enum
import re
from typing import Optional, Tuple


class DateValidationError(Enum):
    """Enumeration of possible date validation errors."""

    INVALID_FORMAT = "invalid_format"
    INVALID_YEAR = "invalid_year"
    INVALID_MONTH = "invalid_month"
    INVALID_DAY = "invalid_day"
    FUTURE_DATE = "future_date"
    UNREALISTIC_DATE = "unrealistic_date"
    INVALID_DATE = "invalid_date"


def validate_birth_date(date_text: str) -> Tuple[bool, Optional[DateValidationError]]:
    """
    Validate birth date in DD.MM.YYYY format.

    This is a pure function that returns validation result and error type enum
    without any dependencies on localization.

    Args:
        date_text: Date text to validate

    Returns:
        Tuple of (is_valid, error_type)
        - is_valid: True if date is valid, False otherwise
        - error_type: DateValidationError enum if validation failed, None if valid
    """
    # Check format DD.MM.YYYY
    pattern = r"^(\d{2})\.(\d{2})\.(\d{4})$"
    match = re.match(pattern, date_text)

    if not match:
        return False, DateValidationError.INVALID_FORMAT

    day, month, year = match.groups()

    try:
        # Convert to integers
        day_int = int(day)
        month_int = int(month)
        year_int = int(year)

        # Validate date ranges
        if year_int < 1900 or year_int > datetime.now().year:
            return False, DateValidationError.INVALID_YEAR

        if month_int < 1 or month_int > 12:
            return False, DateValidationError.INVALID_MONTH

        if day_int < 1 or day_int > 31:
            return False, DateValidationError.INVALID_DAY

        # Try to create a real date to validate
        try:
            birth_date = datetime(year_int, month_int, day_int)

            # Check if date is not in the future
            if birth_date > datetime.now():
                return False, DateValidationError.FUTURE_DATE

            # Check for reasonable minimum age (e.g., not older than 150 years)
            min_date = datetime.now().replace(year=datetime.now().year - 150)
            if birth_date < min_date:
                return False, DateValidationError.UNREALISTIC_DATE

        except ValueError:
            return False, DateValidationError.INVALID_DATE

        return True, None

    except ValueError:
        return False, DateValidationError.INVALID_FORMAT


def parse_birth_date_to_iso(date_text: str) -> str:
    """
    Parse birth date from DD.MM.YYYY format to ISO format.

    Args:
        date_text: Date in DD.MM.YYYY format

    Returns:
        Date in ISO format (YYYY-MM-DD)

    Raises:
        ValueError: If date format is invalid
    """
    try:
        # Parse DD.MM.YYYY format
        day, month, year = date_text.split(".")
        date_obj = datetime(int(year), int(month), int(day))
        return date_obj.strftime("%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"Invalid date format: {date_text}") from e
