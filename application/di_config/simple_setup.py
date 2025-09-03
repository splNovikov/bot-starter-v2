"""
Simplified DI setup for basic functionality testing.

Provides minimal service configuration without circular import issues.
"""

# Import sequence definitions
from application.handlers.sequence_user_info import user_info_sequence
from application.services.user_service import UserService
from core.di.container import DIContainer
from core.protocols.services import HttpClientProtocol, UserServiceProtocol
from core.sequence.protocols import (
    SequenceCompletionServiceProtocol,
    SequenceManagerProtocol,
    SequenceProgressServiceProtocol,
    SequenceProviderProtocol,
    SequenceQuestionRendererProtocol,
    SequenceQuestionServiceProtocol,
    SequenceServiceProtocol,
    SequenceSessionServiceProtocol,
)
from core.services.localization import LocalizationService
from core.utils.logger import get_logger
from infrastructure.api.client import HttpClient
from infrastructure.sequence import (
    InMemorySequenceManager,
    InMemorySequenceProvider,
)
from infrastructure.sequence.services import (
    SequenceCompletionService,
    SequenceProgressService,
    SequenceQuestionService,
    SequenceService,
    SequenceSessionService,
)
from infrastructure.ui.button_question_renderer import ButtonQuestionRenderer

logger = get_logger()


def setup_basic_services() -> DIContainer:
    """
    Set up basic services without sequence dependencies.

    Returns:
        Configured DIContainer instance with basic services
    """
    container = DIContainer()

    # Infrastructure layer services
    logger.info("Registering infrastructure services...")
    container.register_singleton(HttpClientProtocol, HttpClient)

    # Application layer services
    logger.info("Registering application services...")
    container.register_singleton(UserServiceProtocol, UserService)

    # Core services
    container.register_singleton(LocalizationService, LocalizationService)

    # Sequence services
    logger.info("Registering sequence services...")
    container.register_singleton(SequenceManagerProtocol, InMemorySequenceManager)

    # Create and register sequence provider with sequences
    sequence_provider = InMemorySequenceProvider(
        sequence_definitions=[user_info_sequence]
    )
    container.register_instance(SequenceProviderProtocol, sequence_provider)

    # Register question renderer for proper HTML formatting
    container.register_singleton(
        SequenceQuestionRendererProtocol, ButtonQuestionRenderer
    )

    # Register all sequence services for complete functionality
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

    container.register_singleton(SequenceServiceProtocol, SequenceService)

    logger.info("Basic DI container setup completed")
    return container


def get_basic_container() -> DIContainer:
    """
    Get a container with basic services configured.

    Returns:
        DIContainer with basic services
    """
    container = setup_basic_services()

    # Set as global container for legacy code compatibility
    # set_container(container) # This line is removed as per the edit hint.

    return container
