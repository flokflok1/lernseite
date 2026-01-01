"""
LernsystemX Subscription Repository

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

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import psycopg
from psycopg.rows import dict_row

from app.extensions import db_pool


class SubscriptionRepository:
    """
    Subscription Repository for plan and subscription management

    All methods use psycopg connection pool and return dictionaries.
    """

    # ========================================================================
    # SUBSCRIPTION PLAN METHODS
    # ========================================================================

    @classmethod
    def get_all_plans(cls, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all subscription plans

        Args:
            active_only: Only return active plans

        Returns:
            List of plan dictionaries
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                query = "SELECT * FROM subscription_plans"

                if active_only:
                    query += " WHERE active = TRUE"

                query += " ORDER BY price_monthly"

                cur.execute(query)
                return cur.fetchall()

    @classmethod
    def get_plan_by_id(cls, plan_id: int) -> Optional[Dict[str, Any]]:
        """Get subscription plan by ID"""
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM subscription_plans
                    WHERE plan_id = %s
                """, (plan_id,))

                return cur.fetchone()

    @classmethod
    def get_plan_by_name(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get subscription plan by name"""
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM subscription_plans
                    WHERE name = %s
                """, (name,))

                return cur.fetchone()

    @classmethod
    def create_plan(cls, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create subscription plan (admin only)

        Args:
            plan_data: Plan data

        Returns:
            Created plan
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    INSERT INTO subscription_plans (
                        name, plan_type, plan_code, price_monthly, price_yearly,
                        token_monthly_grant, features, active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    plan_data['name'],
                    plan_data['plan_type'],
                    plan_data.get('plan_code', plan_data['name'].lower()),
                    plan_data['price_monthly'],
                    plan_data.get('price_yearly'),
                    plan_data.get('token_monthly_grant', 0),
                    psycopg.types.json.Jsonb(plan_data.get('features', {})),
                    plan_data.get('active', True)
                ))

                conn.commit()
                return cur.fetchone()

    # ========================================================================
    # SUBSCRIPTION METHODS
    # ========================================================================

    @classmethod
    def create_subscription_for_user(
        cls,
        user_id: int,
        plan_id: int,
        billing_cycle: str = 'monthly',
        trial_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create subscription for user

        Args:
            user_id: User ID
            plan_id: Plan ID
            billing_cycle: Billing cycle (monthly, yearly)
            trial_days: Trial period in days

        Returns:
            Created subscription
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Check if user already has active subscription
                cur.execute("""
                    SELECT * FROM subscriptions
                    WHERE user_id = %s AND status IN ('active', 'trial')
                """, (user_id,))

                existing = cur.fetchone()
                if existing:
                    raise ValueError(f'User {user_id} already has active subscription')

                # Get plan
                plan = cls.get_plan_by_id(plan_id)
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
    def create_subscription_for_organisation(
        cls,
        organisation_id: int,
        plan_id: int,
        billing_cycle: str = 'yearly'
    ) -> Dict[str, Any]:
        """
        Create subscription for organisation

        Args:
            organisation_id: Organisation ID
            plan_id: Plan ID
            billing_cycle: Billing cycle

        Returns:
            Created subscription
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Check existing subscription
                # Note: Database uses American spelling 'organization_id'
                cur.execute("""
                    SELECT * FROM subscriptions
                    WHERE organization_id = %s AND status = 'active'
                """, (organisation_id,))

                existing = cur.fetchone()
                if existing:
                    raise ValueError(f'Organisation {organisation_id} already has active subscription')

                # Calculate dates
                started_at = datetime.now()

                if billing_cycle == 'yearly':
                    expires_at = started_at + timedelta(days=365)
                else:
                    expires_at = started_at + timedelta(days=30)

                # Create subscription
                # Note: Database uses American spelling 'organization_id'
                cur.execute("""
                    INSERT INTO subscriptions (
                        organization_id, plan_id, status, billing_cycle,
                        started_at, expires_at, auto_renew
                    ) VALUES (%s, %s, 'active', %s, %s, %s, TRUE)
                    RETURNING *
                """, (organisation_id, plan_id, billing_cycle, started_at, expires_at))

                subscription = cur.fetchone()
                conn.commit()

                return subscription

    @classmethod
    def get_subscription_for_user(cls, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get active subscription for user

        Args:
            user_id: User ID

        Returns:
            Subscription with plan details or None
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
                    FROM subscriptions s
                    JOIN subscription_plans sp ON s.plan_id = sp.plan_id
                    WHERE s.user_id = %s
                    ORDER BY s.created_at DESC
                    LIMIT 1
                """, (user_id,))

                return cur.fetchone()

    @classmethod
    def get_subscription_for_organisation(cls, organisation_id: int) -> Optional[Dict[str, Any]]:
        """Get active subscription for organisation"""
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Note: Database uses American spelling 'organization_id'
                cur.execute("""
                    SELECT
                        s.*,
                        sp.name as plan_name,
                        sp.plan_type as plan_tier,
                        sp.price_monthly as monthly_price_eur,
                        sp.token_monthly_grant as included_tokens,
                        sp.features as plan_features
                    FROM subscriptions s
                    JOIN subscription_plans sp ON s.plan_id = sp.plan_id
                    WHERE s.organization_id = %s
                    ORDER BY s.created_at DESC
                    LIMIT 1
                """, (organisation_id,))

                return cur.fetchone()

    @classmethod
    def change_subscription(
        cls,
        subscription_id: int,
        new_plan_id: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Change subscription plan

        Args:
            subscription_id: Subscription ID
            new_plan_id: New plan ID
            reason: Change reason

        Returns:
            Updated subscription
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get current subscription
                cur.execute("""
                    SELECT * FROM subscriptions
                    WHERE subscription_id = %s
                """, (subscription_id,))

                subscription = cur.fetchone()
                if not subscription:
                    raise ValueError(f'Subscription {subscription_id} not found')

                # Get old and new plans
                old_plan = cls.get_plan_by_id(subscription['plan_id'])
                new_plan = cls.get_plan_by_id(new_plan_id)

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
                    UPDATE subscriptions
                    SET plan_id = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE subscription_id = %s
                    RETURNING *
                """, (new_plan_id, subscription_id))

                updated = cur.fetchone()
                conn.commit()

                return updated

    @classmethod
    def cancel_subscription(
        cls,
        subscription_id: int,
        reason: Optional[str] = None,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """
        Cancel subscription

        Args:
            subscription_id: Subscription ID
            reason: Cancellation reason
            immediate: Cancel immediately vs. end of period

        Returns:
            Updated subscription
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if immediate:
                    # Cancel immediately
                    cur.execute("""
                        UPDATE subscriptions
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
                        UPDATE subscriptions
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
    def reactivate_subscription(cls, subscription_id: int) -> Dict[str, Any]:
        """Reactivate cancelled subscription"""
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    UPDATE subscriptions
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

    @classmethod
    def get_subscription_stats(cls) -> Dict[str, Any]:
        """
        Get subscription statistics

        Returns:
            Statistics dictionary
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Total counts
                cur.execute("""
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                        SUM(CASE WHEN status = 'trial' THEN 1 ELSE 0 END) as trial,
                        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                        SUM(CASE WHEN status = 'expired' THEN 1 ELSE 0 END) as expired
                    FROM subscriptions
                """)

                totals = cur.fetchone()

                # By plan
                cur.execute("""
                    SELECT
                        sp.name,
                        COUNT(*) as count
                    FROM subscriptions s
                    JOIN subscription_plans sp ON s.plan_id = sp.plan_id
                    WHERE s.status IN ('active', 'trial')
                    GROUP BY sp.name
                """)

                by_plan = {row['name']: row['count'] for row in cur.fetchall()}

                # MRR calculation
                cur.execute("""
                    SELECT
                        COALESCE(SUM(
                            CASE
                                WHEN s.billing_cycle = 'yearly' THEN sp.price_yearly / 12
                                ELSE sp.price_monthly
                            END
                        ), 0) as mrr
                    FROM subscriptions s
                    JOIN subscription_plans sp ON s.plan_id = sp.plan_id
                    WHERE s.status IN ('active', 'trial')
                """)

                mrr_result = cur.fetchone()
                mrr = float(mrr_result['mrr']) if mrr_result else 0.0

                return {
                    'total_subscribers': totals['total'],
                    'active_subscribers': totals['active'],
                    'trial_subscribers': totals['trial'],
                    'cancelled_subscribers': totals['cancelled'],
                    'expired_subscribers': totals['expired'],
                    'by_plan': by_plan,
                    'by_status': {
                        'active': totals['active'],
                        'trial': totals['trial'],
                        'cancelled': totals['cancelled'],
                        'expired': totals['expired']
                    },
                    'mrr': mrr,
                    'arr': mrr * 12
                }

    @classmethod
    def get_expiring_subscriptions(cls, days: int = 3) -> List[Dict[str, Any]]:
        """
        Get subscriptions expiring soon

        Args:
            days: Days until expiry

        Returns:
            List of expiring subscriptions
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                expires_before = datetime.now() + timedelta(days=days)

                cur.execute("""
                    SELECT
                        s.*,
                        sp.name as plan_name,
                        sp.price_monthly as monthly_price_eur
                    FROM subscriptions s
                    JOIN subscription_plans sp ON s.plan_id = sp.plan_id
                    WHERE s.status = 'active'
                    AND s.expires_at <= %s
                    AND s.auto_renew = TRUE
                    ORDER BY s.expires_at
                """, (expires_before,))

                return cur.fetchall()
