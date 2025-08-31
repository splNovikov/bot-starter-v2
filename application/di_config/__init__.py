"""
Application layer DI configuration.

Contains dependency injection setup and configuration that depends on
both Application and Infrastructure layers, maintaining Clean Architecture
principles by keeping Core layer independent.
"""

from .setup import (
    get_configured_container,
    register_sequence_dependencies,
    setup_di_container,
)
from .simple_setup import get_basic_container

__all__ = [
    "get_configured_container",
    "register_sequence_dependencies",
    "setup_di_container",
    "get_basic_container",
]
