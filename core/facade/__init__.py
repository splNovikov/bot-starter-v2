"""
Core facade layer.

Provides clean interfaces for application layer components,
following the Facade design pattern to simplify complex subsystems.
"""

from .application_facade import ApplicationFacadeProtocol

__all__ = [
    "ApplicationFacadeProtocol",
]
