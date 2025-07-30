from aiogram import Router

# Commands
from .command_start import start_router
from .command_locale import locale_router
# Sequences
from .sequence_user_info import sequence_user_info_router

# Create main router
main_router = Router(name="main_router")
# Commands
main_router.include_router(start_router)
main_router.include_router(locale_router)
# Sequences
main_router.include_router(sequence_user_info_router)
