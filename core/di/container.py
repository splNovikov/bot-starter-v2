"""
Simple dependency injection container.

Provides a lightweight DI container for managing service dependencies
with type safety and lifetime management.
"""

import inspect
from typing import Any, Callable, Dict, Optional, Type, TypeVar, get_type_hints

from core.utils.logger import get_logger

from .protocols import Disposable

T = TypeVar("T")

logger = get_logger()


class DIContainer:
    """
    Simple dependency injection container.

    Manages service registration, resolution, and lifetime.
    Supports singleton and transient lifetimes.
    """

    def __init__(self):
        """Initialize DI container."""
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}

    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """
        Register a service as singleton.

        Args:
            interface: The interface type
            implementation: The implementation type
        """
        self._services[interface] = implementation
        logger.debug(
            f"Registered singleton: {interface.__name__} -> {implementation.__name__}"
        )

    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """
        Register a service as transient (new instance each time).

        Args:
            interface: The interface type
            implementation: The implementation type
        """
        self._services[interface] = implementation
        # Don't store in singletons - new instance each resolve
        logger.debug(
            f"Registered transient: {interface.__name__} -> {implementation.__name__}"
        )

    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a service factory.

        Args:
            interface: The interface type
            factory: Factory function that creates the service
        """
        self._factories[interface] = factory
        logger.debug(f"Registered factory for: {interface.__name__}")

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register an existing instance as singleton.

        Args:
            interface: The interface type
            instance: The service instance
        """
        self._singletons[interface] = instance
        logger.debug(f"Registered instance: {interface.__name__}")

    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a service instance.

        Args:
            interface: The interface type to resolve

        Returns:
            Service instance

        Raises:
            ValueError: If service is not registered
        """
        # Check for existing singleton instance
        if interface in self._singletons:
            return self._singletons[interface]

        # Check for factory
        if interface in self._factories:
            instance = self._factories[interface]()
            # Store as singleton if registered as singleton
            if interface in self._services:
                self._singletons[interface] = instance
            return instance

        # Check for registered service
        if interface not in self._services:
            raise ValueError(f"Service {interface.__name__} is not registered")

        implementation = self._services[interface]

        # Create instance with dependency injection
        instance = self._create_instance(implementation)

        # Store as singleton (default behavior)
        self._singletons[interface] = instance

        return instance

    def _create_instance(self, cls: Type[T]) -> T:
        """
        Create instance with automatic dependency injection.

        Args:
            cls: Class to instantiate

        Returns:
            Instance with dependencies injected
        """
        # Get constructor parameters
        sig = inspect.signature(cls.__init__)
        type_hints = get_type_hints(cls.__init__)

        kwargs = {}

        # Resolve dependencies
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = type_hints.get(param_name)

            if (
                param_type
                and param_type in self._services
                or param_type in self._singletons
                or param_type in self._factories
            ):
                # Recursive resolve
                kwargs[param_name] = self.resolve(param_type)
            elif param.default != inspect.Parameter.empty:
                # Has default value - skip
                continue
            else:
                logger.warning(
                    f"Cannot resolve dependency {param_name}: {param_type} for {cls.__name__}"
                )

        return cls(**kwargs)

    def is_registered(self, interface: Type) -> bool:
        """
        Check if a service is registered.

        Args:
            interface: The interface type

        Returns:
            True if service is registered
        """
        return (
            interface in self._services
            or interface in self._singletons
            or interface in self._factories
        )

    async def dispose(self) -> None:
        """
        Dispose all services and clean up resources.

        Calls dispose() on all services that implement Disposable protocol.
        """
        logger.info("Disposing DI container...")

        # Dispose singleton instances that implement Disposable
        for instance in self._singletons.values():
            if isinstance(instance, Disposable):
                try:
                    await instance.dispose()
                except Exception as e:
                    logger.error(f"Error disposing {type(instance).__name__}: {e}")

        # Clear all registrations
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()

        logger.info("DI container disposed")


# Global container instance
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """
    Get the global DI container instance.

    Returns:
        DIContainer instance
    """
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def set_container(container: DIContainer) -> None:
    """
    Set the global DI container instance.

    Args:
        container: DI container to set as global
    """
    global _container
    _container = container
