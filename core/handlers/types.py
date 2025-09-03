"""
Type definitions for the handlers registry system.
Provides enums, type aliases, and data structures for type-safe handler management.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class HandlerType(Enum):
    """Enumeration of different handler types."""

    COMMAND = "command"
    TEXT = "text"
    MESSAGE = "message"
    CALLBACK = "callback"
    INLINE = "inline"


class HandlerCategory(Enum):
    """Categories for organizing handlers."""

    CORE = "core"  # Essential bot commands (start, help)
    USER = "user"  # User interaction commands
    ADMIN = "admin"  # Administrative commands
    UTILITY = "utility"  # Utility and helper commands
    FUN = "fun"  # Entertainment commands


@dataclass
class HandlerMetadata:
    """Metadata for a registered handler."""

    # Basic information
    name: str
    description: str
    handler_type: HandlerType
    category: HandlerCategory = HandlerCategory.USER

    # Command-specific information
    command: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    usage: Optional[str] = None
    examples: List[str] = field(default_factory=list)

    # Callback-specific information
    callback_filter: Optional[str] = None  # Filter pattern for callback queries

    # Behavior configuration
    enabled: bool = True
    hidden: bool = False  # Hidden from help
    admin_only: bool = False

    # Additional metadata
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    author: Optional[str] = None

    def __post_init__(self):
        """Validate metadata after initialization."""
        if self.handler_type == HandlerType.COMMAND and not self.command:
            raise ValueError("Command handlers must specify a command name")

        if self.handler_type == HandlerType.CALLBACK and not self.callback_filter:
            raise ValueError("Callback handlers must specify a callback filter")

        if self.command and not self.usage:
            # Auto-generate basic usage if not provided
            self.usage = f"/{self.command}"


@dataclass
class HandlerStats:
    """Statistics for handler usage."""

    calls: int = 0
    errors: int = 0
    last_called: Optional[float] = None  # Unix timestamp
    avg_response_time: float = 0.0


# Type aliases for better readability
HandlerFunction = Any  # Will be more specific in protocols.py
HandlerRegistry = Dict[str, "RegisteredHandler"]
MetadataDict = Dict[str, Any]


@dataclass
class RegisteredHandler:
    """Container for a registered handler with its metadata."""

    function: HandlerFunction
    metadata: HandlerMetadata
    stats: HandlerStats = field(default_factory=HandlerStats)

    @property
    def identifier(self) -> str:
        """Get unique identifier for this handler."""
        if self.metadata.command:
            return f"cmd_{self.metadata.command}"
        return f"{self.metadata.handler_type.value}_{self.metadata.name}"

    def __str__(self) -> str:
        """String representation of the handler."""
        return f"Handler({self.metadata.name}, {self.metadata.handler_type.value})"
