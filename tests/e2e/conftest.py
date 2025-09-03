"""
Pytest configuration for e2e tests.

Provides fixtures and configuration for end-to-end testing
of the bot application.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from application import create_application_facade
from core.sequence.protocols import SequenceServiceProtocol


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def app_facade():
    """Create application facade for testing."""
    return create_application_facade()


@pytest.fixture
async def sequence_service(app_facade):
    """Get sequence service from DI container."""
    container = app_facade.get_di_container()
    return container.resolve(SequenceServiceProtocol)


@pytest.fixture
def mock_user_id():
    """Mock user ID for testing."""
    return 12345


@pytest.fixture
def mock_telegram_user():
    """Create mock Telegram user."""
    user = MagicMock()
    user.id = 12345
    user.username = "test_user"
    user.first_name = "Test"
    user.last_name = "User"
    return user


@pytest.fixture
def mock_chat():
    """Create mock Telegram chat."""
    chat = MagicMock()
    chat.id = 12345
    chat.type = "private"
    return chat


@pytest.fixture
def mock_bot():
    """Create mock Telegram bot."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    bot.answer_callback_query = AsyncMock()
    bot.edit_message_text = AsyncMock()
    return bot


@pytest.fixture
def mock_state():
    """Create mock FSM state."""
    state = MagicMock()
    state.get_state = AsyncMock(return_value=None)
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    return state
