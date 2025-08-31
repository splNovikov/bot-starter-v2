"""
Core sequence services package.

Provides service implementations for the sequence framework including
session management, sequence orchestration, and result handling.
"""

from typing import Optional

from .base_sequence_manager import BaseSequenceManager
from .completion_service import SequenceCompletionService
from .progress_service import SequenceProgressService
from .question_service import SequenceQuestionService
from .sequence_orchestrator import SequenceOrchestrator
from .sequence_service import SequenceService
from .session_service import SequenceSessionService

# Global sequence service instance (legacy - will be replaced by DI)
_sequence_service: Optional[SequenceService] = None


def get_sequence_service() -> Optional[SequenceService]:
    """
    Get the global sequence service instance.

    Returns:
        SequenceService instance or None if not set

    Note:
        This function is deprecated. Use DI container to resolve services.
    """
    return _sequence_service


def set_sequence_service(service: SequenceService) -> None:
    """
    Set the global sequence service instance.

    Args:
        service: SequenceService instance to set

    Note:
        This function is deprecated. Use DI container to register services.
    """
    global _sequence_service
    _sequence_service = service


__all__ = [
    "BaseSequenceManager",
    "SequenceService",
    # Refactored services
    "SequenceSessionService",
    "SequenceQuestionService",
    "SequenceProgressService",
    "SequenceCompletionService",
    "SequenceOrchestrator",
    # Legacy global functions
    "get_sequence_service",
    "set_sequence_service",
]
