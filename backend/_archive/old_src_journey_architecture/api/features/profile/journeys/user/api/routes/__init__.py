"""Profile Domain - User Journey Routes"""
from .core import profile_core_bp
from .preferences import profile_preferences_bp
from .activity import profile_activity_bp
from .theme import profile_theme_bp
from .subscription_info import profile_subscription_info_bp
__all__ = [
    'profile_core_bp',
    'profile_preferences_bp',
    'profile_activity_bp',
    'profile_theme_bp',
    'profile_subscription_info_bp',
]
