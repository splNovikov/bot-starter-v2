"""
HTTP infrastructure module.

Contains HTTP client implementations and related utilities for external service integration.
"""

from .client import HttpClient, close_http_client, get_http_client

__all__ = ["HttpClient", "get_http_client", "close_http_client"]
