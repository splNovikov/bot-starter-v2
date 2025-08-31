"""
Application facade implementation.

Concrete implementation of ApplicationFacadeProtocol that orchestrates
all application layer components through a unified interface.
"""

from typing import List

from aiogram import Router

# Application layer imports
from application.di_config import get_basic_container
from application.handlers import initialize_registry, main_router, user_info_sequence
from core.di.container import DIContainer
from core.facade.application_facade import ApplicationFacadeProtocol
from core.sequence import set_translator_factory
from core.sequence.types import SequenceDefinition
from core.utils.logger import get_logger

logger = get_logger()


class ApplicationFacade(ApplicationFacadeProtocol):
    """
    Concrete implementation of application facade.

    Orchestrates application layer initialization, dependency injection,
    and handler registration through a clean, unified interface.
    """

    def __init__(self):
        """Initialize application facade."""
        self._container: DIContainer = None
        logger.info("ApplicationFacade initialized")

    def get_di_container(self) -> DIContainer:
        """
        Get configured dependency injection container.

        Returns:
            DIContainer with all application services registered
        """
        if self._container is None:
            self._container = get_basic_container()
            logger.info("✅ DI container created and configured")

        return self._container

    def get_main_router(self) -> Router:
        """
        Get main aiogram router with all handlers registered.

        Returns:
            Router instance with all application handlers included
        """
        logger.info("✅ Main router retrieved")
        return main_router

    def get_sequence_definitions(self) -> List[SequenceDefinition]:
        """
        Get all sequence definitions for the sequence framework.

        Returns:
            List of SequenceDefinition objects to register
        """
        sequence_definitions = [user_info_sequence]
        logger.info(f"✅ Retrieved {len(sequence_definitions)} sequence definitions")
        return sequence_definitions

    def initialize_handlers(self) -> None:
        """
        Initialize and register all application handlers.

        This method should be called before using the main router
        to ensure all decorated handlers are properly registered.
        """
        try:
            initialize_registry()
            logger.info("✅ Application handlers initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize handlers: {e}")
            raise

    def setup_legacy_services(self, container: DIContainer) -> None:
        """
        Setup legacy global services for backwards compatibility.

        Args:
            container: DI container with resolved services

        This method handles legacy service registration that some parts
        of the application might still depend on.
        """
        try:
            # Legacy services setup no longer needed - services resolved from DI container
            logger.info(
                "✅ Legacy global services no longer needed - using DI container"
            )
        except Exception as e:
            logger.error(f"❌ Failed to setup legacy services: {e}")
            raise

    def initialize_infrastructure(self) -> None:
        """
        Initialize infrastructure layer components.

        This method sets up infrastructure dependencies like HTTP clients,
        sequence systems, and external integrations through proper abstractions.
        """
        try:
            # Import infrastructure components locally to avoid architectural violations
            from infrastructure.sequence import (
                ContextAwareTranslator,
                initialize_sequences,
            )

            # Initialize translator factory
            def create_context_aware_translator(user):
                return ContextAwareTranslator(user)

            set_translator_factory(create_context_aware_translator)
            logger.info("✅ Translator factory initialized")

            # Get sequence definitions and initialize sequences
            sequence_definitions = self.get_sequence_definitions()
            initialize_sequences(sequence_definitions=sequence_definitions)
            logger.info("✅ Sequence system initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize infrastructure: {e}")
            raise

    async def cleanup_infrastructure(self) -> None:
        """
        Clean up infrastructure resources.

        This method properly disposes of infrastructure-level resources
        like HTTP clients and external connections.
        """
        try:
            # Import infrastructure cleanup locally to avoid architectural violations
            from infrastructure.api import close_http_client

            await close_http_client()
            logger.info("✅ Infrastructure resources cleaned up")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup infrastructure: {e}")
            raise

    async def dispose(self) -> None:
        """
        Clean up application resources.

        This method should be called during application shutdown
        to properly dispose of all application-level resources.
        """
        try:
            if self._container:
                await self._container.dispose()
                logger.info("✅ Application facade disposed")
        except Exception as e:
            logger.error(f"❌ Error disposing application facade: {e}")
            raise
