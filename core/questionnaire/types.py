"""
Type definitions for the core questionnaire framework.

Provides data structures, enums, and type aliases for type-safe 
questionnaire functionality.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict


class QuestionType(Enum):
    """Enumeration of different question types."""
    TEXT = "text"                    # Free text input
    BUTTONS = "buttons"              # Multiple choice with buttons
    MULTIPLE_CHOICE = "multiple_choice"  # Multiple choice (single selection)
    MULTIPLE_SELECT = "multiple_select"  # Multiple choice (multiple selections)
    SCALE = "scale"                  # Rating scale (1-5, 1-10, etc.)
    YES_NO = "yes_no"               # Boolean yes/no question
    DATE = "date"                   # Date input
    NUMBER = "number"               # Numeric input
    EMAIL = "email"                 # Email validation
    PHONE = "phone"                 # Phone number validation


@dataclass
class QuestionOption:
    """Represents a single answer option for a question."""
    text: str                        # Display text for the option
    value: str                       # Value to store when selected
    description: Optional[str] = None # Optional detailed description
    emoji: Optional[str] = None      # Optional emoji for the option
    
    def __post_init__(self):
        """Validate option data after initialization."""
        if not self.text.strip():
            raise ValueError("Option text cannot be empty")
        if not self.value.strip():
            raise ValueError("Option value cannot be empty")


@dataclass 
class QuestionData:
    """Enhanced question data structure supporting various question types."""
    text: str                                    # Question text
    question_type: QuestionType = QuestionType.TEXT  # Type of question
    image: Optional[str] = None                  # Optional image URL/path
    options: Optional[List[QuestionOption]] = None    # Answer options
    validation: Optional[Dict[str, Any]] = None  # Validation rules
    metadata: Optional[Dict[str, Any]] = None    # Additional metadata
    required: bool = True                        # Whether question is required
    
    def __post_init__(self):
        """Validate question data after initialization."""
        if not self.text.strip():
            raise ValueError("Question text cannot be empty")
            
        # Convert string question_type to enum if needed
        if isinstance(self.question_type, str):
            self.question_type = QuestionType(self.question_type)
            
        # Validate that button-type questions have options
        if self.question_type in [QuestionType.BUTTONS, QuestionType.MULTIPLE_CHOICE, 
                                 QuestionType.MULTIPLE_SELECT] and not self.options:
            raise ValueError(f"{self.question_type.value} questions must have options")
            
        # Convert dict options to QuestionOption objects
        if self.options:
            self.options = [
                option if isinstance(option, QuestionOption) 
                else QuestionOption(**option) if isinstance(option, dict)
                else QuestionOption(text=str(option), value=str(option))
                for option in self.options
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question data to dictionary."""
        data = asdict(self)
        data['question_type'] = self.question_type.value
        return data


@dataclass
class QuestionnaireSession:
    """Active questionnaire session data with enhanced functionality."""
    session_id: str                              # Unique session identifier
    user_id: int                                # User identifier
    current_question: int                       # Current question index
    answers: Dict[str, str]                     # Question key -> answer mapping
    metadata: Optional[Dict[str, Any]] = None   # Session metadata
    started_at: Optional[float] = None          # Session start timestamp
    updated_at: Optional[float] = None          # Last update timestamp
    is_complete: bool = False                   # Whether questionnaire is complete
    
    def __post_init__(self):
        """Initialize session with default values.""" 
        if not self.answers:
            self.answers = {}
        if not self.metadata:
            self.metadata = {}
        
        # Set timestamps if not provided
        import time
        current_time = time.time()
        if self.started_at is None:
            self.started_at = current_time
        if self.updated_at is None:
            self.updated_at = current_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return asdict(self)
    
    def add_answer(self, question_key: str, answer: str) -> None:
        """
        Add an answer to the session.
        
        Args:
            question_key: Question identifier
            answer: User's answer
        """
        self.answers[question_key] = answer
        import time
        self.updated_at = time.time()
    
    def get_answer(self, question_key: str) -> Optional[str]:
        """
        Get an answer from the session.
        
        Args:
            question_key: Question identifier
            
        Returns:
            Answer string or None if not found
        """
        return self.answers.get(question_key)
    
    def has_answer(self, question_key: str) -> bool:
        """
        Check if session has answer for question.
        
        Args:
            question_key: Question identifier
            
        Returns:
            True if answer exists
        """
        return question_key in self.answers
    
    def get_progress(self, total_questions: int) -> tuple[int, int]:
        """
        Get progress information.
        
        Args:
            total_questions: Total number of questions
            
        Returns:
            Tuple of (answered_questions, total_questions)
        """
        answered = len(self.answers)
        return answered, total_questions


@dataclass
class QuestionnaireConfig:
    """Configuration for questionnaire behavior."""
    name: str                                   # Questionnaire name/identifier
    description: Optional[str] = None           # Description of questionnaire
    version: str = "1.0.0"                    # Version string
    allow_restart: bool = True                  # Allow users to restart
    show_progress: bool = True                  # Show progress indicators
    save_partial: bool = True                   # Save partial responses
    timeout_minutes: Optional[int] = None       # Session timeout
    max_retries: int = 3                       # Maximum retry attempts
    shuffle_questions: bool = False             # Randomize question order
    shuffle_options: bool = False               # Randomize option order
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)


# Type aliases for better readability
QuestionKey = str
AnswerValue = str
SessionID = str
UserID = int
QuestionSequence = List[QuestionKey]
AnswerDict = Dict[QuestionKey, AnswerValue]

# Re-export HandlerCategory from core handlers for convenience
from ..handlers.types import HandlerCategory

__all__ = [
    # Enums
    'QuestionType',
    'HandlerCategory',
    
    # Data classes
    'QuestionOption',
    'QuestionData', 
    'QuestionnaireSession',
    'QuestionnaireConfig',
    
    # Type aliases
    'QuestionKey',
    'AnswerValue',
    'SessionID',
    'UserID',
    'QuestionSequence',
    'AnswerDict'
] 