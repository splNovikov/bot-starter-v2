"""
User-related types and data structures.

Contains application-specific user data structures.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional


@dataclass
class UserData:
    """User data structure matching backend User model."""

    id: int
    platform_id: str
    platform_type: str
    metadata: Optional[Dict[str, Any]] = None

    @property
    def display_name(self) -> str:
        """Get display name from metadata or return platform_id."""
        if self.metadata and "name" in self.metadata:
            return self.metadata["name"]
        elif self.metadata and "username" in self.metadata:
            return self.metadata["username"]
        return self.platform_id

    @property
    def name(self) -> Optional[str]:
        """Get user's name from metadata."""
        return self.metadata.get("name") if self.metadata else None

    @property
    def gender(self) -> Optional[str]:
        """Get user's gender from metadata."""
        return self.metadata.get("gender") if self.metadata else None

    @property
    def birth_date(self) -> Optional[date]:
        """Get user's birth date from metadata."""
        if self.metadata and "birth_date" in self.metadata:
            birth_date_str = self.metadata["birth_date"]
            if isinstance(birth_date_str, str):
                try:
                    return date.fromisoformat(birth_date_str)
                except ValueError:
                    return None
        return None

    @property
    def marital_status(self) -> Optional[str]:
        """Get user's marital status from metadata."""
        return self.metadata.get("marital_status") if self.metadata else None

    @property
    def eye_color(self) -> Optional[str]:
        """Get user's eye color from metadata."""
        return self.metadata.get("eye_color") if self.metadata else None

    @property
    def notification_time(self) -> Optional[str]:
        """Get user's notification time from metadata."""
        return self.metadata.get("notification_time") if self.metadata else None

    @property
    def timezone(self) -> Optional[str]:
        """Get user's timezone from metadata."""
        return self.metadata.get("timezone") if self.metadata else None

    # Legacy properties for backward compatibility
    @property
    def first_name(self) -> Optional[str]:
        """Get first name from metadata (legacy property)."""
        return self.metadata.get("first_name") if self.metadata else None

    @property
    def username(self) -> Optional[str]:
        """Get username from metadata (legacy property)."""
        return self.metadata.get("username") if self.metadata else None

    @property
    def last_name(self) -> Optional[str]:
        """Get last name from metadata (legacy property)."""
        return self.metadata.get("last_name") if self.metadata else None

    @property
    def email(self) -> Optional[str]:
        """Get email from metadata (legacy property)."""
        return self.metadata.get("email") if self.metadata else None

    @property
    def phone(self) -> Optional[str]:
        """Get phone from metadata (legacy property)."""
        return self.metadata.get("phone") if self.metadata else None

    @property
    def is_active(self) -> bool:
        """Get active status from metadata, default to True."""
        if self.metadata and "is_active" in self.metadata:
            return self.metadata["is_active"]
        return True


__all__ = ["UserData"]
