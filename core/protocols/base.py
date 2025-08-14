"""
Base protocol interfaces for core infrastructure services.

Contains generic protocol definitions that can be used across different
business domains and are not specific to any particular feature.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ApiResponse:
    """Response from API call."""

    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
