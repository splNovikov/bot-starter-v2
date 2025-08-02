"""
Core sequence services package.

Provides service implementations for the sequence framework including
session management, sequence orchestration, and result handling.
"""

from typing import Optional

from .base_sequence_manager import BaseSequenceManager
from .sequence_service import SequenceService

# Global sequence service instance
_sequence_service: Optional[SequenceService] = None


def get_sequence_service() -> Optional[SequenceService]:
    """
    Get the global sequence service instance.

    Returns:
        SequenceService instance or None if not set
    """
    return _sequence_service


def set_sequence_service(service: SequenceService) -> None:
    """
    Set the global sequence service instance.

    Args:
        service: SequenceService instance to set
    """
    global _sequence_service
    _sequence_service = service


__all__ = [
    "BaseSequenceManager",
    "SequenceService",
    "get_sequence_service",
    "set_sequence_service",
]
