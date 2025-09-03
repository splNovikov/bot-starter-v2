"""
Validation error localization service.

This service handles localization of validation errors in the application layer.
"""

from typing import Any, Dict, Optional

from core.sequence.protocols import TranslatorProtocol
from core.utils.date_validator import DateValidationError


class ValidationErrorService:
    """Service for localizing validation errors."""

    # Mapping of error types to localization keys
    DATE_ERROR_KEY_MAP = {
        DateValidationError.INVALID_FORMAT: "sequence.errors.invalid_birth_date_format",
        DateValidationError.INVALID_YEAR: "sequence.errors.invalid_birth_date_year",
        DateValidationError.INVALID_MONTH: "sequence.errors.invalid_birth_date_month",
        DateValidationError.INVALID_DAY: "sequence.errors.invalid_birth_date_day",
        DateValidationError.FUTURE_DATE: "sequence.errors.birth_date_in_future",
        DateValidationError.UNREALISTIC_DATE: "sequence.errors.birth_date_unrealistic",
        DateValidationError.INVALID_DATE: "sequence.errors.invalid_date_validation",
    }

    # Fallback English messages
    DATE_ERROR_FALLBACK = {
        DateValidationError.INVALID_FORMAT: "Invalid date format. Please use DD.MM.YYYY format (e.g., 15.03.1990)",
        DateValidationError.INVALID_YEAR: "Year must be between 1900 and current year",
        DateValidationError.INVALID_MONTH: "Month must be between 01 and 12",
        DateValidationError.INVALID_DAY: "Day must be between 01 and 31",
        DateValidationError.FUTURE_DATE: "Birth date cannot be in the future",
        DateValidationError.UNREALISTIC_DATE: "Birth date seems unrealistic",
        DateValidationError.INVALID_DATE: "Invalid date. Please check day and month values",
    }

    @staticmethod
    def localize_date_error(
        error: DateValidationError,
        translator: Optional[TranslatorProtocol] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Localize a date validation error.

        Args:
            error: The date validation error enum
            translator: Optional translator for localized messages
            context: Optional context for translation

        Returns:
            Localized error message
        """
        if translator and error in ValidationErrorService.DATE_ERROR_KEY_MAP:
            key = ValidationErrorService.DATE_ERROR_KEY_MAP[error]
            return translator.translate(key, context)

        # Fallback to English message
        return ValidationErrorService.DATE_ERROR_FALLBACK.get(
            error, "Invalid date format"
        )
