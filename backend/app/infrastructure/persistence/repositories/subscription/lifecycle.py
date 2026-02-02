"""
Subscription Lifecycle Repository

Data access layer for subscription state management:
- Change subscription plans
- Cancel subscriptions (immediate or end-of-period)
- Reactivate cancelled subscriptions
- Upgrade/downgrade tracking

Uses pure psycopg for PostgreSQL access with connection pooling.
"""

from typing import Dict, Any, Optional
from psycopg.rows import dict_row

from app.core.bootstrap import extensions
from app.infrastructure.persistence.repositories.subscription.crud import PlanRepository


class SubscriptionLifecycleRepository:
    """
    Subscription Lifecycle Repository for managing subscription state transitions

    All methods use psycopg connection pool and return dictionaries.
    """

    @classmethod
    def change_plan(
        cls,
        subscription_id: int,
        new_plan_id: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Change subscription plan (upgrade or downgrade)

        Args:
            subscription_id: Subscription identifier
            new_plan_id: New plan identifier
            reason: Change reason (optional)

        Returns:
            Updated subscription dictionary

        Raises:
            ValueError: If subscription or plan not found
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get current subscription
                cur.execute("""
                    SELECT * FROM billing_storage.subscriptions
                    WHERE subscription_id = %s
                """, (subscription_id,))

                subscription = cur.fetchone()
                if not subscription:
                    raise ValueError(f'Subscription {subscription_id} not found')

                # Get old and new plans
                old_plan = PlanRepository.get_plan_by_id(subscription['plan_id'])
                new_plan = PlanRepository.get_plan_by_id(new_plan_id)

                if not new_plan:
                    raise ValueError(f'Plan {new_plan_id} not found')

                # Log upgrade/downgrade
                if subscription.get('user_id'):
                    cur.execute("""
                        INSERT INTO subscription_upgrades (
                            user_id, from_plan, to_plan, reason
                        ) VALUES (%s, %s, %s, %s)
                    """, (
                        subscription['user_id'],
                        old_plan['name'],
                        new_plan['name'],
                        reason
                    ))

                # Update subscription
                cur.execute("""
                    UPDATE billing_storage.subscriptions
                    SET plan_id = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE subscription_id = %s
                    RETURNING *
                """, (new_plan_id, subscription_id))

                updated = cur.fetchone()
                conn.commit()

                return updated

    @classmethod
    def cancel(
        cls,
        subscription_id: int,
        reason: Optional[str] = None,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """
        Cancel subscription

        Args:
            subscription_id: Subscription identifier
            reason: Cancellation reason (optional)
            immediate: Cancel immediately (True) vs. end of period (False)

        Returns:
            Updated subscription dictionary

        Raises:
            ValueError: If subscription not found
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if immediate:
                    # Cancel immediately
                    cur.execute("""
                        UPDATE billing_storage.subscriptions
                        SET status = 'cancelled',
                            cancelled_at = CURRENT_TIMESTAMP,
                            cancellation_reason = %s,
                            auto_renew = FALSE,
                            expires_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE subscription_id = %s
                        RETURNING *
                    """, (reason, subscription_id))
                else:
                    # Cancel at end of period
                    cur.execute("""
                        UPDATE billing_storage.subscriptions
                        SET status = 'cancelled',
                            cancelled_at = CURRENT_TIMESTAMP,
                            cancellation_reason = %s,
                            auto_renew = FALSE,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE subscription_id = %s
                        RETURNING *
                    """, (reason, subscription_id))

                subscription = cur.fetchone()
                conn.commit()

                return subscription

    @classmethod
    def reactivate(cls, subscription_id: int) -> Dict[str, Any]:
        """
        Reactivate cancelled subscription

        Args:
            subscription_id: Subscription identifier

        Returns:
            Updated subscription dictionary

        Raises:
            ValueError: If subscription not found
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    UPDATE billing_storage.subscriptions
                    SET status = 'active',
                        cancelled_at = NULL,
                        cancellation_reason = NULL,
                        auto_renew = TRUE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE subscription_id = %s
                    RETURNING *
                """, (subscription_id,))

                subscription = cur.fetchone()
                conn.commit()

                return subscription
