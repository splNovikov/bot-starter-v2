"""
Core protocol interfaces.

Contains framework-level protocol definitions that define architectural
contracts and can be implemented by different layers.
"""

from .base import ApiResponse
from .entities import UserEntity
from .services import HttpClientProtocol, UserServiceProtocol

__all__ = [
    "ApiResponse",
    "UserEntity",
    "HttpClientProtocol",
    "UserServiceProtocol",
]
