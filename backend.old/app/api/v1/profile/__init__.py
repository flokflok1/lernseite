"""
Profile API Package

Feature-based structure (flattened from appearance/subscription/user structure):
- appearance.py: User theme/appearance settings
- subscription.py: Subscription info for profile
- activity.py: User activity tracking
- preferences.py: User preferences
- core.py: Core profile operations

All routes: /api/v1/profile/*
"""

from app.api.v1.profile import appearance, subscription, activity, core, preferences

__all__ = ['appearance', 'subscription', 'core', 'activity', 'preferences']
