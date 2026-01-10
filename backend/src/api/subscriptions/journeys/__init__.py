"""Subscriptions Domain - All Journeys"""

from .public import subscriptions_plans_bp
from .user import subscriptions_user_bp, subscriptions_billing_bp
from .admin import subscriptions_admin_bp

ALL_JOURNEY_BLUEPRINTS = [
    # Public Journey (1 endpoint)
    subscriptions_plans_bp,
    # User Journey (5 endpoints)
    subscriptions_user_bp,
    subscriptions_billing_bp,
    # Admin Journey (2 endpoints)
    subscriptions_admin_bp,
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    'subscriptions_plans_bp',
    'subscriptions_user_bp',
    'subscriptions_billing_bp',
    'subscriptions_admin_bp',
]
