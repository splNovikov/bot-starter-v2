"""
End-to-end tests for user_info sequence.

Tests the complete user journey through the user_info sequence,
including all questions, validations, and completion.
"""

import pytest

from application import create_application_facade
from core.sequence.protocols import SequenceServiceProtocol
from core.sequence.types import SequenceStatus


class TestUserInfoSequenceE2E:
    """End-to-end tests for user_info sequence."""

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
    def mock_user_id(self):
        """Mock user ID for testing."""
        return 12345

    @pytest.fixture
    def mock_user_data(self):
        """Mock user data for testing."""
        return {
            "id": 12345,
            "username": "test_user",
            "first_name": "Test",
            "last_name": "User",
        }

    async def test_sequence_initialization(self, app_facade, sequence_service):
        """Test that sequence system initializes correctly."""
        # Verify sequence is registered
        sequences = app_facade.get_sequence_definitions()
        assert len(sequences) == 1
        assert sequences[0].name == "user_info"

        # Verify sequence has correct questions
        user_info_seq = sequences[0]
        assert len(user_info_seq.questions) == 6
        assert user_info_seq.questions[0].key == "confirm_user_name"
        assert user_info_seq.questions[1].key == "preferred_name"
        assert user_info_seq.questions[2].key == "gender"
        assert user_info_seq.questions[3].key == "birth_date"
        assert user_info_seq.questions[4].key == "eyes_color"
        assert user_info_seq.questions[5].key == "marital_status"

    async def test_sequence_start_and_first_question(
        self, sequence_service, mock_user_id
    ):
        """Test starting sequence and getting first question."""
        # Start sequence
        session_id = sequence_service.start_sequence(mock_user_id, "user_info")
        assert session_id is not None

        # Get session details
        session = await sequence_service.get_session(mock_user_id)
        assert session is not None
        assert session.user_id == mock_user_id
        assert session.sequence_name == "user_info"
        assert session.status == SequenceStatus.ACTIVE

        # Get first question
        question = await sequence_service.get_current_question(mock_user_id)
        assert question is not None
        assert question.key == "confirm_user_name"
        assert question.question_type.value == "boolean"
        assert len(question.options) == 2
        assert question.options[0].value == "true"
        assert question.options[1].value == "false"

    async def test_boolean_question_answer(self, sequence_service, mock_user_id):
        """Test answering boolean question."""
        # Start sequence and answer first question
        sequence_service.start_sequence(mock_user_id, "user_info")

        # Answer with "true" (confirming name)
        result = await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        assert result.success
        assert result.next_question is not None

        # Next question should be gender (skipping preferred_name due to condition)
        assert result.next_question.key == "gender"

    async def test_conditional_question_flow(self, sequence_service, mock_user_id):
        """Test conditional question flow when name is not confirmed."""
        # Start sequence
        sequence_service.start_sequence(mock_user_id, "user_info")

        # Answer with "false" (not confirming name)
        result = await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "false"
        )
        assert result.success
        assert result.next_question is not None

        # Next question should be preferred_name due to condition
        assert result.next_question.key == "preferred_name"

        # Answer preferred_name question
        result = await sequence_service.answer_question(
            mock_user_id, "preferred_name", "John"
        )
        assert result.success
        assert result.next_question is not None

        # Next question should be gender
        assert result.next_question.key == "gender"

    async def test_gender_question_answer(self, sequence_service, mock_user_id):
        """Test answering gender question."""
        # Setup: answer previous questions
        sequence_service.start_sequence(mock_user_id, "user_info")
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )

        # Answer gender question
        result = await sequence_service.answer_question(mock_user_id, "gender", "male")
        assert result.success
        assert result.next_question is not None
        assert result.next_question.key == "birth_date"

    async def test_birth_date_validation(self, sequence_service, mock_user_id):
        """Test birth date validation."""
        # Setup: answer previous questions
        sequence_service.start_sequence(mock_user_id, "user_info")
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        await sequence_service.answer_question(mock_user_id, "gender", "male")

        # Test valid birth date
        result = await sequence_service.answer_question(
            mock_user_id, "birth_date", "15.03.1990"
        )
        assert result.success
        assert result.next_question is not None
        assert result.next_question.key == "eyes_color"

        # Test invalid birth date format
        result = await sequence_service.answer_question(
            mock_user_id, "birth_date", "invalid_date"
        )
        assert not result.success
        assert "Invalid date format" in result.error_message

    async def test_eyes_color_question_answer(self, sequence_service, mock_user_id):
        """Test answering eyes color question."""
        # Setup: answer previous questions
        sequence_service.start_sequence(mock_user_id, "user_info")
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        await sequence_service.answer_question(mock_user_id, "gender", "male")
        await sequence_service.answer_question(mock_user_id, "birth_date", "15.03.1990")

        # Answer eyes color question
        result = await sequence_service.answer_question(
            mock_user_id, "eyes_color", "blue"
        )
        assert result.success
        assert result.next_question is not None
        assert result.next_question.key == "marital_status"

    async def test_marital_status_question_answer(self, sequence_service, mock_user_id):
        """Test answering marital status question."""
        # Setup: answer previous questions
        sequence_service.start_sequence(mock_user_id, "user_info")
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        await sequence_service.answer_question(mock_user_id, "gender", "male")
        await sequence_service.answer_question(mock_user_id, "birth_date", "15.03.1990")
        await sequence_service.answer_question(mock_user_id, "eyes_color", "blue")

        # Answer marital status question
        result = await sequence_service.answer_question(
            mock_user_id, "marital_status", "single"
        )
        assert result.success

        # Sequence should be completed
        assert result.sequence_completed
        assert result.summary is not None

    async def test_complete_sequence_flow(self, sequence_service, mock_user_id):
        """Test complete sequence flow from start to finish."""
        # Start sequence
        session_id = sequence_service.start_sequence(mock_user_id, "user_info")
        assert session_id is not None

        # Get session details
        session = await sequence_service.get_session(mock_user_id)
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
                mock_user_id, question_key, answer
            )
            assert result.success, (
                f"Failed to answer {question_key}: {result.error_message}"
            )

        # Verify sequence completion
        final_session = await sequence_service.get_session(mock_user_id)
        assert final_session.status == SequenceStatus.COMPLETED

        # Verify all answers are recorded
        progress = await sequence_service.get_progress(mock_user_id)
        assert progress is not None
        assert len(progress.answers) == 5

    async def test_sequence_restart(self, sequence_service, mock_user_id):
        """Test restarting a completed sequence."""
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
            await sequence_service.answer_question(mock_user_id, answer_key, answer)

        # Restart sequence
        new_session_id = sequence_service.start_sequence(mock_user_id, "user_info")
        assert new_session_id is not None

        # Get session details
        new_session = await sequence_service.get_session(mock_user_id)
        assert new_session.status == SequenceStatus.ACTIVE

        # Verify we're back to first question
        question = await sequence_service.get_current_question(mock_user_id)
        assert question.key == "confirm_user_name"

    async def test_sequence_progress_tracking(self, sequence_service, mock_user_id):
        """Test that sequence progress is properly tracked."""
        # Start sequence
        sequence_service.start_sequence(mock_user_id, "user_info")

        # Check initial progress
        progress = await sequence_service.get_progress(mock_user_id)
        assert progress.current_question_index == 0
        assert progress.total_questions == 6
        assert progress.completion_percentage == 0.0

        # Answer first question
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )

        # Check updated progress
        progress = await sequence_service.get_progress(mock_user_id)
        assert progress.current_question_index == 1
        assert progress.completion_percentage > 0.0

    async def test_sequence_error_handling(self, sequence_service, mock_user_id):
        """Test sequence error handling for invalid inputs."""
        # Start sequence
        sequence_service.start_sequence(mock_user_id, "user_info")

        # Test invalid answer for boolean question
        result = await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "maybe"
        )
        assert not result.success
        assert result.error_message is not None

        # Test invalid answer for single choice question
        await sequence_service.answer_question(
            mock_user_id, "confirm_user_name", "true"
        )
        result = await sequence_service.answer_question(
            mock_user_id, "gender", "invalid_gender"
        )
        assert not result.success
        assert result.error_message is not None

    async def test_sequence_session_management(self, sequence_service, mock_user_id):
        """Test sequence session management."""
        # Start sequence
        session_id = sequence_service.start_sequence(mock_user_id, "user_info")
        assert session_id is not None

        # Get session details
        session = await sequence_service.get_session(mock_user_id)
        assert session.session_id == session_id
        assert session.user_id == mock_user_id
        assert session.sequence_name == "user_info"

        # Verify session state
        assert session.status == SequenceStatus.ACTIVE
        assert session.start_time is not None
