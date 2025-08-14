from typing import Any

from aiogram.types import User

from application.types import UserData
from core.protocols.base import ApiResponse
from core.utils.logger import get_logger
from infrastructure.api.client import HttpClient

logger = get_logger()


class UserService:
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client

    def get_user_name_parts(self, user: User) -> tuple[str, str]:
        """
        Extract user's first and last name from Telegram data.

        Args:
            user: Telegram User object

        Returns:
            Tuple of (first_name, last_name) where last_name defaults to empty string
        """
        return user.first_name, user.last_name or ""

    def get_user_display_name(self, user: User) -> str:
        """
        Get user's display name (first_name + last_name or username).

        Args:
            user: Telegram User object

        Returns:
            Display name string
        """
        first_name, last_name = self.get_user_name_parts(user)
        if first_name and last_name:
            return f"{first_name} {last_name}"
        elif first_name:
            return first_name
        elif user.username:
            return f"@{user.username}"
        else:
            return "Anonymous"

    async def get_user(self, user: User) -> UserData | None:
        user_id = user.id

        try:
            # Fetch from API using application-specific endpoint
            logger.info(f"Fetching user {user_id} from API")
            response = await self._fetch_user_from_api(user_id)

            if response.success and response.data:
                # Parse user data from API response
                user_data = self._parse_user_data(response.data, user)

                logger.info(f"Successfully fetched user {user_id} from API")
                return user_data
            else:
                logger.info(f"User {user_id} not found in API")
                return None

        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None

    async def create_user(self, user: User) -> UserData | None:
        user_id = user.id

        try:
            logger.info(f"Creating new user {user_id} in API")

            payload = {
                "platformId": str(user_id),
                "platformType": "telegram",
                "metadata": {
                    "tg_first_name": user.first_name or "",
                    "tg_username": user.username or "",
                    "tg_last_name": user.last_name or "",
                },
            }

            response = await self._http_client.post("users", json=payload)

            if response.success and response.data:
                # Parse user data from API response
                user_data = self._parse_user_data(response.data, user)

                logger.info(f"Successfully created user {user_id} in API")
                return user_data
            else:
                logger.error(f"Failed to create user {user_id}: {response.error}")
                return None

        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return None

    async def update_user(
        self, user: User, metadata_updates: dict[str, Any]
    ) -> UserData | None:
        """
        Update user metadata in the API.

        Args:
            user: Telegram User object
            metadata_updates: Dictionary of metadata fields to update

        Returns:
            Updated UserData object or None if update failed
        """
        user_id = user.id

        try:
            logger.info(f"Updating user {user_id} metadata in API")

            # Prepare payload according to UpdateUserDto structure
            payload = {
                "metadata": metadata_updates,
            }

            response = await self._update_user_in_api(user_id, payload)

            if response.success and response.data:
                # Parse updated user data from API response
                updated_user_data = self._parse_user_data(response.data, user)

                logger.info(f"Successfully updated user {user_id} metadata in API")
                return updated_user_data
            else:
                logger.error(f"Failed to update user {user_id}: {response.error}")
                return None

        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None

    async def _fetch_user_from_api(self, user_id: int) -> ApiResponse:
        endpoint = f"users/platform?platformId={user_id}&platformType=telegram"
        return await self._http_client.get(endpoint)

    async def _update_user_in_api(
        self, user_id: int, payload: dict[str, Any]
    ) -> ApiResponse:
        endpoint = f"users/platform?platformId={user_id}&platformType=telegram"
        return await self._http_client.patch(endpoint, json=payload)

    def _parse_user_data(self, api_data: dict[str, Any], user: User) -> UserData:
        # Extract basic fields from API response
        user_id = api_data.get("id")
        platform_id = api_data.get("platformId", str(user.id))
        platform_type = api_data.get("platformType", "telegram")
        is_active = api_data.get("is_active")
        metadata = api_data.get("metadata", {})

        # If metadata is None, create default metadata from Telegram user
        if metadata is None:
            metadata = {
                "tg_first_name": user.first_name or "",
                "tg_username": user.username or "",
                "tg_last_name": user.last_name or "",
            }

        return UserData(
            id=user_id,
            platform_id=platform_id,
            platform_type=platform_type,
            is_active=is_active,
            metadata=metadata,
        )


# Global user service instance
_user_service: UserService | None = None


def get_user_service() -> UserService | None:
    """Get global user service instance."""
    return _user_service


def set_user_service(service: UserService):
    """Set global user service instance."""
    global _user_service
    _user_service = service
