"""
Questionnaire domain protocol interfaces.

Defines the contracts for questionnaire-specific services and components
following domain-driven design principles.
"""

from typing import Protocol, runtime_checkable, Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from aiogram.types import User, InlineKeyboardMarkup


@dataclass
class QuestionOption:
    """Represents a single answer option for a question."""
    text: str
    value: str


@dataclass
class QuestionData:
    """Enhanced question data structure supporting images and button options."""
    text: str
    image: Optional[str] = None
    question_type: str = "text"  # "text", "buttons"
    options: Optional[List[QuestionOption]] = None
    
    def __post_init__(self):
        """Validate question data after initialization."""
        if self.question_type == "buttons" and not self.options:
            raise ValueError("Button-type questions must have options")
        if self.options:
            self.options = [
                option if isinstance(option, QuestionOption) 
                else QuestionOption(**option) if isinstance(option, dict)
                else QuestionOption(text=str(option), value=str(option))
                for option in self.options
            ]


@runtime_checkable
class SessionManagerProtocol(Protocol):
    """Protocol for session management implementations."""
    
    def create_session(self, user_id: int) -> str:
        """Create a new questionnaire session."""
        ...
    
    def get_session(self, user_id: int) -> Optional[dict]:
        """Get existing session data."""
        ...
    
    def add_answer(self, user_id: int, question_key: str, answer: str) -> bool:
        """Add answer to session."""
        ...
    
    def advance_question(self, user_id: int) -> None:
        """Advance to next question in session."""
        ...
    
    def cancel_session(self, user_id: int) -> bool:
        """Cancel active session."""
        ...
    
    def delete_session(self, user_id: int) -> bool:
        """Delete session data."""
        ...


@runtime_checkable
class QuestionProviderProtocol(Protocol):
    """Protocol for providing questions and managing question flow."""
    
    def get_question_sequence(self, user: User) -> List[str]:
        """Get the sequence of question keys."""
        ...
    
    def get_question_data(self, question_key: str, user: User) -> QuestionData:
        """Get enhanced question data including text, image, and options."""
        ...
    
    def get_question_text(self, question_key: str, user: User) -> str:
        """Get localized question text (backward compatibility)."""
        ...
    
    def create_question_keyboard(self, question_key: str, user: User) -> Optional[InlineKeyboardMarkup]:
        """Create inline keyboard for question options."""
        ...
    
    def validate_answer(self, question_key: str, answer: str, user: User) -> bool:
        """Validate if the answer is valid for the given question."""
        ...
    
    def get_answer_display_text(self, question_key: str, answer: str, user: User) -> str:
        """Get display text for an answer value."""
        ...
    
    def should_ask_additional_question(self, answers: Dict[str, str]) -> bool:
        """Determine if additional questions should be asked."""
        ...
    
    def get_next_question(self, current_answers: Dict[str, str], user: User) -> Optional[str]:
        """Get the next question key based on current answers."""
        ...
    
    def get_progress(self, current_answers: Dict[str, str], user: User) -> Tuple[int, int]:
        """Get progress information for the current questionnaire."""
        ... 