"""
Tests for sequence services functionality.

Comprehensive test coverage for the refactored sequence services including
session management, question handling, progress tracking, and completion.
"""

from pathlib import Path

# Add project root to path
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.sequence.services.completion_service import SequenceCompletionService
from core.sequence.services.progress_service import SequenceProgressService
from core.sequence.services.question_service import SequenceQuestionService
from core.sequence.services.session_service import SequenceSessionService
from core.sequence.types import QuestionType


class TestSequenceSessionService:
    """Test cases for SequenceSessionService."""

    @pytest.fixture
    def mock_session_manager(self):
        """Create mock session manager."""
        return MagicMock()

    @pytest.fixture
    def mock_sequence_provider(self):
        """Create mock sequence provider."""
        return MagicMock()

    @pytest.fixture
    def session_service(self, mock_session_manager, mock_sequence_provider):
        """Create session service with mocks."""
        return SequenceSessionService(mock_session_manager, mock_sequence_provider)

    @pytest.fixture
    def mock_sequence_definition(self):
        """Create mock sequence definition."""
        definition = MagicMock()
        definition.name = "test_sequence"
        definition.questions = [MagicMock(), MagicMock()]  # 2 questions
        definition.scored = False
        return definition

    def test_start_session_success(
        self,
        session_service,
        mock_session_manager,
        mock_sequence_provider,
        mock_sequence_definition,
    ):
        """Test successful sequence start."""
        user_id = 12345
        sequence_name = "test_sequence"

        # Setup mocks
        mock_sequence_provider.get_sequence_definition.return_value = (
            mock_sequence_definition
        )
        mock_session_manager.get_session.return_value = None  # No existing session
        mock_session_manager.create_session.return_value = "session_123"

        mock_session = MagicMock()
        mock_session_manager.get_session.return_value = mock_session

        # Test
        result = session_service.start_session(user_id, sequence_name)

        # Assertions
        assert result == "session_123"
        mock_sequence_provider.get_sequence_definition.assert_called_once_with(
            sequence_name
        )
        mock_session_manager.create_session.assert_called_once_with(
            user_id, sequence_name
        )

        # Should set session metadata
        assert mock_session.total_questions == 2
        assert mock_session.metadata["sequence_definition"] == "test_sequence"

    def test_start_session_sequence_not_found(
        self, session_service, mock_sequence_provider
    ):
        """Test starting session with non-existent sequence."""
        mock_sequence_provider.get_sequence_definition.return_value = None

        with pytest.raises(ValueError, match="Sequence 'unknown' not found"):
            session_service.start_session(12345, "unknown")

    def test_start_session_clears_existing(
        self,
        session_service,
        mock_session_manager,
        mock_sequence_provider,
        mock_sequence_definition,
    ):
        """Test that existing session is cleared when starting new one."""
        user_id = 12345
        sequence_name = "test_sequence"

        # Setup mocks - existing session
        existing_session = MagicMock()
        mock_sequence_provider.get_sequence_definition.return_value = (
            mock_sequence_definition
        )
        mock_session_manager.get_session.return_value = existing_session
        mock_session_manager.create_session.return_value = "session_123"

        # Test
        session_service.start_session(user_id, sequence_name)

        # Should clear existing session
        mock_session_manager.clear_session.assert_called_once_with(user_id)

    def test_get_session(self, session_service, mock_session_manager):
        """Test getting session."""
        user_id = 12345
        mock_session = MagicMock()
        mock_session_manager.get_session.return_value = mock_session

        result = session_service.get_session(user_id)

        assert result == mock_session
        mock_session_manager.get_session.assert_called_once_with(user_id)

    def test_add_answer(self, session_service, mock_session_manager):
        """Test adding answer."""
        user_id = 12345
        answer = MagicMock()
        mock_session_manager.add_answer.return_value = True

        result = session_service.add_answer(user_id, answer)

        assert result is True
        mock_session_manager.add_answer.assert_called_once_with(user_id, answer)

    def test_advance_step(self, session_service, mock_session_manager):
        """Test advancing step."""
        user_id = 12345
        mock_session_manager.advance_step.return_value = True

        result = session_service.advance_step(user_id)

        assert result is True
        mock_session_manager.advance_step.assert_called_once_with(user_id)

    def test_complete_session(self, session_service, mock_session_manager):
        """Test completing session."""
        user_id = 12345
        mock_session_manager.complete_session.return_value = True

        result = session_service.complete_session(user_id)

        assert result is True
        mock_session_manager.complete_session.assert_called_once_with(user_id)


class TestSequenceProgressService:
    """Test cases for SequenceProgressService."""

    @pytest.fixture
    def mock_sequence_provider(self):
        """Create mock sequence provider."""
        return MagicMock()

    @pytest.fixture
    def progress_service(self, mock_sequence_provider):
        """Create progress service with mock."""
        return SequenceProgressService(mock_sequence_provider)

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        session = MagicMock()
        session.current_step = 2
        session.sequence_name = "test_sequence"
        return session

    def test_get_progress(self, progress_service, mock_session, mock_sequence_provider):
        """Test getting progress."""
        # Setup mock
        mock_definition = MagicMock()
        mock_definition.questions = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]  # 3 questions
        mock_sequence_provider.get_sequence_definition.return_value = mock_definition
        mock_sequence_provider.should_show_question.return_value = True

        current_step, total_steps = progress_service.get_progress(mock_session)

        assert current_step == 2
        assert total_steps == 3

    def test_get_progress_no_session(self, progress_service):
        """Test getting progress with no session."""
        current_step, total_steps = progress_service.get_progress(None)

        assert current_step == 0
        assert total_steps == 0

    def test_is_complete(self, progress_service, mock_session):
        """Test is_complete method."""
        mock_session.is_complete.return_value = True

        result = progress_service.is_complete(mock_session)

        assert result is True
        mock_session.is_complete.assert_called_once()

    def test_is_complete_no_session(self, progress_service):
        """Test is_complete with no session."""
        result = progress_service.is_complete(None)

        assert result is False

    def test_get_visible_questions_count(
        self, progress_service, mock_session, mock_sequence_provider
    ):
        """Test getting visible questions count."""
        # Setup mock
        mock_definition = MagicMock()
        questions = [MagicMock(), MagicMock(), MagicMock()]
        mock_definition.questions = questions
        mock_sequence_provider.get_sequence_definition.return_value = mock_definition

        # First 2 questions visible, last one hidden
        mock_sequence_provider.should_show_question.side_effect = [True, True, False]

        result = progress_service.get_visible_questions_count(mock_session)

        assert result == 2

    def test_get_completion_percentage(
        self, progress_service, mock_session, mock_sequence_provider
    ):
        """Test getting completion percentage."""
        # Setup mock - 2/4 questions completed = 50%
        mock_definition = MagicMock()
        mock_definition.questions = [MagicMock()] * 4  # 4 questions
        mock_sequence_provider.get_sequence_definition.return_value = mock_definition
        mock_sequence_provider.should_show_question.return_value = True

        mock_session.current_step = 2

        result = progress_service.get_completion_percentage(mock_session)

        assert result == 50.0

    def test_get_remaining_questions_count(
        self, progress_service, mock_session, mock_sequence_provider
    ):
        """Test getting remaining questions count."""
        # Setup mock - 4 total, 2 completed = 2 remaining
        mock_definition = MagicMock()
        mock_definition.questions = [MagicMock()] * 4
        mock_sequence_provider.get_sequence_definition.return_value = mock_definition
        mock_sequence_provider.should_show_question.return_value = True

        mock_session.current_step = 2

        result = progress_service.get_remaining_questions_count(mock_session)

        assert result == 2

    def test_is_first_question(self, progress_service, mock_session):
        """Test checking if current question is first."""
        mock_session.current_step = 0

        result = progress_service.is_first_question(mock_session)

        assert result is True

    def test_is_last_question(
        self, progress_service, mock_session, mock_sequence_provider
    ):
        """Test checking if current question is last."""
        # Setup - 3 questions, on step 2 (last)
        mock_definition = MagicMock()
        mock_definition.questions = [MagicMock()] * 3
        mock_sequence_provider.get_sequence_definition.return_value = mock_definition
        mock_sequence_provider.should_show_question.return_value = True

        mock_session.current_step = 2

        result = progress_service.is_last_question(mock_session)

        assert result is True


class TestSequenceQuestionService:
    """Test cases for SequenceQuestionService."""

    @pytest.fixture
    def mock_sequence_provider(self):
        """Create mock sequence provider."""
        return MagicMock()

    @pytest.fixture
    def mock_question_renderer(self):
        """Create mock question renderer."""
        return AsyncMock()

    @pytest.fixture
    def question_service(self, mock_sequence_provider, mock_question_renderer):
        """Create question service with mocks."""
        return SequenceQuestionService(mock_sequence_provider, mock_question_renderer)

    @pytest.fixture
    def question_service_no_renderer(self, mock_sequence_provider):
        """Create question service without renderer."""
        return SequenceQuestionService(mock_sequence_provider)

    @pytest.fixture
    def mock_question(self):
        """Create mock question."""
        question = MagicMock()
        question.key = "test_question"
        question.question_text = "What is your name?"
        question.question_type = QuestionType.TEXT
        return question

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        session = MagicMock()
        session.current_step = 1
        return session

    @pytest.fixture
    def mock_message(self):
        """Create mock message."""
        message = AsyncMock()
        message.from_user.id = 12345
        return message

    @pytest.fixture
    def mock_translator(self):
        """Create mock translator."""
        translator = MagicMock()
        translator.translate.return_value = "Translated text"
        return translator

    @pytest.mark.asyncio
    async def test_send_question_with_renderer(
        self,
        question_service,
        mock_question_renderer,
        mock_question,
        mock_session,
        mock_message,
        mock_translator,
    ):
        """Test sending question with custom renderer."""
        # Setup mocks
        mock_question_renderer.render_question.return_value = ("Question text", None)
        mock_question_renderer.send_question_message.return_value = True

        result = await question_service.send_question(
            mock_message, mock_question, mock_session, mock_translator
        )

        assert result is True
        mock_question_renderer.render_question.assert_called_once()
        mock_question_renderer.send_question_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_question_without_renderer(
        self,
        question_service_no_renderer,
        mock_question,
        mock_session,
        mock_message,
        mock_translator,
    ):
        """Test sending question without custom renderer."""
        result = await question_service_no_renderer.send_question(
            mock_message, mock_question, mock_session, mock_translator
        )

        assert result is True
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_question_error(
        self,
        question_service,
        mock_question_renderer,
        mock_question,
        mock_session,
        mock_message,
        mock_translator,
    ):
        """Test sending question with error."""
        # Setup mock to fail
        mock_question_renderer.render_question.side_effect = Exception("Render error")
        mock_translator.translate.return_value = "Error message"

        result = await question_service.send_question(
            mock_message, mock_question, mock_session, mock_translator
        )

        assert result is False
        mock_message.answer.assert_called_with("Error message")

    def test_validate_answer_empty(self, question_service_no_renderer, mock_question):
        """Test validating empty answer."""
        is_valid, error = question_service_no_renderer.validate_answer(
            mock_question, ""
        )

        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_answer_whitespace_only(
        self, question_service_no_renderer, mock_question
    ):
        """Test validating whitespace-only answer."""
        is_valid, error = question_service_no_renderer.validate_answer(
            mock_question, "   "
        )

        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_answer_valid(self, question_service_no_renderer, mock_question):
        """Test validating valid answer."""
        is_valid, error = question_service_no_renderer.validate_answer(
            mock_question, "Valid answer"
        )

        assert is_valid is True
        assert error is None


class TestSequenceCompletionService:
    """Test cases for SequenceCompletionService."""

    @pytest.fixture
    def mock_sequence_provider(self):
        """Create mock sequence provider."""
        return MagicMock()

    @pytest.fixture
    def mock_question_renderer(self):
        """Create mock question renderer."""
        return AsyncMock()

    @pytest.fixture
    def mock_result_handler(self):
        """Create mock result handler."""
        return AsyncMock()

    @pytest.fixture
    def completion_service(
        self, mock_sequence_provider, mock_question_renderer, mock_result_handler
    ):
        """Create completion service with mocks."""
        return SequenceCompletionService(
            mock_sequence_provider, mock_question_renderer, mock_result_handler
        )

    @pytest.fixture
    def completion_service_no_handlers(self, mock_sequence_provider):
        """Create completion service without handlers."""
        return SequenceCompletionService(mock_sequence_provider)

    @pytest.fixture
    def mock_session(self):
        """Create mock completed session."""
        session = MagicMock()
        session.sequence_name = "test_sequence"
        session.user_id = 12345
        session.total_score = None
        session.max_possible_score = None
        session.created_at = 1000
        session.completed_at = 2000
        return session

    @pytest.fixture
    def mock_message(self):
        """Create mock message."""
        message = AsyncMock()
        message.from_user.id = 12345
        return message

    @pytest.fixture
    def mock_translator(self):
        """Create mock translator."""
        translator = MagicMock()
        translator.translate.return_value = "Completion message"
        return translator

    @pytest.mark.asyncio
    async def test_send_completion_message_with_renderer(
        self,
        completion_service,
        mock_question_renderer,
        mock_session,
        mock_message,
        mock_translator,
    ):
        """Test sending completion message with custom renderer."""
        mock_question_renderer.send_completion_message.return_value = True

        result = await completion_service.send_completion_message(
            mock_message, mock_session, mock_translator
        )

        assert result is True
        mock_question_renderer.send_completion_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_completion_message_without_renderer(
        self,
        completion_service_no_handlers,
        mock_session,
        mock_message,
        mock_translator,
    ):
        """Test sending completion message without renderer."""
        result = await completion_service_no_handlers.send_completion_message(
            mock_message, mock_session, mock_translator
        )

        assert result is True
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_completion_with_handler(
        self, completion_service, mock_result_handler, mock_session, mock_message
    ):
        """Test handling completion with custom handler."""
        mock_result_handler.handle_sequence_completion.return_value = None

        result = await completion_service.handle_completion(
            mock_session, mock_message.from_user
        )

        assert result is True
        mock_result_handler.handle_sequence_completion.assert_called_once_with(
            mock_session, mock_message.from_user
        )

    @pytest.mark.asyncio
    async def test_handle_completion_without_handler(
        self, completion_service_no_handlers, mock_session, mock_message
    ):
        """Test handling completion without custom handler."""
        result = await completion_service_no_handlers.handle_completion(
            mock_session, mock_message.from_user
        )

        assert result is True

    def test_get_completion_summary_basic(
        self, completion_service_no_handlers, mock_session
    ):
        """Test getting completion summary."""
        mock_session.answers = [MagicMock(), MagicMock()]  # 2 answers

        summary = completion_service_no_handlers.get_completion_summary(mock_session)

        assert summary["sequence_name"] == "test_sequence"
        assert summary["user_id"] == 12345
        assert summary["total_questions"] == 2
        assert summary["duration"] == 1000  # 2000 - 1000

    def test_get_completion_summary_with_scoring(
        self, completion_service_no_handlers, mock_session
    ):
        """Test getting completion summary with scoring."""
        mock_session.answers = [MagicMock()]
        mock_session.total_score = 8
        mock_session.max_possible_score = 10

        summary = completion_service_no_handlers.get_completion_summary(mock_session)

        assert summary["total_score"] == 8
        assert summary["max_possible_score"] == 10
        assert summary["percentage"] == 80.0
