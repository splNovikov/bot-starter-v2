"""
Core protocol interfaces.

Contains framework-level protocol definitions that define architectural
contracts and can be implemented by different layers.
"""

from .base import ApiClientProtocol, ApiResponse

__all__ = ["ApiClientProtocol", "ApiResponse"]
