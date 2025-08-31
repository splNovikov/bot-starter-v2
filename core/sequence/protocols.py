"""
Core sequence protocol interfaces.

Defines the contracts for sequence framework components following
domain-driven design and dependency inversion principles.
"""

from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)

from aiogram.types import InlineKeyboardMarkup, Message, User

from .types import SequenceAnswer, SequenceDefinition, SequenceQuestion, SequenceSession


@runtime_checkable
class TranslatorProtocol(Protocol):
    """Protocol for translation services."""

    def translate(
        self, key: str, context: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> str:
        """
        Translate a message key with context.

        Args:
            key: Translation key
            context: Optional context mapping for interpolation
            **kwargs: Additional parameters for interpolation

        Returns:
            Translated and formatted message
        """
        ...


@runtime_checkable
class SequenceManagerProtocol(Protocol):
    """Protocol for sequence session management implementations."""

    def create_session(self, user_id: int, sequence_name: str) -> str:
        """
        Create a new sequence session.

        Args:
            user_id: User identifier
            sequence_name: Name of the sequence to start

        Returns:
            Session ID string
        """
        ...

    def get_session(self, user_id: int) -> Optional[SequenceSession]:
        """
        Get existing session data.

        Args:
            user_id: User identifier

        Returns:
            SequenceSession object or None if no session exists
        """
        ...

    def add_answer(self, user_id: int, answer: SequenceAnswer) -> bool:
        """
        Add answer to session.

        Args:
            user_id: User identifier
            answer: SequenceAnswer object

        Returns:
            True if answer was successfully added
        """
        ...

    def advance_step(self, user_id: int) -> bool:
        """
        Advance to next step in sequence.

        Args:
            user_id: User identifier

        Returns:
            True if advanced successfully
        """
        ...

    def complete_session(self, user_id: int) -> bool:
        """
        Mark session as completed.

        Args:
            user_id: User identifier

        Returns:
            True if marked as completed
        """
        ...

    def abandon_session(self, user_id: int) -> bool:
        """
        Mark session as abandoned.

        Args:
            user_id: User identifier

        Returns:
            True if marked as abandoned
        """
        ...

    def clear_session(self, user_id: int) -> bool:
        """
        Clear/delete session data.

        Args:
            user_id: User identifier

        Returns:
            True if session was cleared
        """
        ...


@runtime_checkable
class SequenceProviderProtocol(Protocol):
    """Protocol for sequence definition providers."""

    def get_sequence_definition(
        self, sequence_name: str
    ) -> Optional[SequenceDefinition]:
        """
        Get sequence definition by name.

        Args:
            sequence_name: Name of the sequence

        Returns:
            SequenceDefinition object or None if not found
        """
        ...

    def get_available_sequences(self) -> List[str]:
        """
        Get list of available sequence names.

        Returns:
            List of sequence names
        """
        ...

    def get_current_question(
        self, sequence_name: str, step: int
    ) -> Optional[SequenceQuestion]:
        """
        Get current question for sequence at given step.

        Args:
            sequence_name: Name of the sequence
            step: Current step index

        Returns:
            SequenceQuestion object or None
        """
        ...

    def get_next_question_key(self, session: SequenceSession) -> Optional[str]:
        """
        Get next question key based on session state and conditional logic.

        Args:
            session: Current sequence session

        Returns:
            Next question key or None if sequence is complete
        """
        ...

    def validate_answer(
        self, sequence_name: str, question_key: str, answer_value: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate answer for a specific question.

        Args:
            sequence_name: Name of the sequence
            question_key: Question identifier
            answer_value: User's answer

        Returns:
            Tuple of (is_valid, error_message)
        """
        ...

    def register_sequence(self, definition: SequenceDefinition) -> None:
        """
        Register a sequence definition.

        Args:
            definition: SequenceDefinition to register
        """
        ...

    def register_sequences(self, definitions: List[SequenceDefinition]) -> None:
        """
        Register multiple sequence definitions.

        Args:
            definitions: List of SequenceDefinition objects to register
        """
        ...

    def unregister_sequence(self, sequence_name: str) -> bool:
        """
        Unregister a sequence definition.

        Args:
            sequence_name: Name of the sequence to unregister

        Returns:
            True if sequence was unregistered, False if not found
        """
        ...

    def should_show_question(
        self, question: SequenceQuestion, session: SequenceSession
    ) -> bool:
        """
        Check if a question should be shown based on conditions.

        Args:
            question: Question to check
            session: Current session

        Returns:
            True if question should be shown, False otherwise
        """
        ...


@runtime_checkable
class SequenceServiceProtocol(Protocol):
    """Protocol for main sequence orchestration service."""

    def start_sequence(self, user_id: int, sequence_name: str) -> str:
        """
        Start a new sequence session.

        Args:
            user_id: User identifier
            sequence_name: Name of the sequence to start

        Returns:
            Session ID
        """
        ...

    def get_session(self, user_id: int) -> Optional[SequenceSession]:
        """
        Get current session for user.

        Args:
            user_id: User identifier

        Returns:
            SequenceSession object or None
        """
        ...

    def process_answer(
        self, user_id: int, answer_text: str, user: User
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process user's answer to current question.

        Args:
            user_id: User identifier
            answer_text: User's answer text
            user: User object

        Returns:
            Tuple of (success, error_message, next_question_key)
        """
        ...

    async def send_question(
        self,
        message: Message,
        question_key: str,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        user_id: Optional[int] = None,
    ) -> bool:
        """
        Send question to user via platform.

        Args:
            message: Message object for reply
            question_key: Question identifier
            translator: Translation service
            context: Optional context for localization
            show_progress: Whether to show progress indicator
            user_id: Optional user ID (if not provided, uses message.from_user.id)

        Returns:
            True if question was sent successfully
        """
        ...

    async def edit_question(
        self,
        message: Message,
        question_key: str,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        user_id: Optional[int] = None,
    ) -> bool:
        """
        Edit existing message with new question (for callback queries).

        Args:
            message: Message object to edit
            question_key: Question identifier
            translator: Translation service
            context: Optional context for localization
            show_progress: Whether to show progress indicator
            user_id: Optional user ID (if not provided, uses message.from_user.id)

        Returns:
            True if question was edited successfully
        """
        ...

    async def send_completion_message(
        self,
        message: Message,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        """
        Send completion message and summary.

        Args:
            message: Message object for reply
            session: Completed session
            translator: Translation service
            context: Optional context for localization

        Returns:
            True if message was sent successfully
        """
        ...

    def get_current_question_key(self, user_id: int) -> Optional[str]:
        """
        Get current question key for user's active session.

        Args:
            user_id: User identifier

        Returns:
            Current question key or None
        """
        ...

    def is_sequence_complete(self, user_id: int) -> bool:
        """
        Check if user's current sequence is complete.

        Args:
            user_id: User identifier

        Returns:
            True if sequence is complete
        """
        ...

    def get_sequence_progress(self, user_id: int) -> Tuple[int, int]:
        """
        Get sequence progress for user.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (current_step, total_steps)
        """
        ...


@runtime_checkable
class SequenceResultHandlerProtocol(Protocol):
    """Protocol for handling sequence completion results."""

    async def handle_sequence_completion(
        self, session: SequenceSession, user: User
    ) -> Optional[Dict[str, Any]]:
        """
        Handle sequence completion with custom logic.

        Args:
            session: Completed sequence session
            user: User object

        Returns:
            Optional result data
        """
        ...


@runtime_checkable
class SequenceQuestionRendererProtocol(Protocol):
    """Protocol for rendering sequence questions in different formats."""

    async def render_question(
        self,
        question: SequenceQuestion,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        visible_questions_count: Optional[int] = None,
    ) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """
        Render question text and keyboard.

        Args:
            question: SequenceQuestion to render
            session: Current session for context
            translator: Translation service
            context: Optional context for localization
            show_progress: Whether to include progress indicator
            visible_questions_count: Number of visible questions for progress calculation

        Returns:
            Tuple of (message_text, keyboard_markup)
        """
        ...

    async def render_completion_message(
        self,
        session: SequenceSession,
        sequence_definition: SequenceDefinition,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        Render sequence completion message.

        Args:
            session: Completed session
            sequence_definition: Sequence definition
            translator: Translation service
            context: Optional context for localization

        Returns:
            Formatted completion message
        """
        ...

    async def send_question_message(
        self,
        message: Message,
        question_text: str,
        keyboard: Optional[InlineKeyboardMarkup] = None,
        edit_existing: bool = False,
    ) -> bool:
        """
        Send or edit a question message with platform-specific formatting.

        Args:
            message: Platform message object
            question_text: Text of the question
            keyboard: Optional keyboard markup
            edit_existing: Whether to edit existing message or send new one

        Returns:
            True if message was sent/edited successfully
        """
        ...

    async def send_completion_message(
        self,
        message: Message,
        completion_text: str,
    ) -> bool:
        """
        Send completion message with platform-specific formatting.

        Args:
            message: Platform message object
            completion_text: Completion message text

        Returns:
            True if message was sent successfully
        """
        ...


# Service protocols for refactored sequence services


@runtime_checkable
class SequenceSessionServiceProtocol(Protocol):
    """Protocol for sequence session management."""

    def start_session(self, user_id: int, sequence_name: str) -> str:
        """Start a new sequence session."""
        ...

    def get_session(self, user_id: int) -> Optional[SequenceSession]:
        """Get current session for user."""
        ...


@runtime_checkable
class SequenceQuestionServiceProtocol(Protocol):
    """Protocol for sequence question handling."""

    async def send_question(
        self,
        message: Message,
        question: "SequenceQuestion",
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
        show_progress: bool = True,
        visible_questions_count: Optional[int] = None,
    ) -> bool:
        """Send question to user via platform."""
        ...


@runtime_checkable
class SequenceProgressServiceProtocol(Protocol):
    """Protocol for sequence progress tracking."""

    def get_progress(self, session: SequenceSession) -> Tuple[int, int]:
        """Get sequence progress for session."""
        ...


@runtime_checkable
class SequenceCompletionServiceProtocol(Protocol):
    """Protocol for sequence completion handling."""

    async def send_completion_message(
        self,
        message: Message,
        session: SequenceSession,
        translator: TranslatorProtocol,
        context: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        """Send completion message and summary."""
        ...


__all__ = [
    "TranslatorProtocol",
    "SequenceManagerProtocol",
    "SequenceProviderProtocol",
    "SequenceServiceProtocol",
    "SequenceResultHandlerProtocol",
    "SequenceQuestionRendererProtocol",
    # Refactored service protocols
    "SequenceSessionServiceProtocol",
    "SequenceQuestionServiceProtocol",
    "SequenceProgressServiceProtocol",
    "SequenceCompletionServiceProtocol",
]
