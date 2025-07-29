"""
Core questionnaire protocol interfaces.

Defines the contracts for questionnaire framework components following
domain-driven design and dependency inversion principles.
"""

from typing import Protocol, runtime_checkable, Optional, List, Dict, Any, Tuple
from aiogram.types import User, InlineKeyboardMarkup

from .types import QuestionData, QuestionnaireSession


@runtime_checkable
class SessionManagerProtocol(Protocol):
    """Protocol for questionnaire session management implementations."""
    
    def create_session(self, user_id: int) -> str:
        """
        Create a new questionnaire session.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session ID string
        """
        ...
    
    def get_session(self, user_id: int) -> Optional[dict]:
        """
        Get existing session data.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session data dictionary or None if no session exists
        """
        ...
    
    def get_session_object(self, user_id: int) -> Optional[QuestionnaireSession]:
        """
        Get session as typed object.
        
        Args:
            user_id: User identifier
            
        Returns:
            QuestionnaireSession object or None if no session exists
        """
        ...
    
    def add_answer(self, user_id: int, question_key: str, answer: str) -> bool:
        """
        Add answer to session.
        
        Args:
            user_id: User identifier
            question_key: Question identifier
            answer: User's answer
            
        Returns:
            True if answer was successfully added
        """
        ...
    
    def advance_question(self, user_id: int) -> None:
        """
        Advance to next question in session.
        
        Args:
            user_id: User identifier
        """
        ...
    
    def cancel_session(self, user_id: int) -> bool:
        """
        Cancel active session.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if session was successfully cancelled
        """
        ...
    
    def delete_session(self, user_id: int) -> bool:
        """
        Delete session data.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if session was successfully deleted
        """
        ...


@runtime_checkable
class QuestionProviderProtocol(Protocol):
    """Protocol for providing questions and managing question flow."""
    
    def get_question_sequence(self, user: User) -> List[str]:
        """
        Get the sequence of question keys for a user.
        
        Args:
            user: User object for personalization
            
        Returns:
            List of question keys in order
        """
        ...
    
    def get_question_data(self, question_key: str, user: User) -> QuestionData:
        """
        Get enhanced question data including text, image, and options.
        
        Args:
            question_key: Question identifier
            user: User object for localization
            
        Returns:
            QuestionData object with question details
        """
        ...
    
    def get_question_text(self, question_key: str, user: User) -> str:
        """
        Get localized question text (backward compatibility).
        
        Args:
            question_key: Question identifier
            user: User object for localization
            
        Returns:
            Localized question text
        """
        ...
    
    def create_question_keyboard(self, question_key: str, user: User) -> Optional[InlineKeyboardMarkup]:
        """
        Create inline keyboard for question options.
        
        Args:
            question_key: Question identifier
            user: User object for localization
            
        Returns:
            InlineKeyboardMarkup if question has options, None otherwise
        """
        ...
    
    def validate_answer(self, question_key: str, answer: str, user: User) -> bool:
        """
        Validate if the answer is valid for the given question.
        
        Args:
            question_key: Question identifier
            answer: User's answer
            user: User object for context
            
        Returns:
            True if answer is valid
        """
        ...
    
    def get_answer_display_text(self, question_key: str, answer: str, user: User) -> str:
        """
        Get display text for an answer value.
        
        Args:
            question_key: Question identifier
            answer: Answer value
            user: User object for localization
            
        Returns:
            Human-readable answer text
        """
        ...
    
    def should_ask_additional_question(self, answers: Dict[str, str]) -> bool:
        """
        Determine if additional questions should be asked based on answers.
        
        Args:
            answers: Dictionary of current answers
            
        Returns:
            True if additional question should be asked
        """
        ...
    
    def get_next_question(self, current_answers: Dict[str, str], user: User) -> Optional[str]:
        """
        Get the next question key based on current answers.
        
        Args:
            current_answers: Dictionary of answers so far
            user: User object for personalization
            
        Returns:
            Next question key or None if questionnaire is complete
        """
        ...
    
    def get_progress(self, current_answers: Dict[str, str], user: User) -> Tuple[int, int]:
        """
        Get progress information for the current questionnaire.
        
        Args:
            current_answers: Dictionary of answers so far
            user: User object for personalization
            
        Returns:
            Tuple of (current_question_number, total_questions)
        """
        ...


@runtime_checkable
class QuestionnaireServiceProtocol(Protocol):
    """Protocol for questionnaire orchestration service."""
    
    def start_questionnaire(self, user_id: int) -> str:
        """
        Start a new questionnaire session.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session ID
        """
        ...
    
    def get_session(self, user_id: int) -> Optional[dict]:
        """
        Get active questionnaire session for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Active session data or None if no session exists
        """
        ...
    
    def get_current_question_key(self, user_id: int, user: User) -> Optional[str]:
        """
        Get the current question key for the user's session.
        
        Args:
            user_id: User identifier
            user: User object
            
        Returns:
            Current question key or None if questionnaire is complete
        """
        ...
    
    async def send_question(
        self, 
        message: Any, 
        question_key: str, 
        user: User,
        show_progress: bool = True
    ) -> bool:
        """
        Send a question to the user with appropriate formatting.
        
        Args:
            message: Message object to reply to
            question_key: Question identifier
            user: User object
            show_progress: Whether to include progress information
            
        Returns:
            True if question was sent successfully
        """
        ...
    
    async def submit_answer(
        self, 
        user_id: int, 
        answer: str, 
        user: User
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Submit answer for current question and advance session.
        
        Args:
            user_id: User identifier
            answer: User's answer
            user: User object for localization
            
        Returns:
            Tuple of (success, next_question_key, error_message)
        """
        ...
    
    def cancel_session(self, user_id: int) -> None:
        """
        Cancel active questionnaire session.
        
        Args:
            user_id: User identifier
        """
        ...
    
    def get_progress_text(self, user_id: int, user: User) -> str:
        """
        Get progress text for current session.
        
        Args:
            user_id: User identifier
            user: User object for localization
            
        Returns:
            Localized progress text
        """
        ... 