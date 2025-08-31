"""
Application layer entry point.

Provides the main application facade for external consumption,
following Clean Architecture principles where application layer
orchestrates business logic through core abstractions.
"""

from .facade import ApplicationFacade

# Factory function for creating application facade
def create_application_facade() -> ApplicationFacade:
    """
    Create and return a new application facade instance.
    
    Returns:
        ApplicationFacade: Configured application facade
    """
    return ApplicationFacade()

__all__ = [
    "ApplicationFacade", 
    "create_application_facade"
]
