"""
Protocols for dependency injection system.

Defines the contracts for injectable services and dependencies.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Injectable(Protocol):
    """
    Protocol for services that can be injected by the DI container.

    Services implementing this protocol can be automatically resolved
    and injected into other services that depend on them.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the injectable service."""
        ...


@runtime_checkable
class Disposable(Protocol):
    """
    Protocol for services that need cleanup on shutdown.

    Services implementing this protocol will have their dispose()
    method called when the DI container is being cleaned up.
    """

    async def dispose(self) -> None:
        """Clean up resources used by this service."""
        ...
