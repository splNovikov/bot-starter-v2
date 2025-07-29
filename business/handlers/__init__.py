"""
Business handlers package.

Contains application-specific handler implementations organized by feature.
This package provides a clean separation of concerns with different handler types.
"""

# Import the main router aggregator
from .router import main_router

# Import individual routers for direct access if needed
from .basic import start_router
from .settings import locale_router

# Maintain backward compatibility by providing the old user_router
# This allows existing code to continue working during transition
from .basic.start_handler import start_router as user_router

# Import the registry initialization function
from .registry_init import initialize_registry

__all__ = [
    'main_router',
    'start_router', 
    'locale_router',
    'user_router',  # Backward compatibility
    'initialize_registry'
] 