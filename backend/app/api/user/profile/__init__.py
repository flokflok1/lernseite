"""
LernsystemX Profile API Package

User profile, preferences, subscription info, and theme management.
Refactored from flat structure into 3 focused packages.

Packages:
    - user: Core profile, activity, preferences (~318 + 144 + 260 = 722 lines split into 3 files)
    - subscription: Subscription information (~154 lines)
    - appearance: Theme settings (~154 lines)

Structure (all under 500 lines per file):
    user/core.py        ~318 lines  - /profile, /profile/change-password
    user/activity.py    ~144 lines  - /profile/activity
    user/preferences.py ~260 lines  - /profile/preferences
    subscription/info.py ~154 lines - /profile/subscription
    appearance/theme.py  ~154 lines - /profile/theme

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    Final URLs: /api/v1/profile/...

Refactored: 2026-01-08 per Developer-Guide-KI Section 10
"""

from .user import profile_core_bp, profile_activity_bp, profile_preferences_bp
from .subscription import profile_subscription_bp
from .appearance import profile_theme_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    profile_core_bp,
    profile_activity_bp,
    profile_preferences_bp,
    profile_subscription_bp,
    profile_theme_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported from app/api/__init__.py
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    'profile_core_bp',
    'profile_activity_bp',
    'profile_preferences_bp',
    'profile_subscription_bp',
    'profile_theme_bp',
    'ALL_BLUEPRINTS',
]
