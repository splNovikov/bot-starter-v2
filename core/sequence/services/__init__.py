"""
Core sequence services package.

NOTE: This package is deprecated as part of Clean Architecture refactoring.
All concrete implementations have been moved to infrastructure.sequence.services.

This module is kept only as a placeholder. All services should be resolved
through dependency injection using the ApplicationFacade.

Example usage:
    from application import create_application_facade

    app_facade = create_application_facade()
    container = app_facade.get_di_container()
    sequence_service = container.resolve(SequenceServiceProtocol)
"""

# This module no longer exports any functions or services
__all__ = []
