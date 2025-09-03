"""
Context utilities for accessing services in handlers.

Provides convenient functions for accessing services through ApplicationFacade
from handler context, replacing deprecated global container access.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from core.facade.application_facade import ApplicationFacadeProtocol
from core.sequence.protocols import SequenceServiceProtocol
from core.services.localization import LocalizationService
from core.utils.logger import get_logger

# Forward declaration to avoid circular imports
if TYPE_CHECKING:
    from application.services.user_service import UserServiceProtocol

logger = get_logger()


class ServiceAccessError(Exception):
    """Exception raised when service access fails."""


def get_app_facade(data: Dict[str, Any]) -> ApplicationFacadeProtocol:
    """
    Get ApplicationFacade from handler context.

    Args:
        data: Handler context data

    Returns:
        ApplicationFacade instance

    Raises:
        ServiceAccessError: If facade is not available in context
    """
    app_facade = data.get("app_facade")
    if not app_facade:
        raise ServiceAccessError(
            "ApplicationFacade not found in context. "
            "Ensure ApplicationFacadeMiddleware is registered."
        )
    return app_facade


def get_user_service(data: Dict[str, Any]) -> "UserServiceProtocol":
    """
    Get user service from handler context.

    Args:
        data: Handler context data

    Returns:
        UserServiceProtocol instance

    Raises:
        ServiceAccessError: If service is not available
    """
    try:
        app_facade = get_app_facade(data)
        return app_facade.get_user_service()
    except Exception as e:
        logger.error(f"Failed to get user service: {e}")
        raise ServiceAccessError(f"User service access failed: {e}") from e


def get_sequence_service(data: Dict[str, Any]) -> SequenceServiceProtocol:
    """
    Get sequence service from handler context.

    Args:
        data: Handler context data

    Returns:
        SequenceServiceProtocol instance

    Raises:
        ServiceAccessError: If service is not available
    """
    try:
        app_facade = get_app_facade(data)
        return app_facade.get_sequence_service()
    except Exception as e:
        logger.error(f"Failed to get sequence service: {e}")
        raise ServiceAccessError(f"Sequence service access failed: {e}") from e


def get_localization_service(data: Dict[str, Any]) -> LocalizationService:
    """
    Get localization service from handler context.

    Args:
        data: Handler context data

    Returns:
        LocalizationService instance

    Raises:
        ServiceAccessError: If service is not available
    """
    try:
        app_facade = get_app_facade(data)
        return app_facade.get_localization_service()
    except Exception as e:
        logger.error(f"Failed to get localization service: {e}")
        raise ServiceAccessError(f"Localization service access failed: {e}") from e


def get_service(data: Dict[str, Any], service_type: type):
    """
    Get any service from handler context by type.

    Args:
        data: Handler context data
        service_type: Service type/protocol to resolve

    Returns:
        Service instance of the specified type

    Raises:
        ServiceAccessError: If service is not available
    """
    try:
        app_facade = get_app_facade(data)
        return app_facade.get_service(service_type)
    except Exception as e:
        logger.error(f"Failed to get service {service_type.__name__}: {e}")
        raise ServiceAccessError(
            f"Service access failed for {service_type.__name__}: {e}"
        ) from e


# Backward compatibility function with deprecation warning
def get_container_from_context(data: Dict[str, Any]) -> Optional[Any]:
    """
    DEPRECATED: Get container from context.

    This function is deprecated and provided only for backward compatibility.
    Use get_app_facade() and service-specific functions instead.

    Args:
        data: Handler context data

    Returns:
        ApplicationFacade DI container (deprecated access pattern)
    """
    import warnings

    warnings.warn(
        "get_container_from_context() is deprecated. Use get_app_facade() and service-specific functions instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    try:
        app_facade = get_app_facade(data)
        return app_facade.get_di_container()
    except Exception as e:
        logger.error(f"Failed to get container from context: {e}")
        return None
