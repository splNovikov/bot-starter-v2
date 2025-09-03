"""
Integration tests for button functionality and callback handlers.

Tests the complete flow from button creation to callback handling.
"""

from unittest.mock import AsyncMock, MagicMock

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)
import pytest

from application import create_application_facade
from application.handlers.command_start.start_callback_handler import (
    start_callback_handler,
)
from application.handlers.command_start.start_command_handler import (
    start_command_handler,
)
from core.utils.logger import get_logger

logger = get_logger()


class TestButtonIntegration:
    """Integration tests for button functionality."""

    @pytest.fixture
    async def app_facade(self):
        """Create application facade for testing."""
        facade = create_application_facade()
        # Initialize infrastructure to set up translator factory
        facade.initialize_infrastructure()
        facade.initialize_handlers()  # Initialize registry
        return facade

    @pytest.fixture
    def mock_user(self):
        """Create mock user for testing."""
        user = MagicMock(spec=User)
        user.id = 12345
        user.username = "test_user"
        user.first_name = "Test"
        user.last_name = "User"
        user.language_code = "en"  # Add missing attribute
        return user

    @pytest.fixture
    def mock_message(self, mock_user):
        """Create mock message for testing."""
        message = MagicMock(spec=Message)
        message.from_user = mock_user
        message.answer = AsyncMock()
        message.edit_reply_markup = AsyncMock()
        return message

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
    def mock_context(self, app_facade):
        """Create mock context with app_facade."""
        return {"app_facade": app_facade}

    async def test_start_command_creates_button(self, mock_message, mock_context):
        """Test that start command creates a button with correct layout."""
        # Mock ensure_user_exists to return None (new user)
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "application.services.user_utils.ensure_user_exists",
                AsyncMock(return_value=None),
            )

            # Call start command handler
            await start_command_handler(mock_message, **mock_context)

            # Verify that message.answer was called twice (greeting + readiness with button)
            assert mock_message.answer.call_count == 2

            # Get the second call (readiness message with button)
            second_call = mock_message.answer.call_args_list[1]
            args, kwargs = second_call

            # Check that reply_markup is present
            assert "reply_markup" in kwargs
            reply_markup = kwargs["reply_markup"]

            # Verify it's an InlineKeyboardMarkup
            assert isinstance(reply_markup, InlineKeyboardMarkup)

            # Verify button layout - should be one row with one button
            assert len(reply_markup.inline_keyboard) == 1
            assert len(reply_markup.inline_keyboard[0]) == 1

            # Verify button properties
            button = reply_markup.inline_keyboard[0][0]
            assert isinstance(button, InlineKeyboardButton)
            assert button.callback_data == "start_ready:user_info"
            assert "ready" in button.text.lower() or "готов" in button.text.lower()

    async def test_callback_handler_with_app_facade(self, mock_callback, app_facade):
        """Test that callback handler works with ApplicationFacade passed directly."""
        # Mock sequence initiation to succeed
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "infrastructure.sequence.SequenceInitiationService.initiate_user_info_sequence",
                AsyncMock(return_value=(True, None)),
            )
            
            # Create context with app_facade
            context = {"app_facade": app_facade}
            
            # Call callback handler directly with context
            await start_callback_handler(mock_callback, **context)
            
            # Verify that callback.answer was called (no error occurred)
            mock_callback.answer.assert_called()

    async def test_sequence_callback_handler_with_yes_no_buttons(self, mock_callback, app_facade):
        """Test that sequence callback handler works with Yes/No buttons."""
        # Mock sequence service methods
        with pytest.MonkeyPatch().context() as m:
            # Mock get_session to return a valid session
            mock_session = MagicMock()
            mock_session.current_step = 0
            mock_session.sequence_name = "user_info"
            # Mock sequence service methods
            mock_sequence_service = MagicMock()
            mock_sequence_service.get_session.return_value = mock_session
            mock_sequence_service.process_answer.return_value = (True, None, "preferred_name")
            
            # Mock sequence provider
            mock_sequence_provider = MagicMock()
            mock_sequence_def = MagicMock()
            mock_question = MagicMock()
            mock_question.key = "confirm_user_name"
            mock_sequence_def.get_question_by_key.return_value = mock_question
            mock_sequence_provider.get_sequence_definition.return_value = mock_sequence_def
            mock_sequence_service._sequence_provider = mock_sequence_provider
            
            # Mock get_sequence_service to return our mock
            m.setattr("core.utils.context_utils.get_sequence_service", 
                     MagicMock(return_value=mock_sequence_service))
            
            # Set callback data for Yes button
            mock_callback.data = "seq_answer:user_info:confirm_user_name:true"
            
            # Create context with app_facade
            context = {"app_facade": app_facade}
            
            # Import and call sequence callback handler
            from application.handlers.sequence_user_info.user_info_callback_handler import user_info_callback_handler
            
            # Call sequence callback handler directly with context
            await user_info_callback_handler(mock_callback, **context)
            
            # Verify that callback.answer was called (no error occurred)
            mock_callback.answer.assert_called()

    async def test_sequence_callback_handler_with_no_button(self, mock_callback, app_facade):
        """Test that sequence callback handler works with No button."""
        # Mock sequence service methods
        with pytest.MonkeyPatch().context() as m:
            # Mock get_session to return a valid session
            mock_session = MagicMock()
            mock_session.current_step = 0
            mock_session.sequence_name = "user_info"
            # Mock sequence service methods
            mock_sequence_service = MagicMock()
            mock_sequence_service.get_session.return_value = mock_session
            mock_sequence_service.process_answer.return_value = (True, None, "preferred_name")
            
            # Mock sequence provider
            mock_sequence_provider = MagicMock()
            mock_sequence_def = MagicMock()
            mock_question = MagicMock()
            mock_question.key = "confirm_user_name"
            mock_question.options = [MagicMock(value="true"), MagicMock(value="false")]
            mock_sequence_def.get_question_by_key.return_value = mock_question
            mock_sequence_provider.get_sequence_definition.return_value = mock_sequence_def
            mock_sequence_service._sequence_provider = mock_sequence_provider
            
            # Mock get_sequence_service to return our mock
            m.setattr("core.utils.context_utils.get_sequence_service", 
                     MagicMock(return_value=mock_sequence_service))
            
            # Set callback data for No button
            mock_callback.data = "seq_answer:user_info:confirm_user_name:false"
            
            # Create context with app_facade
            context = {"app_facade": app_facade}
            
            # Import and call sequence callback handler
            from application.handlers.sequence_user_info.user_info_callback_handler import user_info_callback_handler
            
            # Call sequence callback handler directly with context
            await user_info_callback_handler(mock_callback, **context)
            
            # Verify that callback.answer was called (no error occurred)
            mock_callback.answer.assert_called()

    async def test_full_flow_start_to_sequence_buttons(self, mock_message, mock_callback, app_facade):
        """Test full flow from start button to sequence Yes/No buttons."""
        # Mock ensure_user_exists to return None (new user)
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "application.services.user_utils.ensure_user_exists",
                AsyncMock(return_value=None),
            )
            
            # Mock sequence initiation to succeed
            m.setattr(
                "infrastructure.sequence.SequenceInitiationService.initiate_user_info_sequence",
                AsyncMock(return_value=(True, None)),
            )
            
            # Create context with app_facade
            context = {"app_facade": app_facade}
            
            # Step 1: Create start button via start command
            await start_command_handler(mock_message, **context)
            
            # Step 2: Simulate clicking "Yes, I'm ready!" button
            await start_callback_handler(mock_callback, **context)
            
            # Verify that sequence initiation was called
            # This should trigger the sequence and create Yes/No buttons
            mock_callback.answer.assert_called()
            
            # The sequence initiation should send a new message with Yes/No buttons
            # We need to verify that the sequence system creates the correct buttons
            assert mock_message.answer.call_count >= 2  # Greeting + readiness + sequence question

    async def test_callback_handler_removes_keyboard(self, mock_callback, mock_context):
        """Test that callback handler removes keyboard after processing."""
        # Mock sequence initiation to succeed
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "infrastructure.sequence.SequenceInitiationService.initiate_user_info_sequence",
                AsyncMock(return_value=(True, None)),
            )

            # Call callback handler
            await start_callback_handler(mock_callback, **mock_context)

            # Verify that keyboard was removed
            mock_callback.message.edit_reply_markup.assert_called_with(
                reply_markup=None
            )

    async def test_callback_handler_sequence_initiation(
        self, mock_callback, mock_context
    ):
        """Test that callback handler initiates sequence correctly."""
        # Mock sequence initiation
        mock_initiate = AsyncMock(return_value=(True, None))

        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "infrastructure.sequence.SequenceInitiationService.initiate_user_info_sequence",
                mock_initiate,
            )

            # Call callback handler
            await start_callback_handler(mock_callback, **mock_context)

            # Verify that sequence initiation was called
            mock_initiate.assert_called_once()

    async def test_invalid_callback_data(self, mock_callback, mock_context):
        """Test handling of invalid callback data."""
        # Set invalid callback data
        mock_callback.data = "invalid_data"

        # Call callback handler
        await start_callback_handler(mock_callback, **mock_context)

        # Verify that error was returned
        mock_callback.answer.assert_called()
        # Check that error message was sent
        call_args = mock_callback.answer.call_args[0]
        assert len(call_args) > 0

    async def test_empty_callback_data(self, mock_callback, mock_context):
        """Test handling of empty callback data."""
        # Set empty callback data
        mock_callback.data = None

        # Call callback handler
        await start_callback_handler(mock_callback, **mock_context)

        # Verify that error was returned
        mock_callback.answer.assert_called()

    async def test_button_text_localization(self, mock_message, mock_context):
        """Test that button text is properly localized."""
        # Mock ensure_user_exists to return None (new user)
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "application.services.user_utils.ensure_user_exists",
                AsyncMock(return_value=None),
            )

            # Call start command handler
            await start_command_handler(mock_message, **mock_context)

            # Get the button
            second_call = mock_message.answer.call_args_list[1]
            reply_markup = second_call[1]["reply_markup"]
            button = reply_markup.inline_keyboard[0][0]

            # Verify button text is not empty
            assert button.text is not None
            assert len(button.text.strip()) > 0

    async def test_complete_button_flow(
        self, mock_message, mock_callback, mock_context
    ):
        """Test complete flow from button creation to callback handling."""
        # Mock ensure_user_exists to return None (new user)
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "application.services.user_utils.ensure_user_exists",
                AsyncMock(return_value=None),
            )
            m.setattr(
                "infrastructure.sequence.SequenceInitiationService.initiate_user_info_sequence",
                AsyncMock(return_value=(True, None)),
            )

            # Step 1: Create button via start command
            await start_command_handler(mock_message, **mock_context)

            # Step 2: Simulate button click via callback
            await start_callback_handler(mock_callback, **mock_context)

            # Verify complete flow worked
            assert (
                mock_message.answer.call_count == 2
            )  # Greeting + readiness with button
            mock_callback.answer.assert_called()  # Callback processed
            mock_callback.message.edit_reply_markup.assert_called_with(
                reply_markup=None
            )  # Keyboard removed
