# Import the main router aggregator
from .router import main_router

# Import individual routers for direct access if needed
from .command_start import command_start_router
from .command_locale import command_locale_router

# Import the registry initialization function
from .registry_init import initialize_registry

__all__ = [
    'main_router',
    'command_start_router',
    'command_locale_router',
    'initialize_registry'
] 
