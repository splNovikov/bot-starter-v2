"""
In-memory sequence provider implementation.

Provides concrete sequence definitions for user info sequences.
"""

from typing import Optional, List, Dict, Tuple
from aiogram.types import User

from core.sequence.protocols import SequenceProviderProtocol
from core.sequence.types import (
    SequenceDefinition, 
    SequenceQuestion, 
    SequenceSession, 
    SequenceOption,
    QuestionType
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
    
    def __init__(self):
        """Initialize the sequence provider with predefined sequences."""
        self._sequences: Dict[str, SequenceDefinition] = {}
        self._initialize_sequences()
    
    def get_sequence_definition(self, sequence_name: str) -> Optional[SequenceDefinition]:
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
        self, 
        sequence_name: str, 
        step: int
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
    
    def get_next_question_key(
        self, 
        session: SequenceSession, 
        user: User
    ) -> Optional[str]:
        """
        Get next question key based on session state.
        
        Args:
            session: Current sequence session
            user: User object for personalization
            
        Returns:
            Next question key or None if sequence is complete
        """
        sequence = self.get_sequence_definition(session.sequence_name)
        if not sequence:
            return None
        
        # Check if we've answered all questions
        if session.current_step >= len(sequence.questions):
            return None
        
        # Return the current question key (since we advance step after answering)
        current_question = sequence.questions[session.current_step]
        return current_question.key
    
    def validate_answer(
        self, 
        sequence_name: str, 
        question_key: str, 
        answer_value: str
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
                return False, f"Please select one of the available options: {', '.join(valid_values)}"
        
        # For required questions, ensure answer is not empty
        if question.is_required and not answer_value.strip():
            return False, "This question is required. Please provide an answer."
        
        return True, None
    
    def _initialize_sequences(self) -> None:
        """Initialize predefined sequences."""
        self._sequences.update({
            "user_info": self._create_user_info_sequence()
        })
        logger.info(f"Initialized {len(self._sequences)} sequences: {list(self._sequences.keys())}")
    
    def _create_user_info_sequence(self) -> SequenceDefinition:
        """Create user info sequence with eyes color and marital status."""
        questions = [
            SequenceQuestion(
                key="eyes_color",
                question_text_key="sequence.user_info.eyes_color.question",
                question_type=QuestionType.SINGLE_CHOICE,
                options=[
                    SequenceOption(value="brown", label_key="sequence.user_info.eyes_color.brown", emoji="👁️"),
                    SequenceOption(value="blue", label_key="sequence.user_info.eyes_color.blue", emoji="👁️"),
                    SequenceOption(value="green", label_key="sequence.user_info.eyes_color.green", emoji="👁️"),
                    SequenceOption(value="hazel", label_key="sequence.user_info.eyes_color.hazel", emoji="👁️"),
                    SequenceOption(value="gray", label_key="sequence.user_info.eyes_color.gray", emoji="👁️"),
                    SequenceOption(value="other", label_key="sequence.user_info.eyes_color.other", emoji="👁️")
                ],
                is_required=True
            ),
            SequenceQuestion(
                key="marital_status",
                question_text_key="sequence.user_info.marital_status.question",
                question_type=QuestionType.SINGLE_CHOICE,
                options=[
                    SequenceOption(value="single", label_key="sequence.user_info.marital_status.single", emoji="💚"),
                    SequenceOption(value="married", label_key="sequence.user_info.marital_status.married", emoji="💍"),
                    SequenceOption(value="divorced", label_key="sequence.user_info.marital_status.divorced", emoji="💔"),
                    SequenceOption(value="widowed", label_key="sequence.user_info.marital_status.widowed", emoji="🕊️"),
                    SequenceOption(value="prefer_not_to_say", label_key="sequence.user_info.marital_status.prefer_not_to_say", emoji="🤐")
                ],
                is_required=True
            )
        ]
        
        return SequenceDefinition(
            name="user_info",
            questions=questions,
            title_key="sequence.user_info.title",
            description_key="sequence.user_info.description",
            welcome_message_key="sequence.user_info.welcome",
            completion_message_key="sequence.user_info.completion",
            show_progress=True,
            allow_restart=True,
            generate_summary=True
        )


__all__ = ['InMemorySequenceProvider'] 
