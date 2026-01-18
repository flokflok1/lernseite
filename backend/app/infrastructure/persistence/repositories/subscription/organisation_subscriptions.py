"""
Organisation Subscription Repository

Data access layer for organisation subscription operations:
- Create subscriptions for organisations/schools/companies
- Retrieve organisation subscriptions with plan details
- Organisation-specific subscription management

Uses pure psycopg for PostgreSQL access with connection pooling.

Note: Database uses American spelling 'organization_id'
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from psycopg.rows import dict_row

from app.extensions import db_pool
from app.infrastructure.persistence.repositories.subscription.crud import PlanRepository


class OrganisationSubscriptionRepository:
    """
    Organisation Subscription Repository for organisation-specific subscription management

    All methods use psycopg connection pool and return dictionaries.
    """

    @classmethod
    def create_subscription(
        cls,
        organization_id: int,
        plan_id: int,
        billing_cycle: str = 'yearly'
    ) -> Dict[str, Any]:
        """
        Create subscription for organisation

        Args:
            organization_id: Organisation identifier
            plan_id: Subscription plan identifier
            billing_cycle: Billing cycle ('monthly' or 'yearly', default: 'yearly')

        Returns:
            Created subscription dictionary

        Raises:
            ValueError: If organisation already has active subscription or plan not found

        Note:
            Database uses American spelling 'organization_id'
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Check existing subscription
                # Note: Database uses American spelling 'organization_id'
                cur.execute("""
                    SELECT * FROM billing_storage.subscriptions
                    WHERE organization_id = %s AND status = 'active'
                """, (organization_id,))

                existing = cur.fetchone()
                if existing:
                    raise ValueError(
                        f'Organisation {organization_id} already has active subscription'
                    )

                # Get plan
                plan = PlanRepository.get_plan_by_id(plan_id)
                if not plan:
                    raise ValueError(f'Plan {plan_id} not found')

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
                """, (organization_id, plan_id, billing_cycle, started_at, expires_at))

                subscription = cur.fetchone()
                conn.commit()

                return subscription

    @classmethod
    def get_subscription(cls, organization_id: int) -> Optional[Dict[str, Any]]:
        """
        Get active subscription for organisation

        Args:
            organization_id: Organisation identifier

        Returns:
            Subscription with plan details or None if not found

        Note:
            Database uses American spelling 'organization_id'
        """
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
                    FROM billing_storage.subscriptions s
                    JOIN billing_storage.subscription_plans sp ON s.plan_id = sp.plan_id
                    WHERE s.organization_id = %s
                    ORDER BY s.created_at DESC
                    LIMIT 1
                """, (organization_id,))

                return cur.fetchone()
