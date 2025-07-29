"""
Main router aggregator.

Combines all handler routers from different modules into a single router.
This provides a centralized point for registering all handlers with the dispatcher.
"""

# Third-party imports
from aiogram import Router

# Local application imports
from .basic import start_router
from .settings import locale_router

# Create main router
main_router = Router(name="main_router")

# Include all handler routers
main_router.include_router(start_router)
main_router.include_router(locale_router)

# Future routers can be added here:
# main_router.include_router(sequences_router)
# main_router.include_router(admin_router) 