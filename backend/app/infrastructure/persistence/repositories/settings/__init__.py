"""
Settings Repository Package

System settings and user preferences repositories.

Example usage:
    >>> from app.infrastructure.persistence.repositories.settings.system import SystemSettingsRepository
    >>> from app.infrastructure.persistence.repositories.settings.user_preferences import UserPreferencesRepository
"""

from app.infrastructure.persistence.repositories.settings.system import SystemSettingsRepository
from app.infrastructure.persistence.repositories.settings.user_preferences import UserPreferencesRepository

__all__ = [
    'SystemSettingsRepository',
    'UserPreferencesRepository',
]
