"""
In-memory sequence provider implementation.

Provides concrete sequence definitions for user info sequences.
"""

from typing import Dict, List, Optional, Tuple

from core.sequence.protocols import SequenceProviderProtocol
from core.sequence.services.condition_evaluator import condition_evaluator
from core.sequence.types import (
    QuestionType,
    SequenceDefinition,
    SequenceQuestion,
    SequenceSession,
)
from core.utils.logger import get_logger

logger = get_logger()


class InMemorySequenceProvider(SequenceProviderProtocol):
    """
    In-memory sequence provider implementation.

    Provides sequence definitions for user info sequences
    with button-based questions and custom completion messages.
    Supports localization for all text content.
    """

    def __init__(self, sequence_definitions: Optional[List[SequenceDefinition]] = None):
        """
        Initialize the sequence provider with predefined sequences.

        Args:
            sequence_definitions: List of sequence definitions to register
        """
        self._sequences: Dict[str, SequenceDefinition] = {}
        if sequence_definitions:
            self._register_sequences(sequence_definitions)
        logger.info(
            f"Initialized sequence provider with {len(self._sequences)} sequences: {list(self._sequences.keys())}"
        )

    def register_sequence(self, sequence_definition: SequenceDefinition) -> None:
        """
        Register a sequence definition.

        Args:
            sequence_definition: SequenceDefinition to register
        """
        self._sequences[sequence_definition.name] = sequence_definition
        logger.info(f"Registered sequence: {sequence_definition.name}")

    def register_sequences(
        self, sequence_definitions: List[SequenceDefinition]
    ) -> None:
        """
        Register multiple sequence definitions.

        Args:
            sequence_definitions: List of SequenceDefinition objects to register
        """
        self._register_sequences(sequence_definitions)

    def unregister_sequence(self, sequence_name: str) -> bool:
        """
        Unregister a sequence definition.

        Args:
            sequence_name: Name of the sequence to unregister

        Returns:
            True if sequence was unregistered, False if not found
        """
        if sequence_name in self._sequences:
            del self._sequences[sequence_name]
            logger.info(f"Unregistered sequence: {sequence_name}")
            return True
        return False

    def _register_sequences(
        self, sequence_definitions: List[SequenceDefinition]
    ) -> None:
        """
        Register multiple sequence definitions internally.

        Args:
            sequence_definitions: List of SequenceDefinition objects to register
        """
        for sequence_def in sequence_definitions:
            self.register_sequence(sequence_def)

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
        return self._sequences.get(sequence_name)

    def get_available_sequences(self) -> List[str]:
        """
        Get list of available sequence names.

        Returns:
            List of sequence names
        """
        return list(self._sequences.keys())

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
        sequence = self.get_sequence_definition(sequence_name)
        if not sequence or step >= len(sequence.questions):
            return None

        return sequence.questions[step]

    def get_next_question_key(self, session: SequenceSession) -> Optional[str]:
        """
        Get next question key based on session state.

        Args:
            session: Current sequence session

        Returns:
            Next question key or None if sequence is complete
        """
        sequence = self.get_sequence_definition(session.sequence_name)
        if not sequence:
            return None

        # Check if we've answered all questions
        if session.current_step >= len(sequence.questions):
            return None

        # Find the next question that should be shown based on conditions
        next_question_key = self._find_next_visible_question(session, sequence)
        return next_question_key

    def _find_next_visible_question(
        self, session: SequenceSession, sequence: SequenceDefinition
    ) -> Optional[str]:
        """
        Find the next question that should be shown based on conditions.

        Args:
            session: Current sequence session
            sequence: Sequence definition

        Returns:
            Next question key or None if no more questions
        """
        # Start from current step and look for the next visible question
        for i in range(session.current_step, len(sequence.questions)):
            question = sequence.questions[i]

            # Check if this question should be shown
            if condition_evaluator.should_show_question(question, session):
                # Check if this question has already been answered
                if not session.has_answer_for_question(question.key):
                    return question.key

        # No more visible questions
        return None

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
        sequence = self.get_sequence_definition(sequence_name)
        if not sequence:
            return False, "Sequence not found"

        question = sequence.get_question_by_key(question_key)
        if not question:
            return False, "Question not found"

        # For choice questions, validate against available options
        if question.question_type == QuestionType.SINGLE_CHOICE and question.options:
            valid_values = [option.value for option in question.options]
            if answer_value not in valid_values:
                return (
                    False,
                    f"Please select one of the available options: {', '.join(valid_values)}",
                )

        # For required questions, ensure answer is not empty
        if question.is_required and not answer_value.strip():
            return False, "This question is required. Please provide an answer."

        return True, None

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
        return condition_evaluator.should_show_question(question, session)
