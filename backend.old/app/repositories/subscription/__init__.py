"""
Subscription Repository Package

Data access layer for subscription and plan operations:
- Subscription plan CRUD
- User and organisation subscription management
- Subscription lifecycle (create, update, cancel, reactivate)
- Subscription statistics and analytics

Uses:
- Pure psycopg for PostgreSQL access
- Connection pooling for performance

ISO 27001:2013 compliant - Subscription management
"""

from app.repositories.subscription.crud import PlanRepository
from app.repositories.subscription.user_subscriptions import UserSubscriptionRepository
from app.repositories.subscription.organisation_subscriptions import (
    OrganisationSubscriptionRepository
)
from app.repositories.subscription.lifecycle import SubscriptionLifecycleRepository
from app.repositories.subscription.analytics import SubscriptionAnalyticsRepository



class SubscriptionRepository(
    PlanRepository,
    UserSubscriptionRepository,
    OrganisationSubscriptionRepository,
    SubscriptionLifecycleRepository,
    SubscriptionAnalyticsRepository
):
    """
    Unified SubscriptionRepository combining all functionality
    This class uses multiple inheritance to aggregate methods from specialized modules.
    """
    pass


__all__ = [
    'PlanRepository',
    'UserSubscriptionRepository',
    'OrganisationSubscriptionRepository',
    'SubscriptionLifecycleRepository',
    'SubscriptionAnalyticsRepository',
]
