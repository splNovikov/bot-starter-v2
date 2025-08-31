"""
Service protocols for application layer.

Defines the contracts for application services that handle business logic
and external integrations.
"""

from typing import Any, Dict, Optional, Protocol, Tuple

from aiogram.types import User

from core.protocols.base import ApiResponse
from core.protocols.entities import UserEntity


class UserServiceProtocol(Protocol):
    """
    Protocol for user management service.

    Defines the contract for user-related operations including
    creation, retrieval, and updates.
    """

    def get_user_name_parts(self, user: User) -> Tuple[str, str]:
        """
        Extract user's first and last name from Telegram data.

        Args:
            user: Telegram User object

        Returns:
            Tuple of (first_name, last_name) where last_name defaults to empty string
        """
        ...

    def get_user_display_name(self, user: User) -> str:
        """
        Get user's display name (first_name + last_name or username).

        Args:
            user: Telegram User object

        Returns:
            Display name string
        """
        ...

    async def get_user(self, user: User) -> Optional[UserEntity]:
        """
        Retrieve user from external service.

        Args:
            user: Telegram User object

        Returns:
            UserEntity object or None if not found
        """
        ...

    async def create_user(self, user: User) -> Optional[UserEntity]:
        """
        Create new user in external service.

        Args:
            user: Telegram User object

        Returns:
            Created UserEntity object or None if creation failed
        """
        ...

    async def update_user(
        self, user: User, metadata_updates: Dict[str, Any]
    ) -> Optional[UserEntity]:
        """
        Update user metadata in external service.

        Args:
            user: Telegram User object
            metadata_updates: Dictionary of metadata fields to update

        Returns:
            Updated UserEntity object or None if update failed
        """
        ...


class HttpClientProtocol(Protocol):
    """
    Protocol for HTTP client service.

    Defines the contract for making HTTP requests to external APIs
    with proper error handling and response management.
    """

    async def request(self, method: str, endpoint: str, **kwargs) -> ApiResponse:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for HTTP request

        Returns:
            ApiResponse with success status and data/error
        """
        ...

    async def get(self, endpoint: str, **kwargs) -> ApiResponse:
        """
        Make GET request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments for HTTP request

        Returns:
            ApiResponse with success status and data/error
        """
        ...

    async def post(self, endpoint: str, **kwargs) -> ApiResponse:
        """
        Make POST request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments for HTTP request

        Returns:
            ApiResponse with success status and data/error
        """
        ...

    async def put(self, endpoint: str, **kwargs) -> ApiResponse:
        """
        Make PUT request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments for HTTP request

        Returns:
            ApiResponse with success status and data/error
        """
        ...

    async def patch(self, endpoint: str, **kwargs) -> ApiResponse:
        """
        Make PATCH request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments for HTTP request

        Returns:
            ApiResponse with success status and data/error
        """
        ...

    async def delete(self, endpoint: str, **kwargs) -> ApiResponse:
        """
        Make DELETE request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments for HTTP request

        Returns:
            ApiResponse with success status and data/error
        """
        ...

    async def close(self) -> None:
        """
        Close the HTTP client and clean up resources.
        """
        ...
