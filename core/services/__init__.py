"""
Core services module.

Contains infrastructure-level services that are framework concerns
and can be reused across different business domains.
"""

from .localization import LocalizationService, get_localization_service, t

__all__ = [
    'LocalizationService',
    'get_localization_service', 
    't'
] 