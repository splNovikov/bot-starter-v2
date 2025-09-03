"""
Application facade protocol.

Defines the contract for application layer initialization and configuration,
providing a clean interface that isolates core from application implementation details.
"""

from typing import List, Protocol, TypeVar, runtime_checkable

from aiogram import Router

from core.di.container import DIContainer
from core.sequence.types import SequenceDefinition

T = TypeVar("T")


@runtime_checkable
class ApplicationFacadeProtocol(Protocol):
    """
    Protocol for application layer facade.

    Provides a unified interface for application initialization,
    dependency injection setup, and handler registration.
    This facade isolates core layer from application implementation details.
    """

    def get_di_container(self) -> DIContainer:
        """
        Get configured dependency injection container.

        Returns:
            DIContainer with all application services registered
        """
        ...

    def get_main_router(self) -> Router:
        """
        Get main aiogram router with all handlers registered.

        Returns:
            Router instance with all application handlers included
        """
        ...

    def get_sequence_definitions(self) -> List[SequenceDefinition]:
        """
        Get all sequence definitions for the sequence framework.

        Returns:
            List of SequenceDefinition objects to register
        """
        ...

    def initialize_handlers(self) -> None:
        """
        Initialize and register all application handlers.

        This method should be called before using the main router
        to ensure all decorated handlers are properly registered.
        """
        ...

    def get_service(self, service_type: type[T]) -> T:
        """
        Get a service instance from the DI container.

        This method provides a clean interface for service resolution,
        replacing direct calls to get_container().resolve().

        Args:
            service_type: The service protocol/interface to resolve

        Returns:
            Service instance of the specified type

        Raises:
            ValueError: If service is not registered or resolution fails
        """
        ...

    def get_user_service(self):
        """
        Get user service instance.

        Returns:
            UserServiceProtocol instance for user operations
        """
        ...

    def get_sequence_service(self):
        """
        Get sequence service instance.

        Returns:
            SequenceServiceProtocol instance for sequence operations
        """
        ...

    def get_localization_service(self):
        """
        Get localization service instance.

        Returns:
            LocalizationService instance for i18n operations
        """
        ...

    def setup_legacy_services(self, container: DIContainer) -> None:
        """
        Setup legacy global services for backwards compatibility.

        Args:
            container: DI container with resolved services

        This method handles legacy service registration that some parts
        of the application might still depend on.
        """
        ...

    def initialize_infrastructure(self) -> None:
        """
        Initialize infrastructure layer components.

        This method should be called to setup infrastructure dependencies
        like HTTP clients, sequence systems, and external integrations.
        """
        ...

    async def cleanup_infrastructure(self) -> None:
        """
        Clean up infrastructure resources.

        This method should be called during application shutdown
        to properly dispose of infrastructure-level resources.
        """
        ...

    async def dispose(self) -> None:
        """
        Clean up application resources.

        This method should be called during application shutdown
        to properly dispose of all application-level resources.
        """
        ...
