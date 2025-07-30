"""
Base protocol interfaces for core infrastructure services.

Contains generic protocol definitions that can be used across different
business domains and are not specific to any particular feature.
"""

from typing import Protocol, runtime_checkable, Optional
from dataclasses import dataclass


@dataclass
class ApiResponse:
    """Response from API call."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    status_code: Optional[int] = None


@runtime_checkable
class ApiClientProtocol(Protocol):
    """Generic protocol for API client implementations."""
    
    async def submit_questionnaire_answer(
        self, 
        user_id: int, 
        question_key: str, 
        answer: str, 
        session_id: str
    ) -> ApiResponse:
        """Submit questionnaire answer to external API."""
        ...
    
    async def complete_questionnaire(
        self,
        user_id: int,
        session_id: str
    ) -> ApiResponse:
        """Mark questionnaire as completed in external API."""
        ... 