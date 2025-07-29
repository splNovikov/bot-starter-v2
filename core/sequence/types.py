"""
Core sequence framework types and data structures.

Defines the fundamental types for the sequence abstraction that unifies
all interactive flows under a single "sequence" concept with configuration-driven behavior.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Union
from enum import Enum
import time


class SequenceStatus(Enum):
    """Status of a sequence session."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    PAUSED = "paused"


class QuestionType(Enum):
    """Types of questions within sequences."""
    TEXT = "text"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    BOOLEAN = "boolean"
    NUMERIC = "numeric"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    FILE = "file"
    RATING = "rating"


@dataclass
class SequenceOption:
    """Option for choice-based questions."""
    value: str
    label: str
    description: Optional[str] = None
    emoji: Optional[str] = None
    is_correct: Optional[bool] = None  # For scored sequences


@dataclass
class SequenceQuestion:
    """Individual question within a sequence."""
    key: str
    question_text: str
    question_type: QuestionType
    options: Optional[List[SequenceOption]] = None
    is_required: bool = True
    validation_regex: Optional[str] = None
    error_message: Optional[str] = None
    help_text: Optional[str] = None
    image_url: Optional[str] = None
    
    # Conditional logic
    show_if: Optional[Dict[str, Any]] = None
    skip_if: Optional[Dict[str, Any]] = None
    
    # Scoring (when sequence is scored)
    correct_answer: Optional[Union[str, List[str]]] = None
    points: Optional[int] = None
    explanation: Optional[str] = None
    time_limit: Optional[int] = None  # seconds


@dataclass
class SequenceAnswer:
    """User's answer to a sequence question."""
    question_key: str
    answer_value: Union[str, List[str]]
    answered_at: float = field(default_factory=time.time)
    
    # Scoring fields (when sequence is scored)
    is_correct: Optional[bool] = None
    points_earned: Optional[int] = None
    time_taken: Optional[float] = None  # seconds


@dataclass
class SequenceSession:
    """Active sequence session data."""
    session_id: str
    user_id: int
    sequence_name: str
    current_step: int = 0
    answers: Dict[str, SequenceAnswer] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: SequenceStatus = SequenceStatus.ACTIVE
    started_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    
    # Scoring fields (when sequence is scored)
    total_score: Optional[int] = None
    max_possible_score: Optional[int] = None
    
    # Progress tracking
    total_questions: Optional[int] = None
    questions_answered: int = 0
    
    def __post_init__(self):
        """Initialize session with default values."""
        if not self.answers:
            self.answers = {}
        if not self.metadata:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return asdict(self)
    
    def add_answer(self, answer: SequenceAnswer) -> None:
        """
        Add an answer to the session.
        
        Args:
            answer: SequenceAnswer object
        """
        self.answers[answer.question_key] = answer
        self.questions_answered = len(self.answers)
        self.updated_at = time.time()
        
        # Update score if sequence is scored and answer has points
        if answer.points_earned is not None:
            if self.total_score is None:
                self.total_score = 0
            self.total_score += answer.points_earned
    
    def get_answer(self, question_key: str) -> Optional[SequenceAnswer]:
        """
        Get an answer from the session.
        
        Args:
            question_key: Question identifier
            
        Returns:
            SequenceAnswer object or None if not found
        """
        return self.answers.get(question_key)
    
    def get_progress_percentage(self) -> float:
        """
        Get completion progress as percentage.
        
        Returns:
            Progress percentage (0-100)
        """
        if not self.total_questions or self.total_questions == 0:
            return 0.0
        return (self.questions_answered / self.total_questions) * 100
    
    def is_complete(self) -> bool:
        """Check if sequence is complete."""
        return self.status == SequenceStatus.COMPLETED
    
    def mark_completed(self) -> None:
        """Mark sequence as completed."""
        self.status = SequenceStatus.COMPLETED
        self.completed_at = time.time()
        self.updated_at = time.time()


@dataclass
class SequenceDefinition:
    """
    Definition of a sequence structure with behavior configuration.
    
    All behavior differences (scoring, anonymity, progress, etc.) are handled
    through configuration flags rather than separate types.
    """
    name: str
    questions: List[SequenceQuestion]
    
    # Basic properties
    title: Optional[str] = None
    description: Optional[str] = None
    welcome_message: Optional[str] = None
    completion_message: Optional[str] = None
    
    # Behavior configuration flags
    scored: bool = False  # Enable scoring (makes it "quiz-like")
    anonymous: bool = False  # Anonymous responses (makes it "survey-like")
    show_progress: bool = True  # Show progress indicator
    allow_restart: bool = True  # Allow restarting the sequence
    allow_skip: bool = False  # Allow skipping questions
    randomize_questions: bool = False  # Randomize question order
    generate_summary: bool = False  # Generate AI summary (for single Q+summary)
    
    # Scoring configuration (when scored=True)
    time_limit: Optional[int] = None  # minutes
    passing_score: Optional[int] = None
    show_correct_answers: bool = True
    immediate_feedback: bool = False  # Show feedback after each question
    
    def get_question_by_key(self, question_key: str) -> Optional[SequenceQuestion]:
        """Get question by key."""
        for question in self.questions:
            if question.key == question_key:
                return question
        return None
    
    def get_total_possible_score(self) -> int:
        """Get total possible score (when scored=True)."""
        if not self.scored:
            return 0
        return sum(q.points or 0 for q in self.questions)
    
    def is_single_question(self) -> bool:
        """Check if this is a single question sequence."""
        return len(self.questions) == 1
    
    def is_quiz_like(self) -> bool:
        """Check if this sequence behaves like a quiz."""
        return self.scored
    
    def is_survey_like(self) -> bool:
        """Check if this sequence behaves like a survey."""
        return self.anonymous
    
    def is_single_question_summary(self) -> bool:
        """Check if this is a single question with summary."""
        return self.is_single_question() and self.generate_summary


# Handler category for backward compatibility
from core.handlers.types import HandlerCategory

__all__ = [
    'SequenceStatus', 
    'QuestionType',
    'SequenceOption',
    'SequenceQuestion',
    'SequenceAnswer',
    'SequenceSession',
    'SequenceDefinition',
    'HandlerCategory'
] 