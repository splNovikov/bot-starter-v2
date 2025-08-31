"""
Core entity protocols.

Defines abstract interfaces for domain entities without depending on
concrete implementations, following the Dependency Inversion Principle.
"""

from datetime import date
from typing import Any, Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class UserEntity(Protocol):
    """
    Protocol for user entity.

    Defines the contract for user data without depending on specific
    implementation details from concrete implementations.
    """

    id: int
    platform_id: str
    platform_type: str
    is_active: bool
    metadata: Optional[Dict[str, Any]]

    @property
    def preferred_name(self) -> Optional[str]:
        """Get user's preferred name."""
        ...

    @property
    def tg_username(self) -> Optional[str]:
        """Get user's Telegram username."""
        ...

    @property
    def tg_first_name(self) -> Optional[str]:
        """Get user's Telegram first name."""
        ...

    @property
    def tg_last_name(self) -> Optional[str]:
        """Get user's Telegram last name."""
        ...

    @property
    def gender(self) -> Optional[str]:
        """Get user's gender."""
        ...

    @property
    def birth_date(self) -> Optional[date]:
        """Get user's birth date."""
        ...
