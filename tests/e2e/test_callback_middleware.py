"""
Test callback middleware functionality.

Tests that ApplicationFacadeMiddleware correctly injects context for callback queries.
"""

from unittest.mock import AsyncMock, MagicMock

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
import pytest

from application import create_application_facade
from core.middleware.facade_middleware import ApplicationFacadeMiddleware
from core.utils.context_utils import get_app_facade
from core.utils.logger import get_logger

logger = get_logger()


class TestCallbackMiddleware:
    """Test callback middleware functionality."""

    @pytest.fixture
    async def app_facade(self):
        """Create application facade for testing."""
        facade = create_application_facade()
        facade.initialize_infrastructure()
        return facade

    @pytest.fixture
    def mock_user(self):
        """Create mock user for testing."""
        user = MagicMock(spec=User)
        user.id = 12345
        user.username = "test_user"
        user.first_name = "Test"
        user.last_name = "User"
        user.language_code = "en"
        return user

    @pytest.fixture
    def mock_callback(self, mock_user):
        """Create mock callback query for testing."""
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = mock_user
        callback.data = "start_ready:user_info"
        callback.answer = AsyncMock()
        callback.message = MagicMock()
        callback.message.answer = AsyncMock()
        callback.message.edit_reply_markup = AsyncMock()
        return callback

    @pytest.fixture
    def middleware(self, app_facade):
        """Create ApplicationFacadeMiddleware for testing."""
        return ApplicationFacadeMiddleware(app_facade)

    async def test_middleware_injects_app_facade(self, middleware, mock_callback):
        """Test that middleware injects ApplicationFacade into callback context."""

        # Create mock handler that checks for app_facade in data
        async def mock_handler(event, data):
            # Check if app_facade is in data
            assert "app_facade" in data
            assert data["app_facade"] is not None
            return "success"

        # Call middleware with mock handler
        result = await middleware(mock_handler, mock_callback, {})

        # Verify result
        assert result == "success"

    async def test_middleware_preserves_existing_data(self, middleware, mock_callback):
        """Test that middleware preserves existing data in context."""
        # Create existing data
        existing_data = {"existing_key": "existing_value"}

        # Create mock handler that checks data
        async def mock_handler(event, data):
            # Check that existing data is preserved
            assert "existing_key" in data
            assert data["existing_key"] == "existing_value"
            # Check that app_facade is added
            assert "app_facade" in data
            return "success"

        # Call middleware with existing data
        result = await middleware(mock_handler, mock_callback, existing_data)

        # Verify result
        assert result == "success"

    async def test_get_app_facade_from_context(
        self, middleware, mock_callback, app_facade
    ):
        """Test that get_app_facade can retrieve facade from context."""

        # Create mock handler that uses get_app_facade
        async def mock_handler(event, data):
            # Get app_facade from context
            facade = get_app_facade(data)
            assert facade is not None
            assert facade == app_facade
            return "success"

        # Call middleware with mock handler
        result = await middleware(mock_handler, mock_callback, {})

        # Verify result
        assert result == "success"

    async def test_middleware_with_real_callback_handler(
        self, middleware, mock_callback, app_facade
    ):
        """Test middleware with a real callback handler function."""

        # Create a real callback handler that uses context
        async def real_callback_handler(callback: CallbackQuery, **kwargs):
            # Try to get app_facade from context
            try:
                facade = get_app_facade(kwargs)
                if facade is not None:
                    return "success_with_facade"
                else:
                    return "no_facade"
            except Exception as e:
                return f"error: {str(e)}"

        # Call middleware with real handler
        result = await middleware(real_callback_handler, mock_callback, {})

        # Verify result
        assert result == "success_with_facade"

    async def test_middleware_error_handling(self, middleware, mock_callback):
        """Test middleware error handling."""

        # Create mock handler that raises an exception
        async def error_handler(event, data):
            raise ValueError("Test error")

        # Call middleware and expect exception
        with pytest.raises(ValueError, match="Test error"):
            await middleware(error_handler, mock_callback, {})

    async def test_middleware_logging(self, middleware, mock_callback, caplog):
        """Test that middleware logs correctly."""

        # Create mock handler
        async def mock_handler(event, data):
            return "success"

        # Call middleware
        result = await middleware(mock_handler, mock_callback, {})

        # Check that debug log was created
        assert "ApplicationFacade injected into handler context" in caplog.text
        assert result == "success"

    async def test_router_with_middleware(self, app_facade, mock_callback):
        """Test that router with middleware correctly injects context."""
        # Create router
        router = Router()

        # Create middleware
        middleware = ApplicationFacadeMiddleware(app_facade)

        # Register middleware on router
        router.callback_query.middleware(middleware)

        # Create callback handler that checks for app_facade
        context_received = None

        @router.callback_query(F.data.startswith("start_ready:"))
        async def test_callback_handler(callback: CallbackQuery, **kwargs):
            nonlocal context_received
            try:
                facade = get_app_facade(kwargs)
                context_received = "success" if facade is not None else "no_facade"
            except Exception as e:
                context_received = f"error: {str(e)}"

        # Simulate callback query
        # Note: This is a simplified test - in real aiogram, this would be handled by dispatcher
        # We're testing the middleware directly
        async def simulate_callback():
            # Create data dict that would be passed by aiogram
            data = {}

            # Create a wrapper that calls our handler correctly
            async def wrapper(event, data):
                return await test_callback_handler(event, **data)

            # Call middleware with our wrapper
            await middleware(wrapper, mock_callback, data)

            # Check if context was received
            return context_received

        result = await simulate_callback()
        assert result == "success"
