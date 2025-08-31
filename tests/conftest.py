"""
Pytest configuration and fixtures for bot-starter-v2 tests.

Provides common fixtures and test configuration for all test modules.
"""

from pathlib import Path

# Add project root to path
import sys
from unittest.mock import AsyncMock, MagicMock

from aiogram.types import User
import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from application.services.user_service import UserService
from core.di.container import DIContainer
from core.protocols.services import HttpClientProtocol, UserServiceProtocol
from infrastructure.api.client import HttpClient


@pytest.fixture
def mock_user():
    """Create a mock Telegram user for testing."""
    user = MagicMock(spec=User)
    user.id = 12345
    user.first_name = "Test"
    user.last_name = "User"
    user.username = "testuser"
    return user


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing."""
    client = AsyncMock(spec=HttpClientProtocol)
    return client


@pytest.fixture
def di_container():
    """Create a fresh DI container for each test."""
    container = DIContainer()

    # Register basic services
    container.register_singleton(HttpClientProtocol, HttpClient)
    container.register_singleton(UserServiceProtocol, UserService)

    return container


@pytest.fixture
def mock_di_container(mock_http_client):
    """Create a DI container with mock services for testing."""
    container = DIContainer()

    # Register mock services
    container.register_instance(HttpClientProtocol, mock_http_client)

    # User service will get the mock HTTP client injected
    container.register_singleton(UserServiceProtocol, UserService)

    return container


@pytest.fixture
async def clean_container():
    """Create a container and clean it up after the test."""
    container = DIContainer()
    yield container

    # Cleanup
    try:
        await container.dispose()
    except Exception:
        pass  # Ignore cleanup errors in tests
