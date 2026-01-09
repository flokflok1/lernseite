"""
Subscription Analytics Repository

Data access layer for subscription reporting and analytics:
- Subscription statistics (counts by status, plan, MRR/ARR)
- Expiring subscription alerts
- Subscription metrics and KPIs

Uses pure psycopg for PostgreSQL access with connection pooling.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from psycopg.rows import dict_row

from app.extensions import db_pool


class SubscriptionAnalyticsRepository:
    """
    Subscription Analytics Repository for reporting and metrics

    All methods use psycopg connection pool and return dictionaries.
    """

    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """
        Get comprehensive subscription statistics

        Returns statistics including:
        - Total subscription counts by status
        - Distribution by plan
        - MRR (Monthly Recurring Revenue)
        - ARR (Annual Recurring Revenue)

        Returns:
            Statistics dictionary with keys:
            - total_subscribers: Total subscription count
            - active_subscribers: Active subscriptions
            - trial_subscribers: Trial subscriptions
            - cancelled_subscribers: Cancelled subscriptions
            - expired_subscribers: Expired subscriptions
            - by_plan: Dictionary with plan names and counts
            - by_status: Dictionary with status breakdown
            - mrr: Monthly recurring revenue
            - arr: Annual recurring revenue
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
                    FROM billing_storage.subscriptions s
                    JOIN billing_storage.subscription_plans sp ON s.plan_id = sp.plan_id
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
                    FROM billing_storage.subscriptions s
                    JOIN billing_storage.subscription_plans sp ON s.plan_id = sp.plan_id
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
        Get subscriptions expiring within specified timeframe

        Args:
            days: Days until expiry to check (default: 3)

        Returns:
            List of expiring subscription dictionaries with:
            - subscription_id, user_id, organization_id
            - status, billing_cycle, expires_at
            - plan_name, monthly_price_eur
            - auto_renew flag
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                expires_before = datetime.now() + timedelta(days=days)

                cur.execute("""
                    SELECT
                        s.*,
                        sp.name as plan_name,
                        sp.price_monthly as monthly_price_eur
                    FROM billing_storage.subscriptions s
                    JOIN billing_storage.subscription_plans sp ON s.plan_id = sp.plan_id
                    WHERE s.status = 'active'
                    AND s.expires_at <= %s
                    AND s.auto_renew = TRUE
                    ORDER BY s.expires_at
                """, (expires_before,))

                return cur.fetchall()
