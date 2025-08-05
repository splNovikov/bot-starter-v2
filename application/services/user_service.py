"""
User service for managing user-related operations.

Handles user data fetching, caching, and provides business logic
for user-related operations including API integration.
"""

from typing import Any, Dict, Optional

from aiogram.types import User as TelegramUser

from application.types.user import UserData
from core.protocols.base import ApiResponse
from core.utils.logger import get_logger
from infrastructure.api.client import HttpClient

logger = get_logger()


class UserService:
    """
    Service for managing user-related operations.

    Handles user data fetching from external APIs, caching,
    and provides business logic for user operations.
    """

    def __init__(self, http_client: HttpClient):
        """
        Initialize user service.

        Args:
            http_client: Generic HTTP client for external service communication
        """
        self._http_client = http_client
        self._cache: Dict[int, UserData] = {}
        self._cache_ttl = 300  # 5 minutes cache TTL

    async def get_user(self, telegram_user: TelegramUser) -> Optional[UserData]:
        """
        Get user data from API or cache.

        Args:
            telegram_user: Telegram user object

        Returns:
            UserData if user exists, None if not found
        """
        user_id = telegram_user.id

        # Check cache first
        if user_id in self._cache:
            logger.debug(f"User {user_id} found in cache")
            return self._cache[user_id]

        try:
            # Fetch from API using application-specific endpoint
            logger.info(f"Fetching user {user_id} from API")
            response = await self._fetch_user_from_api(user_id)

            if response.success and response.data:
                # Parse user data from API response
                user_data = self._parse_user_data(response.data, telegram_user)

                # Cache the result
                self._cache[user_id] = user_data

                logger.info(f"Successfully fetched user {user_id} from API")
                return user_data
            else:
                logger.info(f"User {user_id} not found in API")
                return None

        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None

    async def _fetch_user_from_api(self, user_id: int) -> ApiResponse:
        """
        Fetch user data from external API using application-specific endpoint.

        Args:
            user_id: Telegram user ID

        Returns:
            ApiResponse with user data or error
        """
        endpoint = f"users/platform?platformId={user_id}&platformType=telegram"
        return await self._http_client.get(endpoint)

    async def submit_questionnaire_answer(
        self, user_id: int, question_key: str, answer: str, session_id: str
    ) -> ApiResponse:
        """
        Submit questionnaire answer to external API.

        Args:
            user_id: Telegram user ID
            question_key: Question identifier
            answer: User's answer
            session_id: Session identifier

        Returns:
            ApiResponse with success status
        """
        payload = {
            "user_id": user_id,
            "question_key": question_key,
            "answer": answer,
            "session_id": session_id,
        }

        return await self._http_client.post("questionnaire/answers", json=payload)

    async def complete_questionnaire(
        self, user_id: int, session_id: str
    ) -> ApiResponse:
        """
        Mark questionnaire as completed in external API.

        Args:
            user_id: Telegram user ID
            session_id: Session identifier

        Returns:
            ApiResponse with success status
        """
        payload = {"user_id": user_id, "session_id": session_id}

        return await self._http_client.post("questionnaire/complete", json=payload)

    def _parse_user_data(
        self, api_data: Dict[str, Any], telegram_user: TelegramUser
    ) -> UserData:
        """
        Parse user data from API response matching backend User structure.

        Args:
            api_data: Raw API response data
            telegram_user: Telegram user object for fallback data

        Returns:
            Parsed UserData object
        """
        # Extract basic fields from API response
        user_id = api_data.get("id")
        platform_id = api_data.get("platformId", str(telegram_user.id))
        platform_type = api_data.get("platformType", "telegram")
        metadata = api_data.get("metadata", {})

        # If metadata is None, create default metadata from Telegram user
        if metadata is None:
            metadata = {
                "first_name": telegram_user.first_name,
                "username": telegram_user.username,
                "last_name": telegram_user.last_name,
                "is_active": True,
            }

        return UserData(
            id=user_id,
            platform_id=platform_id,
            platform_type=platform_type,
            metadata=metadata,
        )

    def clear_cache(self, user_id: Optional[int] = None):
        """
        Clear user cache.

        Args:
            user_id: Specific user ID to clear, or None to clear all
        """
        if user_id:
            self._cache.pop(user_id, None)
            logger.debug(f"Cleared cache for user {user_id}")
        else:
            self._cache.clear()
            logger.debug("Cleared all user cache")

    def get_cached_user(self, user_id: int) -> Optional[UserData]:
        """
        Get user from cache only.

        Args:
            user_id: User ID

        Returns:
            Cached UserData or None
        """
        return self._cache.get(user_id)

    def is_user_cached(self, user_id: int) -> bool:
        """
        Check if user is cached.

        Args:
            user_id: User ID

        Returns:
            True if user is in cache
        """
        return user_id in self._cache


# Global user service instance
_user_service: Optional[UserService] = None


def get_user_service() -> Optional[UserService]:
    """Get global user service instance."""
    return _user_service


def set_user_service(service: UserService):
    """Set global user service instance."""
    global _user_service
    _user_service = service
