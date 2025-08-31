from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional

from core.protocols.entities import UserEntity


@dataclass
class UserData(UserEntity):
    id: int
    platform_id: str
    platform_type: str
    is_active: bool
    metadata: Optional[Dict[str, Any]] = None

    # pnovikov: this is how we call user in chat. His preferable name
    @property
    def preferred_name(self) -> Optional[str]:
        return self.metadata.get("preferred_name") if self.metadata else None

    # pnovikov: telegram's username. @novikovpa
    @property
    def tg_username(self) -> Optional[str]:
        return self.metadata.get("tg_username") if self.metadata else None

    # pnovikov: if user provides his first_name in telegram bio
    @property
    def tg_first_name(self) -> Optional[str]:
        return self.metadata.get("tg_first_name") if self.metadata else None

    # pnovikov: if user provides his last_name in telegram bio
    @property
    def tg_last_name(self) -> Optional[str]:
        return self.metadata.get("tg_last_name") if self.metadata else None

    @property
    def gender(self) -> Optional[str]:
        """Get user's gender from metadata."""
        return self.metadata.get("gender") if self.metadata else None

    @property
    def birth_date(self) -> Optional[date]:
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
        return self.metadata.get("marital_status") if self.metadata else None

    @property
    def eye_color(self) -> Optional[str]:
        return self.metadata.get("eye_color") if self.metadata else None

    @property
    def notification_time(self) -> Optional[str]:
        return self.metadata.get("notification_time") if self.metadata else None

    @property
    def timezone(self) -> Optional[str]:
        return self.metadata.get("timezone") if self.metadata else None

    @property
    def user_info_sequence_passed(self) -> Optional[str]:
        return self.metadata.get("user_info_sequence_passed") if self.metadata else None
