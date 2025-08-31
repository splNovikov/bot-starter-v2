"""
Dependency injection container setup and configuration.

Provides functions to configure the DI container with all necessary
service registrations for the application.
"""

from application.services.user_service import UserService
from core.di.container import DIContainer, get_container
from core.protocols.services import HttpClientProtocol, UserServiceProtocol
from core.sequence.protocols import (
    SequenceCompletionServiceProtocol,
    SequenceManagerProtocol,
    SequenceProgressServiceProtocol,
    SequenceProviderProtocol,
    SequenceQuestionRendererProtocol,
    SequenceQuestionServiceProtocol,
    SequenceResultHandlerProtocol,
    SequenceSessionServiceProtocol,
)
from core.sequence.services import (
    SequenceCompletionService,
    SequenceOrchestrator,
    SequenceProgressService,
    SequenceQuestionService,
    SequenceSessionService,
)
from core.utils.logger import get_logger
from infrastructure.api.client import HttpClient

logger = get_logger()


def setup_di_container() -> DIContainer:
    """
    Set up and configure the DI container with all service registrations.

    Returns:
        Configured DIContainer instance
    """
    container = get_container()

    # Infrastructure layer services
    logger.info("Registering infrastructure services...")
    container.register_singleton(HttpClientProtocol, HttpClient)

    # Application layer services
    logger.info("Registering application services...")
    container.register_singleton(UserServiceProtocol, UserService)

    # Core sequence services
    logger.info("Registering sequence services...")
    container.register_singleton(SequenceSessionServiceProtocol, SequenceSessionService)
    container.register_singleton(
        SequenceQuestionServiceProtocol, SequenceQuestionService
    )
    container.register_singleton(
        SequenceProgressServiceProtocol, SequenceProgressService
    )
    container.register_singleton(
        SequenceCompletionServiceProtocol, SequenceCompletionService
    )

    # Main orchestration service
    container.register_singleton(SequenceOrchestrator, SequenceOrchestrator)

    logger.info("DI container setup completed")
    return container


def register_sequence_dependencies(
    container: DIContainer,
    session_manager: SequenceManagerProtocol,
    sequence_provider: SequenceProviderProtocol,
    question_renderer: SequenceQuestionRendererProtocol = None,
    result_handler: SequenceResultHandlerProtocol = None,
) -> None:
    """
    Register sequence-specific dependencies that need to be provided externally.

    Args:
        container: DI container instance
        session_manager: Session management implementation
        sequence_provider: Sequence provision implementation
        question_renderer: Optional question renderer implementation
        result_handler: Optional result handler implementation
    """
    logger.info("Registering sequence dependencies...")

    # Register core sequence components
    container.register_instance(SequenceManagerProtocol, session_manager)
    container.register_instance(SequenceProviderProtocol, sequence_provider)

    if question_renderer:
        container.register_instance(SequenceQuestionRendererProtocol, question_renderer)

    if result_handler:
        container.register_instance(SequenceResultHandlerProtocol, result_handler)

    logger.info("Sequence dependencies registered")


def get_configured_container() -> DIContainer:
    """
    Get a fully configured DI container.

    This is the main function to use when you need a ready-to-use container
    with all basic services registered.

    Returns:
        Configured DIContainer instance
    """
    return setup_di_container()
