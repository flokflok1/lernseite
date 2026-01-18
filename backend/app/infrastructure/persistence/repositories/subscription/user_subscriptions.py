"""
User Subscription Repository

Data access layer for user subscription operations:
- Create subscriptions for users with trial support
- Retrieve user subscriptions with plan details
- User-specific subscription management

Uses pure psycopg for PostgreSQL access with connection pooling.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from psycopg.rows import dict_row

from app.core.bootstrap.extensions import db_pool
from app.infrastructure.persistence.repositories.subscription.crud import PlanRepository


class UserSubscriptionRepository:
    """
    User Subscription Repository for user-specific subscription management

    All methods use psycopg connection pool and return dictionaries.
    """

    @classmethod
    def create_subscription(
        cls,
        user_id: int,
        plan_id: int,
        billing_cycle: str = 'monthly',
        trial_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create subscription for user

        Args:
            user_id: User identifier
            plan_id: Subscription plan identifier
            billing_cycle: Billing cycle ('monthly' or 'yearly')
            trial_days: Trial period in days (optional)

        Returns:
            Created subscription dictionary

        Raises:
            ValueError: If user already has active subscription or plan not found
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Check if user already has active subscription
                cur.execute("""
                    SELECT * FROM billing_storage.subscriptions
                    WHERE user_id = %s AND status IN ('active', 'trial')
                """, (user_id,))

                existing = cur.fetchone()
                if existing:
                    raise ValueError(f'User {user_id} already has active subscription')

                # Get plan
                plan = PlanRepository.get_plan_by_id(plan_id)
                if not plan:
                    raise ValueError(f'Plan {plan_id} not found')

                # Calculate dates
                started_at = datetime.now()

                if trial_days and trial_days > 0:
                    trial_ends_at = started_at + timedelta(days=trial_days)
                    status = 'trial'
                    expires_at = trial_ends_at
                else:
                    trial_ends_at = None
                    status = 'active'

                    if billing_cycle == 'yearly':
                        expires_at = started_at + timedelta(days=365)
                    else:
                        expires_at = started_at + timedelta(days=30)

                # Create subscription
                cur.execute("""
                    INSERT INTO subscriptions (
                        user_id, plan_id, status, billing_cycle,
                        started_at, expires_at, trial_ends_at, auto_renew
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                    RETURNING *
                """, (
                    user_id, plan_id, status, billing_cycle,
                    started_at, expires_at, trial_ends_at
                ))

                subscription = cur.fetchone()
                conn.commit()

                return subscription

    @classmethod
    def get_subscription(cls, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get active subscription for user

        Args:
            user_id: User identifier

        Returns:
            Subscription with plan details or None if not found
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        s.*,
                        sp.name as plan_name,
                        sp.plan_type as plan_tier,
                        sp.price_monthly as monthly_price_eur,
                        sp.token_monthly_grant as included_tokens,
                        sp.features as plan_features
                    FROM billing_storage.subscriptions s
                    JOIN billing_storage.subscription_plans sp ON s.plan_id = sp.plan_id
                    WHERE s.user_id = %s
                    ORDER BY s.created_at DESC
                    LIMIT 1
                """, (user_id,))

                return cur.fetchone()

    @classmethod
    def get_subscription_for_user(cls, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Alias for get_subscription() for backward compatibility

        Args:
            user_id: User identifier

        Returns:
            Subscription with plan details or None if not found
        """
        return cls.get_subscription(user_id)
