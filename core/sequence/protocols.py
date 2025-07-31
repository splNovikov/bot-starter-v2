"""
Core sequence protocol interfaces.

Defines the contracts for sequence framework components following
domain-driven design and dependency inversion principles.
"""

from typing import Protocol, runtime_checkable, Optional, List, Dict, Any, Tuple
from aiogram.types import User, Message, InlineKeyboardMarkup

from .types import (
    SequenceSession, 
    SequenceDefinition, 
    SequenceQuestion, 
    SequenceAnswer
)


@runtime_checkable
class SequenceManagerProtocol(Protocol):
    """Protocol for sequence session management implementations."""
    
    def create_session(
        self, 
        user_id: int, 
        sequence_name: str
    ) -> str:
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
    
    def add_answer(
        self, 
        user_id: int, 
        answer: SequenceAnswer
    ) -> bool:
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
    
    def get_sequence_definition(self, sequence_name: str) -> Optional[SequenceDefinition]:
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
        ...
    
    def get_next_question_key(
        self, 
        session: SequenceSession, 
        user: User
    ) -> Optional[str]:
        """
        Get next question key based on session state and conditional logic.
        
        Args:
            session: Current sequence session
            user: User object for personalization
            
        Returns:
            Next question key or None if sequence is complete
        """
        ...
    
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


@runtime_checkable
class SequenceServiceProtocol(Protocol):
    """Protocol for main sequence orchestration service."""
    
    def start_sequence(
        self, 
        user_id: int, 
        sequence_name: str
    ) -> str:
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
        self, 
        user_id: int, 
        answer_text: str, 
        user: User
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
        user: User, 
        show_progress: bool = True
    ) -> bool:
        """
        Send question to user via Telegram.
        
        Args:
            message: Message object for reply
            question_key: Question identifier
            user: User object
            show_progress: Whether to show progress indicator
            
        Returns:
            True if question was sent successfully
        """
        ...
    
    async def send_completion_message(
        self, 
        message: Message, 
        session: SequenceSession, 
        user: User
    ) -> bool:
        """
        Send completion message and summary.
        
        Args:
            message: Message object for reply
            session: Completed session
            user: User object
            
        Returns:
            True if message was sent successfully
        """
        ...
    
    def get_current_question_key(self, user_id: int, user: User) -> Optional[str]:
        """
        Get current question key for user's active session.
        
        Args:
            user_id: User identifier
            user: User object
            
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
        self, 
        session: SequenceSession, 
        user: User
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
        show_progress: bool = True,
        user: Optional[User] = None
    ) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """
        Render question text and keyboard.
        
        Args:
            question: SequenceQuestion to render
            session: Current session for context
            show_progress: Whether to include progress indicator
            user: User object for localization context
            
        Returns:
            Tuple of (message_text, keyboard_markup)
        """
        ...
    
    async def render_completion_message(
        self, 
        session: SequenceSession, 
        sequence_definition: SequenceDefinition,
        user: Optional[User] = None
    ) -> str:
        """
        Render sequence completion message.
        
        Args:
            session: Completed session
            sequence_definition: Sequence definition
            user: User object for localization context
            
        Returns:
            Formatted completion message
        """
        ...


__all__ = [
    'SequenceManagerProtocol',
    'SequenceProviderProtocol', 
    'SequenceServiceProtocol',
    'SequenceResultHandlerProtocol',
    'SequenceQuestionRendererProtocol'
] 