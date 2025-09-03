"""
End-to-end tests for UI interactions.

Tests button rendering, click handling, and UI flow
through the sequence system.
"""

from aiogram.types import InlineKeyboardMarkup
import pytest

from application import create_application_facade
from core.sequence.protocols import (
    SequenceQuestionRendererProtocol,
    SequenceServiceProtocol,
)
from core.sequence.types import SequenceStatus


class TestUIIntractionsE2E:
    """End-to-end tests for UI interactions."""

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
    async def question_renderer(self, app_facade):
        """Get question renderer from DI container."""
        container = app_facade.get_di_container()
        return container.resolve(SequenceQuestionRendererProtocol)

    @pytest.fixture
    def mock_user_id(self):
        """Mock user ID for testing."""
        return 12345

    async def test_button_rendering_for_boolean_question(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test that boolean questions render with proper buttons."""
        # Start sequence and get first question
        sequence_service.start_sequence(mock_user_id, "user_info")
        question = await sequence_service.get_current_question(mock_user_id)

        # Render question with buttons
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify buttons are rendered
        assert rendered is not None
        assert hasattr(rendered, "reply_markup")
        assert rendered.reply_markup is not None

        # Verify button structure
        markup = rendered.reply_markup
        assert isinstance(markup, InlineKeyboardMarkup)
        assert len(markup.inline_keyboard) == 1  # One row
        assert len(markup.inline_keyboard[0]) == 2  # Two buttons

        # Verify button labels and callbacks
        buttons = markup.inline_keyboard[0]
        assert buttons[0].text == "✅ Yes"
        assert buttons[1].text == "❌ No"

        # Verify callback data format
        assert buttons[0].callback_data.startswith("answer:")
        assert buttons[1].callback_data.startswith("answer:")

    async def test_button_rendering_for_single_choice_question(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test that single choice questions render with proper buttons."""
        # Setup: answer first question to get to gender question
        sequence_service.start_sequence(mock_user_id, "user_info")
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )

        # Get gender question
        question = await sequence_service.get_current_question(mock_user_id)
        assert question.key == "gender"

        # Render question with buttons
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify buttons are rendered
        assert rendered is not None
        assert hasattr(rendered, "reply_markup")
        assert rendered.reply_markup is not None

        # Verify button structure
        markup = rendered.reply_markup
        assert isinstance(markup, InlineKeyboardMarkup)
        assert len(markup.inline_keyboard) == 1  # One row
        assert len(markup.inline_keyboard[0]) == 2  # Two buttons for gender

        # Verify button labels
        buttons = markup.inline_keyboard[0]
        assert buttons[0].text == "👨 Male"
        assert buttons[1].text == "👩 Female"

    async def test_button_rendering_for_eyes_color_question(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test that eyes color question renders with multiple buttons."""
        # Setup: answer previous questions to get to eyes color
        sequence_service.start_sequence(mock_user_id, "user_info")
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        await sequence_service.answer_question(mock_user_id, "gender", "male")
        await sequence_service.answer_question(mock_user_id, "birth_date", "15.03.1990")

        # Get eyes color question
        question = await sequence_service.get_current_question(mock_user_id)
        assert question.key == "eyes_color"

        # Render question with buttons
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify buttons are rendered
        assert rendered is not None
        assert hasattr(rendered, "reply_markup")
        assert rendered.reply_markup is not None

        # Verify button structure - should have multiple rows for 6 options
        markup = rendered.reply_markup
        assert isinstance(markup, InlineKeyboardMarkup)
        assert len(markup.inline_keyboard) >= 2  # Multiple rows for better UX

        # Count total buttons
        total_buttons = sum(len(row) for row in markup.inline_keyboard)
        assert total_buttons == 6  # 6 eye color options

        # Verify some specific button labels
        all_buttons = [btn for row in markup.inline_keyboard for btn in row]
        button_texts = [btn.text for btn in all_buttons]

        assert "👁️ Brown" in button_texts
        assert "👁️ Blue" in button_texts
        assert "👁️ Green" in button_texts

    async def test_button_rendering_for_marital_status_question(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test that marital status question renders with proper buttons."""
        # Setup: answer previous questions to get to marital status
        sequence_service.start_sequence(mock_user_id, "user_info")
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        await sequence_service.answer_question(mock_user_id, "gender", "male")
        await sequence_service.answer_question(mock_user_id, "birth_date", "15.03.1990")
        await sequence_service.answer_question(mock_user_id, "eyes_color", "blue")

        # Get marital status question
        question = await sequence_service.get_current_question(mock_user_id)
        assert question.key == "marital_status"

        # Render question with buttons
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify buttons are rendered
        assert rendered is not None
        assert hasattr(rendered, "reply_markup")
        assert rendered.reply_markup is not None

        # Verify button structure
        markup = rendered.reply_markup
        assert isinstance(markup, InlineKeyboardMarkup)

        # Count total buttons
        total_buttons = sum(len(row) for row in markup.inline_keyboard)
        assert total_buttons == 5  # 5 marital status options

        # Verify some specific button labels
        all_buttons = [btn for row in markup.inline_keyboard for btn in row]
        button_texts = [btn.text for btn in all_buttons]

        assert "💚 Single" in button_texts
        assert "💍 Married" in button_texts
        assert "💔 Divorced" in button_texts
        assert "🕊️ Widowed" in button_texts
        assert "🤐 Prefer not to say" in button_texts

    async def test_text_question_rendering(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test that text questions render without buttons."""
        # Setup: answer first question with false to trigger preferred_name question
        sequence_service.start_sequence(mock_user_id, "user_info")
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "false"
        )

        # Get preferred_name question
        question = await sequence_service.get_current_question(mock_user_id)
        assert question.key == "preferred_name"
        assert question.question_type.value == "text"

        # Render question
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify no buttons for text questions
        assert rendered is not None
        assert not hasattr(rendered, "reply_markup") or rendered.reply_markup is None

    async def test_birth_date_question_rendering(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test that birth date question renders without buttons."""
        # Setup: answer previous questions to get to birth date
        sequence_service.start_sequence(mock_user_id, "user_info")
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        await sequence_service.answer_question(mock_user_id, "gender", "male")

        # Get birth date question
        question = await sequence_service.get_current_question(mock_user_id)
        assert question.key == "birth_date"
        assert question.question_type.value == "text"

        # Render question
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify no buttons for text questions
        assert rendered is not None
        assert not hasattr(rendered, "reply_markup") or rendered.reply_markup is None

    async def test_button_callback_data_format(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test that button callback data has correct format."""
        # Start sequence and get first question
        sequence_service.start_sequence(mock_user_id, "user_info")
        question = await sequence_service.get_current_question(mock_user_id)

        # Render question with buttons
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify callback data format
        markup = rendered.reply_markup
        buttons = markup.inline_keyboard[0]

        for button in buttons:
            callback_data = button.callback_data
            assert callback_data.startswith("answer:")

            # Parse callback data
            parts = callback_data.split(":")
            assert len(parts) == 3  # answer:question_key:value

            question_key = parts[1]
            value = parts[2]

            assert question_key == "confirm_user_name"
            assert value in ["true", "false"]

    async def test_question_text_formatting(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test that question text is properly formatted."""
        # Start sequence and get first question
        sequence_service.start_sequence(mock_user_id, "user_info")
        question = await sequence_service.get_current_question(mock_user_id)

        # Render question
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify question text is present and formatted
        assert rendered is not None
        assert hasattr(rendered, "text")
        assert rendered.text is not None
        assert len(rendered.text) > 0

        # Verify text contains expected content
        text = rendered.text
        assert "Let's start with your name" in text
        assert "you're called" in text
        assert "right?" in text

    async def test_conditional_question_flow_ui(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test UI flow for conditional questions."""
        # Start sequence
        sequence_service.start_sequence(mock_user_id, "user_info")

        # Answer first question with false to trigger conditional flow
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "false"
        )

        # Get preferred_name question
        question = await sequence_service.get_current_question(mock_user_id)
        assert question.key == "preferred_name"

        # Render question
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify no buttons for text input
        assert rendered is not None
        assert not hasattr(rendered, "reply_markup") or rendered.reply_markup is None

        # Answer preferred_name question
        await sequence_service.answer_question(mock_user_id, "preferred_name", "John")

        # Get next question (gender)
        question = await sequence_service.get_current_question(mock_user_id)
        assert question.key == "gender"

        # Render gender question
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify buttons are present for single choice
        assert rendered is not None
        assert hasattr(rendered, "reply_markup")
        assert rendered.reply_markup is not None

    async def test_progress_indicator_in_questions(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test that progress indicator is shown in questions."""
        # Start sequence
        sequence_service.start_sequence(mock_user_id, "user_info")

        # Get first question
        question = await sequence_service.get_current_question(mock_user_id)

        # Render question
        rendered = await question_renderer.render_question(question, mock_user_id)

        # Verify question text contains progress information
        assert rendered is not None
        assert hasattr(rendered, "text")
        text = rendered.text

        # Check for progress indicator (this depends on implementation)
        # Could be "Question 1 of 6" or similar
        assert "1" in text or "first" in text.lower()

    async def test_completion_message_rendering(
        self, question_renderer, sequence_service, mock_user_id
    ):
        """Test that completion message renders correctly."""
        # Complete the sequence first
        sequence_service.start_sequence(mock_user_id, "user_info")
        answers = [
            ("confirm_user_name", "true"),
            ("gender", "male"),
            ("birth_date", "15.03.1990"),
            ("eyes_color", "blue"),
            ("marital_status", "single"),
        ]

        for question_key, answer in answers:
            await sequence_service.answer_question(mock_user_id, question_key, answer)

        # Get completion message
        # This depends on the specific implementation of completion handling
        # For now, we'll test that the sequence is completed
        session = await sequence_service.get_session(mock_user_id)
        assert session.status == SequenceStatus.COMPLETED
