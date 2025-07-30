"""
Infrastructure package.

Contains infrastructure implementations for the application layer including
sequence management, UI components, and other technical concerns.
"""

from .sequence.factory import create_sequence_service, initialize_sequences

__all__ = [
    'create_sequence_service',
    'initialize_sequences'
] 