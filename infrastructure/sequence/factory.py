"""
Sequence service factory.

Creates and configures the sequence service with all required components
for the in-memory sequence implementation.
"""

from core.sequence import SequenceService, set_sequence_service
from core.utils.logger import get_logger

from .provider import InMemorySequenceProvider
from .manager import InMemorySequenceManager
from ..ui.button_question_renderer import ButtonQuestionRenderer

logger = get_logger()


def create_sequence_service() -> SequenceService:
    """
    Create and configure the sequence service with all components.
    
    Returns:
        Configured SequenceService instance
    """
    # Create components
    sequence_provider = InMemorySequenceProvider()
    sequence_manager = InMemorySequenceManager()
    question_renderer = ButtonQuestionRenderer()
    
    # Create sequence service
    sequence_service = SequenceService(
        session_manager=sequence_manager,
        sequence_provider=sequence_provider,
        question_renderer=question_renderer
    )
    
    # Set as global service
    set_sequence_service(sequence_service)
    
    logger.info("Sequence service created and configured successfully")
    return sequence_service


def initialize_sequences() -> None:
    """
    Initialize the sequence system.
    
    This function should be called during application startup
    to set up the sequence service and make it available globally.
    """
    try:
        service = create_sequence_service()
        logger.info(f"Sequence system initialized with {len(service._sequence_provider.get_available_sequences())} sequences")
    except Exception as e:
        logger.error(f"Failed to initialize sequence system: {e}")
        raise


__all__ = ['create_sequence_service', 'initialize_sequences'] 