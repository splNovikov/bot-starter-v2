"""
Simplified DI setup for basic functionality testing.

Provides minimal service configuration without circular import issues.
"""

from application.services.user_service import UserService
from core.di.container import DIContainer
from core.protocols.services import HttpClientProtocol, UserServiceProtocol
from core.utils.logger import get_logger
from infrastructure.api.client import HttpClient

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

    logger.info("Basic DI container setup completed")
    return container


def get_basic_container() -> DIContainer:
    """
    Get a container with basic services configured.

    Returns:
        DIContainer with basic services
    """
    return setup_basic_services()
