"""
Tests for UserService functionality.

Comprehensive test coverage for user service operations including
user retrieval, creation, updates, and error handling.
"""

from unittest.mock import AsyncMock

import pytest

from application.services.user_service import UserService
from application.types.user import UserData
from core.protocols.base import ApiResponse


class TestUserService:
    """Test cases for UserService."""

    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client."""
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_http_client):
        """Create UserService with mock HTTP client."""
        return UserService(mock_http_client)

    def test_get_user_name_parts(self, user_service, mock_user):
        """Test extracting user name parts."""
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"

        first_name, last_name = user_service.get_user_name_parts(mock_user)

        assert first_name == "John"
        assert last_name == "Doe"

    def test_get_user_name_parts_no_last_name(self, user_service, mock_user):
        """Test extracting user name parts with no last name."""
        mock_user.first_name = "John"
        mock_user.last_name = None

        first_name, last_name = user_service.get_user_name_parts(mock_user)

        assert first_name == "John"
        assert last_name == ""

    def test_get_user_display_name_full_name(self, user_service, mock_user):
        """Test getting display name with full name."""
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        mock_user.username = "johndoe"

        display_name = user_service.get_user_display_name(mock_user)

        assert display_name == "John Doe"

    def test_get_user_display_name_first_only(self, user_service, mock_user):
        """Test getting display name with first name only."""
        mock_user.first_name = "John"
        mock_user.last_name = None
        mock_user.username = "johndoe"

        display_name = user_service.get_user_display_name(mock_user)

        assert display_name == "John"

    def test_get_user_display_name_username_only(self, user_service, mock_user):
        """Test getting display name with username only."""
        mock_user.first_name = None
        mock_user.last_name = None
        mock_user.username = "johndoe"

        display_name = user_service.get_user_display_name(mock_user)

        assert display_name == "@johndoe"

    def test_get_user_display_name_anonymous(self, user_service, mock_user):
        """Test getting display name with no info."""
        mock_user.first_name = None
        mock_user.last_name = None
        mock_user.username = None

        display_name = user_service.get_user_display_name(mock_user)

        assert display_name == "Anonymous"

    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service, mock_user):
        """Test successful user retrieval."""
        # Setup mock response
        mock_response = ApiResponse(
            success=True,
            data={
                "id": 1,
                "platformId": "12345",
                "platformType": "telegram",
                "is_active": True,
                "metadata": {
                    "tg_first_name": "John",
                    "tg_last_name": "Doe",
                    "tg_username": "johndoe",
                },
            },
        )
        user_service._fetch_user_from_api = AsyncMock(return_value=mock_response)

        # Test
        result = await user_service.get_user(mock_user)

        # Assertions
        assert result is not None
        assert isinstance(result, UserData)
        assert result.id == 1
        assert result.platform_id == "12345"
        assert result.platform_type == "telegram"
        assert result.tg_first_name == "John"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service, mock_user):
        """Test user not found scenario."""
        # Setup mock response
        mock_response = ApiResponse(success=False, data=None)
        user_service._fetch_user_from_api = AsyncMock(return_value=mock_response)

        # Test
        result = await user_service.get_user(mock_user)

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_api_error(self, user_service, mock_user):
        """Test API error handling."""
        # Setup mock to raise exception
        user_service._fetch_user_from_api = AsyncMock(
            side_effect=Exception("API Error")
        )

        # Test
        result = await user_service.get_user(mock_user)

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_user):
        """Test successful user creation."""
        mock_user.id = 12345
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        mock_user.username = "johndoe"

        # Setup mock response
        mock_response = ApiResponse(
            success=True,
            data={
                "id": 1,
                "platformId": "12345",
                "platformType": "telegram",
                "is_active": True,
                "metadata": {
                    "tg_first_name": "John",
                    "tg_last_name": "Doe",
                    "tg_username": "johndoe",
                },
            },
        )
        user_service._http_client.post = AsyncMock(return_value=mock_response)

        # Test
        result = await user_service.create_user(mock_user)

        # Assertions
        assert result is not None
        assert isinstance(result, UserData)
        assert result.id == 1
        assert result.platform_id == "12345"

        # Verify API call
        user_service._http_client.post.assert_called_once()
        call_args = user_service._http_client.post.call_args
        assert call_args[0][0] == "users"  # endpoint

        payload = call_args[1]["json"]
        assert payload["platformId"] == "12345"
        assert payload["platformType"] == "telegram"
        assert payload["metadata"]["tg_first_name"] == "John"

    @pytest.mark.asyncio
    async def test_create_user_failure(self, user_service, mock_user):
        """Test user creation failure."""
        # Setup mock response
        mock_response = ApiResponse(success=False, error="Creation failed")
        user_service._http_client.post = AsyncMock(return_value=mock_response)

        # Test
        result = await user_service.create_user(mock_user)

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service, mock_user):
        """Test successful user update."""
        mock_user.id = 12345
        updates = {"preferred_name": "Johnny"}

        # Setup mock response
        mock_response = ApiResponse(
            success=True,
            data={
                "id": 1,
                "platformId": "12345",
                "platformType": "telegram",
                "is_active": True,
                "metadata": {"tg_first_name": "John", "preferred_name": "Johnny"},
            },
        )
        user_service._update_user_in_api = AsyncMock(return_value=mock_response)

        # Test
        result = await user_service.update_user(mock_user, updates)

        # Assertions
        assert result is not None
        assert isinstance(result, UserData)
        assert result.preferred_name == "Johnny"

        # Verify API call
        user_service._update_user_in_api.assert_called_once_with(
            12345, {"metadata": updates}
        )

    @pytest.mark.asyncio
    async def test_update_user_failure(self, user_service, mock_user):
        """Test user update failure."""
        updates = {"preferred_name": "Johnny"}

        # Setup mock response
        mock_response = ApiResponse(success=False, error="Update failed")
        user_service._update_user_in_api = AsyncMock(return_value=mock_response)

        # Test
        result = await user_service.update_user(mock_user, updates)

        # Assertions
        assert result is None

    def test_parse_user_data(self, user_service, mock_user):
        """Test user data parsing."""
        api_data = {
            "id": 1,
            "platformId": "12345",
            "platformType": "telegram",
            "is_active": True,
            "metadata": {
                "tg_first_name": "John",
                "tg_last_name": "Doe",
                "preferred_name": "Johnny",
            },
        }

        result = user_service._parse_user_data(api_data, mock_user)

        assert isinstance(result, UserData)
        assert result.id == 1
        assert result.platform_id == "12345"
        assert result.tg_first_name == "John"
        assert result.preferred_name == "Johnny"

    def test_parse_user_data_with_none_metadata(self, user_service, mock_user):
        """Test user data parsing with None metadata."""
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        mock_user.username = "johndoe"

        api_data = {
            "id": 1,
            "platformId": "12345",
            "platformType": "telegram",
            "is_active": True,
            "metadata": None,
        }

        result = user_service._parse_user_data(api_data, mock_user)

        assert isinstance(result, UserData)
        assert result.metadata is not None
        assert result.tg_first_name == "John"
        assert result.tg_last_name == "Doe"
        assert result.tg_username == "johndoe"
