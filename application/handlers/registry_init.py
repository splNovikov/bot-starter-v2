from core.utils.logger import get_logger


logger = get_logger()

def initialize_registry():
    try:
        from core.handlers.registry import get_registry
        from .router import main_router
        
        # Get registry instance and assign router
        registry = get_registry()
        registry._router = main_router
        
        # Re-register all enabled handlers with the router
        enabled_handlers = [
            handler for handler in registry.get_all_handlers() 
            if handler.metadata.enabled
        ]
        
        for handler in enabled_handlers:
            registry._register_with_router(handler)
        
        logger.info(
            f"Registry initialized successfully with {len(enabled_handlers)} "
            f"enabled handlers out of {len(registry.get_all_handlers())} total"
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize registry: {e}")
        raise RuntimeError(f"Registry initialization failed: {e}") from e 
