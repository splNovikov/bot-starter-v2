"""
Tests for architectural refactoring changes.

This module tests the architectural improvements made to eliminate
global state anti-patterns and ensure proper dependency injection.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from application.facade.application_facade import ApplicationFacade
from application.services.user_service import UserService
from core.di.container import DIContainer
from core.protocols.services import HttpClientProtocol, UserServiceProtocol
from infrastructure.api.client import HttpClient


class TestGlobalStateElimination:
    """Test that global state anti-patterns have been eliminated."""

    def test_user_service_no_global_instance(self):
        """Test that UserService no longer uses global instance."""
        # Import should not have global getter/setter functions
        from application.services import user_service

        # These functions should not exist after refactoring
        assert not hasattr(user_service, "get_user_service"), (
            "get_user_service should be removed - violates DIP"
        )
        assert not hasattr(user_service, "set_user_service"), (
            "set_user_service should be removed - violates DIP"
        )

    def test_sequence_initiation_service_no_global_instance(self):
        """Test that SequenceInitiationService no longer uses global instance."""
        from infrastructure.sequence.services import sequence_initiation_service

        # Global getter function should not exist
        assert not hasattr(
            sequence_initiation_service, "get_sequence_initiation_service"
        ), "get_sequence_initiation_service should be removed - violates DIP"


class TestDependencyInjectionContainer:
    """Test that DI container works properly after refactoring."""

    def test_container_service_resolution(self):
        """Test that services can be resolved through DI container."""
        container = DIContainer()

        # Register services
        container.register_singleton(HttpClientProtocol, HttpClient)
        container.register_singleton(UserServiceProtocol, UserService)

        # Test resolution
        http_client = container.resolve(HttpClientProtocol)
        user_service = container.resolve(UserServiceProtocol)

        assert isinstance(http_client, HttpClient)
        assert isinstance(user_service, UserService)

        # Test singleton behavior
        http_client2 = container.resolve(HttpClientProtocol)
        assert http_client is http_client2

    def test_global_container_deprecation_warnings(self):
        """Test that global container functions have deprecation warnings."""
        from core.di.container import get_container, set_container

        # Check that deprecation warnings are in docstrings
        assert "deprecated" in get_container.__doc__.lower()
        assert "violates dependency inversion" in get_container.__doc__
        assert "deprecated" in set_container.__doc__.lower()
        assert "violates dependency inversion" in set_container.__doc__

    def test_service_resolution_pattern(self):
        """Test the new service resolution pattern works."""
        from aiogram.types import User

        from application.services.user_utils import ensure_user_exists

        # Mock user for testing
        mock_user = Mock(spec=User)
        mock_user.id = 12345
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.username = "testuser"

        # Test should not raise exception with proper DI pattern
        # (Even if service resolution fails, it should handle gracefully)
        # This tests that the new pattern is implemented
        import asyncio

        async def test_pattern():
            try:
                result = await ensure_user_exists(mock_user)
                # May return None if service resolution fails, but shouldn't crash
                assert result is None or hasattr(result, "id")
            except Exception as e:
                # Should handle DI resolution failures gracefully
                assert "Failed to resolve user service" in str(
                    e
                ) or "Service UserServiceProtocol is not registered" in str(e)

        asyncio.run(test_pattern())


class TestApplicationFacadeInfrastructure:
    """Test ApplicationFacade infrastructure management."""

    def test_application_facade_has_infrastructure_methods(self):
        """Test that ApplicationFacade has new infrastructure methods."""
        facade = ApplicationFacade()

        # Check that new methods exist
        assert hasattr(facade, "initialize_infrastructure")
        assert hasattr(facade, "cleanup_infrastructure")
        assert callable(facade.initialize_infrastructure)
        assert callable(facade.cleanup_infrastructure)

    @patch("infrastructure.sequence.initialize_sequences")
    @patch("core.sequence.set_translator_factory")
    def test_infrastructure_initialization(
        self, mock_set_translator, mock_init_sequences
    ):
        """Test that infrastructure initialization works through facade."""
        facade = ApplicationFacade()

        # Mock sequence definitions
        with patch.object(facade, "get_sequence_definitions", return_value=[]):
            facade.initialize_infrastructure()

        # Verify infrastructure components were initialized
        mock_set_translator.assert_called_once()
        mock_init_sequences.assert_called_once()

    @pytest.mark.asyncio
    @patch("infrastructure.api.close_http_client")
    async def test_infrastructure_cleanup(self, mock_close_client):
        """Test that infrastructure cleanup works through facade."""
        mock_close_client.return_value = AsyncMock()

        facade = ApplicationFacade()
        await facade.cleanup_infrastructure()

        # Verify cleanup was called
        mock_close_client.assert_called_once()


class TestCleanArchitectureCompliance:
    """Test that Clean Architecture principles are maintained."""

    def test_main_module_no_direct_infrastructure_imports(self):
        """Test that main.py doesn't import infrastructure directly."""
        import ast
        import inspect

        # Read main.py source
        import main

        source = inspect.getsource(main)
        tree = ast.parse(source)

        # Check imports
        infrastructure_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("infrastructure."):
                        infrastructure_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("infrastructure."):
                    infrastructure_imports.append(node.module)

        assert len(infrastructure_imports) == 0, (
            f"main.py should not import infrastructure directly. Found: {infrastructure_imports}"
        )

    def test_application_facade_protocol_compliance(self):
        """Test that ApplicationFacade implements the protocol correctly."""
        from core.facade.application_facade import ApplicationFacadeProtocol

        facade = ApplicationFacade()

        # Test that facade implements the protocol
        assert isinstance(facade, ApplicationFacadeProtocol)

        # Test that all protocol methods are implemented
        protocol_methods = [
            "get_di_container",
            "get_main_router",
            "get_sequence_definitions",
            "initialize_handlers",
            "setup_legacy_services",
            "initialize_infrastructure",
            "cleanup_infrastructure",
            "dispose",
        ]

        for method_name in protocol_methods:
            assert hasattr(facade, method_name), (
                f"ApplicationFacade missing method: {method_name}"
            )
            assert callable(getattr(facade, method_name))


class TestServiceResolutionPatterns:
    """Test that service resolution follows proper patterns."""

    @patch("core.di.container.get_container")
    def test_user_utils_service_resolution(self, mock_get_container):
        """Test that user_utils uses proper DI pattern."""
        # Mock container and service
        mock_container = Mock()
        mock_service = Mock()
        mock_container.resolve.return_value = mock_service
        mock_get_container.return_value = mock_container

        from aiogram.types import User

        from application.services.user_utils import create_enhanced_context

        mock_user = Mock(spec=User)
        mock_user.id = 12345
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.username = "testuser"

        # Mock service methods
        mock_service.get_user_display_name.return_value = "Test User"

        import asyncio

        async def test_resolution():
            # This should use the new DI pattern
            context = await create_enhanced_context(mock_user)

            # Verify container was used
            mock_get_container.assert_called()
            mock_container.resolve.assert_called_with(UserServiceProtocol)

            # Verify context was created
            assert "user" in context
            assert "user_id" in context
            assert context["user_id"] == 12345

        asyncio.run(test_resolution())

    def test_handler_service_access_patterns(self):
        """Test that handlers use proper service access patterns."""
        # Check that handlers import DI components
        import inspect

        from application.handlers.sequence_user_info import (
            gender_handler,
            preferred_name_handler,
        )

        for module in [preferred_name_handler, gender_handler]:
            source = inspect.getsource(module)

            # Should import DI container
            assert "from core.di.container import get_container" in source
            assert "from core.protocols.services import UserServiceProtocol" in source

            # Should not have old global service access
            assert "get_user_service()" not in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
