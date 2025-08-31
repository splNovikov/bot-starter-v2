"""
Integration tests for the refactored architecture.

Tests the interaction between different components and services
to ensure they work together correctly.
"""

from pathlib import Path

# Add project root to path
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from application.services.user_service import UserService
from core.di.container import DIContainer
from core.protocols.base import ApiResponse
from core.protocols.services import HttpClientProtocol, UserServiceProtocol
from infrastructure.api.client import HttpClient


class TestDIIntegration:
    """Integration tests for DI container with real services."""

    @pytest.fixture
    async def integration_container(self):
        """Create a DI container with real services for integration testing."""
        container = DIContainer()

        # Register real services
        container.register_singleton(HttpClientProtocol, HttpClient)
        container.register_singleton(UserServiceProtocol, UserService)

        yield container

        # Cleanup
        await container.dispose()

    def test_di_resolves_real_services(self, integration_container):
        """Test that DI container resolves real services correctly."""
        # Resolve services
        http_client = integration_container.resolve(HttpClientProtocol)
        user_service = integration_container.resolve(UserServiceProtocol)

        # Verify types
        assert isinstance(http_client, HttpClient)
        assert isinstance(user_service, UserService)

        # Verify dependency injection worked
        assert hasattr(user_service, "_http_client")
        assert user_service._http_client is http_client

    def test_di_singleton_behavior(self, integration_container):
        """Test that singletons return the same instance."""
        # Resolve same service twice
        service1 = integration_container.resolve(UserServiceProtocol)
        service2 = integration_container.resolve(UserServiceProtocol)

        # Should be the same instance
        assert service1 is service2

    @pytest.mark.asyncio
    async def test_di_dispose_cleanup(self):
        """Test that DI container properly disposes services."""
        container = DIContainer()

        # Register services
        container.register_singleton(HttpClientProtocol, HttpClient)

        # Resolve to create instance
        http_client = container.resolve(HttpClientProtocol)

        # Verify it's not closed yet
        assert http_client._session is None  # Not initialized yet

        # Initialize session by making it active
        await http_client._get_session()
        assert http_client._session is not None
        assert not http_client._session.closed

        # Dispose container
        await container.dispose()

        # Session should be closed
        assert http_client._session.closed


class TestUserServiceIntegration:
    """Integration tests for UserService with mocked HTTP responses."""

    @pytest.fixture
    def mock_http_response_success(self):
        """Mock successful HTTP response."""
        return ApiResponse(
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

    @pytest.fixture
    def mock_http_client_with_response(self, mock_http_response_success):
        """Create mock HTTP client that returns success response."""
        mock_client = AsyncMock(spec=HttpClientProtocol)
        mock_client.get.return_value = mock_http_response_success
        mock_client.post.return_value = mock_http_response_success
        mock_client.patch.return_value = mock_http_response_success
        return mock_client

    @pytest.fixture
    def integration_user_service(self, mock_http_client_with_response):
        """Create UserService with mocked HTTP client for integration testing."""
        return UserService(mock_http_client_with_response)

    @pytest.fixture
    def test_user(self):
        """Create test user."""
        user = MagicMock()
        user.id = 12345
        user.first_name = "John"
        user.last_name = "Doe"
        user.username = "johndoe"
        return user

    @pytest.mark.asyncio
    async def test_user_service_full_workflow(
        self, integration_user_service, test_user, mock_http_client_with_response
    ):
        """Test complete user service workflow."""
        # Test getting user (success scenario)
        user_data = await integration_user_service.get_user(test_user)

        assert user_data is not None
        assert user_data.platform_id == "12345"
        assert user_data.tg_first_name == "John"

        # Verify HTTP call was made
        mock_http_client_with_response.get.assert_called_once()
        call_args = mock_http_client_with_response.get.call_args[0]
        assert "users/platform" in call_args[0]
        assert "platformId=12345" in call_args[0]

    @pytest.mark.asyncio
    async def test_user_creation_workflow(
        self, integration_user_service, test_user, mock_http_client_with_response
    ):
        """Test user creation workflow."""
        # Test creating user
        user_data = await integration_user_service.create_user(test_user)

        assert user_data is not None
        assert user_data.platform_id == "12345"

        # Verify HTTP POST was made with correct payload
        mock_http_client_with_response.post.assert_called_once()
        call_args = mock_http_client_with_response.post.call_args

        assert call_args[0][0] == "users"  # endpoint
        payload = call_args[1]["json"]
        assert payload["platformId"] == "12345"
        assert payload["platformType"] == "telegram"
        assert payload["metadata"]["tg_first_name"] == "John"

    @pytest.mark.asyncio
    async def test_user_update_workflow(
        self, integration_user_service, test_user, mock_http_client_with_response
    ):
        """Test user update workflow."""
        updates = {"preferred_name": "Johnny", "age": 25}

        # Test updating user
        user_data = await integration_user_service.update_user(test_user, updates)

        assert user_data is not None

        # Verify HTTP PATCH was made with correct payload
        mock_http_client_with_response.patch.assert_called_once()
        call_args = mock_http_client_with_response.patch.call_args

        endpoint = call_args[0][0]
        assert "users/platform" in endpoint
        assert "platformId=12345" in endpoint

        payload = call_args[1]["json"]
        assert payload["metadata"] == updates


class TestArchitecturalPrinciples:
    """Tests to verify architectural principles are maintained."""

    def test_dependency_inversion_principle(self):
        """Test that services depend on abstractions, not concretions."""
        # UserService should depend on HttpClientProtocol, not HttpClient directly
        import inspect

        from application.services.user_service import UserService

        # Get constructor signature
        sig = inspect.signature(UserService.__init__)

        # Check that http_client parameter is typed as protocol
        http_client_param = sig.parameters.get("http_client")
        assert http_client_param is not None

        # The annotation should be HttpClientProtocol
        from core.protocols.services import HttpClientProtocol

        assert http_client_param.annotation == HttpClientProtocol

    def test_single_responsibility_principle(self):
        """Test that services have single, well-defined responsibilities."""
        from core.sequence.services.completion_service import SequenceCompletionService
        from core.sequence.services.progress_service import SequenceProgressService
        from core.sequence.services.question_service import SequenceQuestionService
        from core.sequence.services.session_service import SequenceSessionService

        # Each service should have focused, non-overlapping responsibilities
        session_methods = [
            m for m in dir(SequenceSessionService) if not m.startswith("_")
        ]
        question_methods = [
            m for m in dir(SequenceQuestionService) if not m.startswith("_")
        ]
        progress_methods = [
            m for m in dir(SequenceProgressService) if not m.startswith("_")
        ]
        completion_methods = [
            m for m in dir(SequenceCompletionService) if not m.startswith("_")
        ]

        # Session service should have session-related methods
        assert any("session" in method.lower() for method in session_methods)

        # Question service should have question-related methods
        assert any("question" in method.lower() for method in question_methods)

        # Progress service should have progress-related methods
        assert any(
            "progress" in method.lower() or "complete" in method.lower()
            for method in progress_methods
        )

        # Completion service should have completion-related methods
        assert any("completion" in method.lower() for method in completion_methods)

    def test_interface_segregation_principle(self):
        """Test that interfaces are focused and not too broad."""
        from core.protocols.services import (
            HttpClientProtocol,
            UserServiceProtocol,
        )

        # Each protocol should have a focused set of methods
        user_methods = [m for m in dir(UserServiceProtocol) if not m.startswith("_")]
        http_methods = [m for m in dir(HttpClientProtocol) if not m.startswith("_")]

        # UserServiceProtocol should only have user-related methods
        user_method_names = [
            m
            for m in user_methods
            if hasattr(getattr(UserServiceProtocol, m, None), "__call__")
        ]
        assert all(
            any(keyword in m.lower() for keyword in ["user", "get", "create", "update"])
            for m in user_method_names
            if not m.startswith("__")
        )

        # HttpClientProtocol should only have HTTP-related methods
        http_method_names = [
            m
            for m in http_methods
            if hasattr(getattr(HttpClientProtocol, m, None), "__call__")
        ]
        assert all(
            any(
                keyword in m.lower()
                for keyword in [
                    "request",
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "close",
                ]
            )
            for m in http_method_names
            if not m.startswith("__")
        )

    def test_services_implement_injectable_protocol(self):
        """Test that all services implement Injectable protocol."""
        from application.services.user_service import UserService
        from core.di.protocols import Injectable
        from core.sequence.services.session_service import SequenceSessionService
        from infrastructure.api.client import HttpClient

        # All services should implement Injectable
        assert issubclass(UserService, Injectable)
        assert issubclass(HttpClient, Injectable)
        assert issubclass(SequenceSessionService, Injectable)
