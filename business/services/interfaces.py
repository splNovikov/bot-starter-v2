"""
Service interfaces for dependency inversion and better testability.

Defines protocols that services must implement, enabling dependency injection
and easier unit testing through mocking.
"""

from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable
from dataclasses import dataclass
from aiogram.types import User


@dataclass
class ApiResponse:
    """Response from API call."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    status_code: Optional[int] = None


@runtime_checkable
class ApiClientProtocol(Protocol):
    """Protocol for API client implementations."""
    
    async def submit_questionnaire_answer(
        self, 
        user_id: int, 
        question_key: str, 
        answer: str,
        session_id: Optional[str] = None
    ) -> ApiResponse:
        """Submit a questionnaire answer to the API."""
        ...
    
    async def submit_gender(self, user_id: int, gender: str) -> ApiResponse:
        """Submit gender information to the API."""
        ...
    
    async def complete_questionnaire(
        self, 
        user_id: int, 
        session_id: Optional[str] = None
    ) -> ApiResponse:
        """Mark questionnaire as completed."""
        ...
    
    async def close(self) -> None:
        """Close the API client and cleanup resources."""
        ...


@runtime_checkable  
class SessionManagerProtocol(Protocol):
    """Protocol for managing questionnaire sessions."""
    
    def create_session(self, user_id: int) -> str:
        """Create a new questionnaire session."""
        ...
    
    def get_session(self, user_id: int) -> Optional[dict]:
        """Get active session for user."""
        ...
    
    def update_session(self, user_id: int, **kwargs) -> bool:
        """Update session data."""
        ...
    
    def delete_session(self, user_id: int) -> bool:
        """Delete user session."""
        ...


@runtime_checkable
class QuestionProviderProtocol(Protocol):
    """Protocol for providing questions and managing question flow."""
    
    def get_question_sequence(self, user: User) -> list[str]:
        """Get the sequence of question keys."""
        ...
    
    def get_question_text(self, question_key: str, user: User) -> str:
        """Get localized question text."""
        ...
    
    def should_ask_additional_question(self, answers: dict) -> bool:
        """Determine if additional questions should be asked."""
        ...
    
    def get_next_question(self, current_answers: dict, user: User) -> Optional[str]:
        """Get the next question key based on current answers."""
        ... 