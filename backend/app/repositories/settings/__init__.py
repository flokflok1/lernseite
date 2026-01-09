"""
Settings Repository Package

System settings and user preferences repositories.

Example usage:
    >>> from app.repositories.settings.system import SystemSettingsRepository
    >>> from app.repositories.settings.user_preferences import UserPreferencesRepository
"""

from app.repositories.settings.system import SystemSettingsRepository
from app.repositories.settings.user_preferences import UserPreferencesRepository

__all__ = [
    'SystemSettingsRepository',
    'UserPreferencesRepository',
]
