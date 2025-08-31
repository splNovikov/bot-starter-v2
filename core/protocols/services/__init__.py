"""
Core service protocols.

Defines interfaces for external services without depending on their implementations,
following the Dependency Inversion Principle.
"""

from .services import HttpClientProtocol, UserServiceProtocol

__all__ = [
    "HttpClientProtocol",
    "UserServiceProtocol",
]
