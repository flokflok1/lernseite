"""Profile Domain - All Journeys"""

from .user import (
    profile_core_bp,
    profile_preferences_bp,
    profile_activity_bp,
    profile_theme_bp,
    profile_subscription_info_bp,
)

ALL_JOURNEY_BLUEPRINTS = [
    profile_core_bp,
    profile_preferences_bp,
    profile_activity_bp,
    profile_theme_bp,
    profile_subscription_info_bp,
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    'profile_core_bp',
    'profile_preferences_bp',
    'profile_activity_bp',
    'profile_theme_bp',
    'profile_subscription_info_bp',
]
