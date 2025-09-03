"""
End-to-end tests for Telegram integration.

Tests the complete flow from Telegram message to sequence response,
including message handling, callback processing, and response generation.
"""

from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import CallbackQuery, Chat, InlineKeyboardMarkup, Message
from aiogram.types import User as TelegramUser
import pytest

from application import create_application_facade
from application.handlers.command_start.start_callback_handler import (
    start_callback_handler,
)
from application.handlers.command_start.start_command_handler import (
    start_command_handler,
)
from core.sequence.protocols import SequenceServiceProtocol
from core.sequence.types import SequenceStatus


class TestTelegramIntegrationE2E:
    """End-to-end tests for Telegram integration."""

    @pytest.fixture
    async def app_facade(self):
        """Create application facade for testing."""
        return create_application_facade()

    @pytest.fixture
    async def sequence_service(self, app_facade):
        """Get sequence service from DI container."""
        container = app_facade.get_di_container()
        return container.resolve(SequenceServiceProtocol)

    @pytest.fixture
    def mock_telegram_user(self):
        """Create mock Telegram user."""
        user = MagicMock(spec=TelegramUser)
        user.id = 12345
        user.username = "test_user"
        user.first_name = "Test"
        user.last_name = "User"
        return user

    @pytest.fixture
    def mock_chat(self):
        """Create mock Telegram chat."""
        chat = MagicMock(spec=Chat)
        chat.id = 12345
        chat.type = "private"
        return chat

    @pytest.fixture
    def mock_message(self, mock_telegram_user, mock_chat):
        """Create mock Telegram message."""
        message = MagicMock(spec=Message)
        message.from_user = mock_telegram_user
        message.chat = mock_chat
        message.text = "/start"
        message.message_id = 1
        return message

    @pytest.fixture
    def mock_callback_query(self, mock_telegram_user, mock_chat):
        """Create mock Telegram callback query."""
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = mock_telegram_user
        callback.message = MagicMock()
        callback.message.chat = mock_chat
        callback.message.message_id = 1
        callback.data = "start_sequence:user_info"
        callback.id = "test_callback_id"
        return callback

    @pytest.fixture
    def mock_bot(self):
        """Create mock Telegram bot."""
        bot = MagicMock()
        bot.send_message = AsyncMock()
        bot.answer_callback_query = AsyncMock()
        bot.edit_message_text = AsyncMock()
        return bot

    @pytest.fixture
    def mock_state(self):
        """Create mock FSM state."""
        state = MagicMock()
        state.get_state = AsyncMock(return_value=None)
        state.set_state = AsyncMock()
        state.clear = AsyncMock()
        return state

    async def test_start_command_flow(self, mock_message, mock_bot, mock_state):
        """Test complete start command flow."""
        # Mock the bot.send_message to capture what would be sent
        mock_bot.send_message.return_value = MagicMock()

        # Execute start command handler
        await start_command_handler(mock_message, mock_bot, mock_state)

        # Verify bot.send_message was called
        mock_bot.send_message.assert_called()

        # Verify the message contains expected content
        call_args = mock_bot.send_message.call_args
        chat_id = call_args[0][0]  # First argument is chat_id
        text = call_args[0][1]  # Second argument is text
        reply_markup = call_args[1].get("reply_markup")  # Optional argument

        assert chat_id == mock_message.chat.id
        assert "Hello, I'm your personal psychological mentor!" in text
        assert reply_markup is not None

        # Verify reply markup has the expected button
        assert isinstance(reply_markup, InlineKeyboardMarkup)
        buttons = reply_markup.inline_keyboard[0]
        assert len(buttons) == 1
        assert buttons[0].text == "Yes, I'm ready!"

    async def test_start_callback_flow(
        self, mock_callback_query, mock_bot, mock_state, sequence_service
    ):
        """Test complete start callback flow."""
        # Mock the bot methods
        mock_bot.send_message.return_value = MagicMock()
        mock_bot.answer_callback_query.return_value = MagicMock()

        # Execute start callback handler
        await start_callback_handler(mock_callback_query, mock_bot, mock_state)

        # Verify callback was answered
        mock_bot.answer_callback_query.assert_called_with(
            callback_query_id=mock_callback_query.id
        )

        # Verify sequence was started
        session = await sequence_service.get_session(mock_callback_query.from_user.id)
        assert session is not None
        assert session.sequence_name == "user_info"
        assert session.status == SequenceStatus.ACTIVE

        # Verify first question was sent
        mock_bot.send_message.assert_called()
        call_args = mock_bot.send_message.call_args
        text = call_args[0][1]

        # Should contain first question text
        assert "Let's start with your name" in text

    async def test_sequence_question_flow(self, mock_bot, mock_state, sequence_service):
        """Test complete sequence question flow."""
        user_id = 12345

        # Start sequence
        sequence_service.start_sequence(user_id, "user_info")

        # Get first question
        question = await sequence_service.get_current_question(user_id)
        assert question.key == "confirm_user_name"

        # Create mock message for answering
        mock_message = MagicMock(spec=Message)
        mock_message.from_user.id = user_id
        mock_message.text = "true"

        # Mock the message handler
        with patch(
            "application.handlers.sequence_user_info.user_info_message_handler.user_info_message_handler"
        ) as mock_handler:
            mock_handler.return_value = None

            # This would normally be called by the router
            # For testing, we'll verify the sequence state changes
            await sequence_service.answer_question(user_id, "confirm_user_name", "true")

            # Verify next question
            next_question = await sequence_service.get_current_question(user_id)
            assert next_question.key == "gender"

    async def test_sequence_callback_flow(self, mock_bot, mock_state, sequence_service):
        """Test complete sequence callback flow."""
        user_id = 12345

        # Start sequence
        sequence_service.start_sequence(user_id, "user_info")

        # Create mock callback for answering
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.from_user.id = user_id
        mock_callback.data = "answer:confirm_user_name:true"

        # Mock the callback handler
        with patch(
            "application.handlers.sequence_user_info.user_info_callback_handler.user_info_callback_handler"
        ) as mock_handler:
            mock_handler.return_value = None

            # This would normally be called by the router
            # For testing, we'll verify the sequence state changes
            await sequence_service.answer_question(user_id, "confirm_user_name", "true")

            # Verify next question
            next_question = await sequence_service.get_current_question(user_id)
            assert next_question.key == "gender"

    async def test_complete_user_journey(self, mock_bot, mock_state, sequence_service):
        """Test complete user journey from start to finish."""
        user_id = 12345

        # Start sequence
        session_id = sequence_service.start_sequence(user_id, "user_info")
        assert session_id is not None

        # Get session details
        session = await sequence_service.get_session(user_id)
        assert session.status == SequenceStatus.ACTIVE

        # Answer all questions in sequence
        answers = [
            ("confirm_user_name", "true"),
            ("gender", "female"),
            ("birth_date", "20.07.1985"),
            ("eyes_color", "green"),
            ("marital_status", "married"),
        ]

        for question_key, answer in answers:
            result = await sequence_service.answer_question(
                user_id, question_key, answer
            )
            assert result.success, (
                f"Failed to answer {question_key}: {result.error_message}"
            )

        # Verify sequence completion
        final_session = await sequence_service.get_session(user_id)
        assert final_session.status == SequenceStatus.COMPLETED

        # Verify all answers are recorded
        progress = await sequence_service.get_progress(user_id)
        assert progress is not None
        assert len(progress.answers) == 5

    async def test_error_handling_in_telegram_flow(
        self, mock_bot, mock_state, sequence_service
    ):
        """Test error handling in Telegram flow."""
        user_id = 12345

        # Start sequence
        sequence_service.start_sequence(user_id, "user_info")

        # Try to answer with invalid data
        result = await sequence_service.answer_question(
            user_id, "confirm_user_name", "maybe"
        )

        # Should fail
        assert not result.success
        assert result.error_message is not None

        # Sequence should still be in progress
        session = await sequence_service.get_session(user_id)
        assert session.status == SequenceStatus.ACTIVE

        # Current question should still be the same
        question = await sequence_service.get_current_question(user_id)
        assert question.key == "confirm_user_name"

    async def test_sequence_restart_in_telegram_flow(
        self, mock_bot, mock_state, sequence_service
    ):
        """Test sequence restart in Telegram flow."""
        user_id = 12345

        # Complete sequence first
        sequence_service.start_sequence(user_id, "user_info")
        answers = [
            ("confirm_user_name", "true"),
            ("gender", "male"),
            ("birth_date", "10.01.1995"),
            ("eyes_color", "brown"),
            ("marital_status", "single"),
        ]

        for question_key, answer in answers:
            await sequence_service.answer_question(user_id, question_key, answer)

        # Verify completion
        session = await sequence_service.get_session(user_id)
        assert session.status == SequenceStatus.COMPLETED

        # Restart sequence
        new_session_id = sequence_service.start_sequence(user_id, "user_info")
        assert new_session_id is not None

        # Get session details
        new_session = await sequence_service.get_session(user_id)
        assert new_session.status == SequenceStatus.ACTIVE

        # Verify we're back to first question
        question = await sequence_service.get_current_question(user_id)
        assert question.key == "confirm_user_name"

    async def test_localization_in_telegram_flow(
        self, mock_bot, mock_state, sequence_service
    ):
        """Test localization in Telegram flow."""
        user_id = 12345

        # Start sequence
        sequence_service.start_sequence(user_id, "user_info")

        # Get first question
        question = await sequence_service.get_current_question(user_id)

        # Verify question text contains localized content
        # This depends on the current user's language setting
        # For now, we'll verify the question structure
        assert (
            question.question_text_key
            == "handlers.user_info.questions.confirm_user_name.question"
        )

        # Verify question options are localized
        assert len(question.options) == 2
        assert (
            question.options[0].label_key
            == "handlers.user_info.questions.confirm_user_name.options.yes"
        )
        assert (
            question.options[1].label_key
            == "handlers.user_info.questions.confirm_user_name.options.no"
        )

    async def test_progress_tracking_in_telegram_flow(
        self, mock_bot, mock_state, sequence_service
    ):
        """Test progress tracking in Telegram flow."""
        user_id = 12345

        # Start sequence
        sequence_service.start_sequence(user_id, "user_info")

        # Check initial progress
        progress = await sequence_service.get_progress(user_id)
        assert progress.current_question_index == 0
        assert progress.total_questions == 6
        assert progress.completion_percentage == 0.0

        # Answer first question
        await sequence_service.answer_question(user_id, "confirm_user_name", "true")

        # Check updated progress
        progress = await sequence_service.get_progress(user_id)
        assert progress.current_question_index == 1
        assert progress.completion_percentage > 0.0

        # Answer second question
        await sequence_service.answer_question(user_id, "gender", "male")

        # Check further progress
        progress = await sequence_service.get_progress(user_id)
        assert progress.current_question_index == 2
        assert progress.completion_percentage > 16.0  # More than 2/6

    async def test_session_management_in_telegram_flow(
        self, mock_bot, mock_state, sequence_service
    ):
        """Test session management in Telegram flow."""
        user_id = 12345

        # Start sequence
        session_id = sequence_service.start_sequence(user_id, "user_info")
        assert session_id is not None

        # Get session details
        session = await sequence_service.get_session(user_id)
        assert session.session_id == session_id
        assert session.user_id == user_id
        assert session.sequence_name == "user_info"

        # Verify session state
        assert session.status == SequenceStatus.ACTIVE
        assert session.start_time is not None

    async def test_start_command_handler(self, app_facade, mock_message):
        """Test /start command handler."""
        # Get handler from facade
        router = app_facade.get_main_router()

        # Find start command handler
        start_handler = None
        for handler in router.handlers:
            if hasattr(handler, "callback") and "start_command_handler" in str(
                handler.callback
            ):
                start_handler = handler.callback
                break

        assert start_handler is not None, "Start command handler not found"

        # Test handler execution
        with patch(
            "application.handlers.command_start.start_command_handler.start_command_handler"
        ) as mock_handler:
            mock_handler.return_value = "Welcome message"
            result = await start_handler(mock_message)
            assert result == "Welcome message"

    async def test_start_callback_handler(self, app_facade, mock_callback_query):
        """Test start callback handler."""
        # Get handler from facade
        router = app_facade.get_main_router()

        # Find start callback handler
        start_callback_handler = None
        for handler in router.handlers:
            if hasattr(handler, "callback") and "start_callback_handler" in str(
                handler.callback
            ):
                start_callback_handler = handler.callback
                break

        assert start_callback_handler is not None, "Start callback handler not found"

        # Test handler execution
        with patch(
            "application.handlers.command_start.start_callback_handler.start_callback_handler"
        ) as mock_handler:
            mock_handler.return_value = "Callback response"
            result = await start_callback_handler(mock_callback_query)
            assert result == "Callback response"

    async def test_user_info_message_handler(
        self, app_facade, mock_message, sequence_service
    ):
        """Test user info message handler."""
        # Get handler from facade
        router = app_facade.get_main_router()

        # Find user info message handler
        message_handler = None
        for handler in router.handlers:
            if hasattr(handler, "callback") and "user_info_message_handler" in str(
                handler.callback
            ):
                message_handler = handler.callback
                break

        assert message_handler is not None, "User info message handler not found"

        # Start sequence first
        sequence_service.start_sequence(mock_message.from_user.id, "user_info")

        # Test handler execution
        with patch(
            "application.handlers.sequence_user_info.user_info_message_handler.user_info_message_handler"
        ) as mock_handler:
            mock_handler.return_value = "Message response"
            result = await message_handler(mock_message)
            assert result == "Message response"

    async def test_user_info_callback_handler(
        self, app_facade, mock_callback_query, sequence_service
    ):
        """Test user info callback handler."""
        # Get handler from facade
        router = app_facade.get_main_router()

        # Find user info callback handler
        callback_handler = None
        for handler in router.handlers:
            if hasattr(handler, "callback") and "user_info_callback_handler" in str(
                handler.callback
            ):
                callback_handler = handler.callback
                break

        assert callback_handler is not None, "User info callback handler not found"

        # Start sequence first
        sequence_service.start_sequence(mock_callback_query.from_user.id, "user_info")

        # Test handler execution
        with patch(
            "application.handlers.sequence_user_info.user_info_callback_handler.user_info_callback_handler"
        ) as mock_handler:
            mock_handler.return_value = "Callback response"
            result = await callback_handler(mock_callback_query)
            assert result == "Callback response"

    async def test_complete_user_journey_with_buttons(
        self, app_facade, sequence_service, mock_user_id
    ):
        """Test complete user journey using button interactions."""
        # Start sequence
        sequence_service.start_sequence(mock_user_id, "user_info")

        # Get first question
        question = await sequence_service.get_current_question(mock_user_id)
        assert question.key == "confirm_user_name"

        # Answer with button click (simulating callback)
        result = await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        assert result.success
        assert result.next_question is not None
        assert result.next_question.key == "gender"

        # Answer gender question
        result = await sequence_service.answer_question(
            mock_user_id, "gender", "female"
        )
        assert result.success
        assert result.next_question is not None
        assert result.next_question.key == "birth_date"

        # Answer birth date question
        result = await sequence_service.answer_question(
            mock_user_id, "birth_date", "20.07.1985"
        )
        assert result.success
        assert result.next_question is not None
        assert result.next_question.key == "eyes_color"

        # Answer eyes color question
        result = await sequence_service.answer_question(
            mock_user_id, "eyes_color", "green"
        )
        assert result.success
        assert result.next_question is not None
        assert result.next_question.key == "marital_status"

        # Answer marital status question
        result = await sequence_service.answer_question(
            mock_user_id, "marital_status", "married"
        )
        assert result.success
        assert result.sequence_completed

        # Verify sequence completion
        final_session = await sequence_service.get_session(mock_user_id)
        assert final_session.status == SequenceStatus.COMPLETED

    async def test_complete_user_journey_with_text_input(
        self, app_facade, sequence_service, mock_user_id
    ):
        """Test complete user journey using text input."""
        # Start sequence
        sequence_service.start_sequence(mock_user_id, "user_info")

        # Answer first question with false to trigger text input
        result = await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "false"
        )
        assert result.success
        assert result.next_question is not None
        assert result.next_question.key == "preferred_name"

        # Answer preferred name question with text
        result = await sequence_service.answer_question(
            mock_user_id, "preferred_name", "John"
        )
        assert result.success
        assert result.next_question is not None
        assert result.next_question.key == "gender"

        # Continue with button answers
        result = await sequence_service.answer_question(mock_user_id, "gender", "male")
        assert result.success

        result = await sequence_service.answer_question(
            mock_user_id, "birth_date", "15.03.1990"
        )
        assert result.success

        result = await sequence_service.answer_question(
            mock_user_id, "eyes_color", "blue"
        )
        assert result.success

        result = await sequence_service.answer_question(
            mock_user_id, "marital_status", "single"
        )
        assert result.success
        assert result.sequence_completed

        # Verify sequence completion
        final_session = await sequence_service.get_session(mock_user_id)
        assert final_session.status == SequenceStatus.COMPLETED

    async def test_error_handling_in_user_journey(
        self, app_facade, sequence_service, mock_user_id
    ):
        """Test error handling during user journey."""
        # Start sequence
        sequence_service.start_sequence(mock_user_id, "user_info")

        # Test invalid answer for boolean question
        result = await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "maybe"
        )
        assert not result.success
        assert result.error_message is not None

        # Sequence should still be in progress
        session = await sequence_service.get_session(mock_user_id)
        assert session.status == SequenceStatus.ACTIVE

        # Test invalid answer for single choice question
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        result = await sequence_service.answer_question(
            mock_user_id, "gender", "invalid_gender"
        )
        assert not result.success
        assert result.error_message is not None

        # Test invalid date format
        await sequence_service.answer_question(mock_user_id, "gender", "male")
        result = await sequence_service.answer_question(
            mock_user_id, "birth_date", "invalid_date"
        )
        assert not result.success
        assert "Invalid date format" in result.error_message

    async def test_sequence_restart_after_completion(
        self, app_facade, sequence_service, mock_user_id
    ):
        """Test restarting sequence after completion."""
        # Complete sequence first
        sequence_service.start_sequence(mock_user_id, "user_info")
        answers = [
            ("confirm_user_name", "true"),
            ("gender", "male"),
            ("birth_date", "10.01.1995"),
            ("eyes_color", "brown"),
            ("marital_status", "single"),
        ]

        for question_key, answer in answers:
            await sequence_service.answer_question(mock_user_id, question_key, answer)

        # Verify completion
        session = await sequence_service.get_session(mock_user_id)
        assert session.status == SequenceStatus.COMPLETED

        # Restart sequence
        new_session_id = sequence_service.start_sequence(mock_user_id, "user_info")
        assert new_session_id is not None

        # Verify we're back to first question
        question = await sequence_service.get_current_question(mock_user_id)
        assert question.key == "confirm_user_name"

        # Verify session state
        retrieved_session = await sequence_service.get_session(mock_user_id)
        assert retrieved_session.status == SequenceStatus.ACTIVE

    async def test_session_persistence_across_restarts(
        self, app_facade, sequence_service, mock_user_id
    ):
        """Test that session data persists correctly."""
        # Start sequence and answer some questions
        sequence_service.start_sequence(mock_user_id, "user_info")
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        await sequence_service.answer_question(mock_user_id, "gender", "female")

        # Get session and verify progress
        session = await sequence_service.get_session(mock_user_id)
        assert session.status == SequenceStatus.ACTIVE

        # Get progress
        progress = await sequence_service.get_progress(mock_user_id)
        assert progress is not None
        assert len(progress.answers) == 2

        # Verify answers are recorded
        assert progress.answers["confirm_user_name"] == "true"
        assert progress.answers["gender"] == "female"

        # Continue with more answers
        await sequence_service.answer_question(mock_user_id, "birth_date", "15.03.1990")
        await sequence_service.answer_question(mock_user_id, "eyes_color", "blue")
        await sequence_service.answer_question(
            mock_user_id, "marital_status", "married"
        )

        # Verify completion
        final_session = await sequence_service.get_session(mock_user_id)
        assert final_session.status == SequenceStatus.COMPLETED

        # Verify all answers are recorded
        final_progress = await sequence_service.get_progress(mock_user_id)
        assert len(final_progress.answers) == 5
        assert final_progress.answers["marital_status"] == "married"
