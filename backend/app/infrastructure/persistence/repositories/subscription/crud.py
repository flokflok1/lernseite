"""
Subscription Plan CRUD Repository

Data access layer for subscription plan management:
- Create, read, and manage subscription plans
- Plan activation/deactivation
- Plan feature management

Uses pure psycopg for PostgreSQL access with connection pooling.
"""

from typing import Dict, Any, Optional, List
import psycopg
from psycopg.rows import dict_row

from app.core.bootstrap import extensions


class PlanRepository:
    """
    Plan Repository for subscription plan management

    All methods use psycopg connection pool and return dictionaries.
    """

    @classmethod
    def get_all_plans(cls, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all subscription plans

        Args:
            active_only: Only return active plans

        Returns:
            List of plan dictionaries
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                query = "SELECT * FROM subscription_plans"

                if active_only:
                    query += " WHERE active = TRUE"

                query += " ORDER BY price_monthly"

                cur.execute(query)
                return cur.fetchall()

    @classmethod
    def get_plan_by_id(cls, plan_id: int) -> Optional[Dict[str, Any]]:
        """
        Get subscription plan by ID

        Args:
            plan_id: Plan identifier

        Returns:
            Plan dictionary or None if not found
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM billing_storage.subscription_plans
                    WHERE plan_id = %s
                """, (plan_id,))

                return cur.fetchone()

    @classmethod
    def get_plan_by_name(cls, name: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription plan by name

        Args:
            name: Plan name

        Returns:
            Plan dictionary or None if not found
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM billing_storage.subscription_plans
                    WHERE name = %s
                """, (name,))

                return cur.fetchone()

    @classmethod
    def create_plan(cls, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create subscription plan (admin only)

        Args:
            plan_data: Plan data dictionary containing:
                - name: Plan name (required)
                - plan_type: Plan type (required)
                - plan_code: Plan code (defaults to lowercase name)
                - price_monthly: Monthly price (required)
                - price_yearly: Yearly price (optional)
                - token_monthly_grant: Monthly token allowance (default: 0)
                - features: Plan features JSON (default: {})
                - active: Active status (default: True)

        Returns:
            Created plan dictionary

        Raises:
            ValueError: If required plan_data fields missing
        """
        with extensions.db_pool.connection() as conn:
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

    @classmethod
    def get_subscription_with_plan(cls, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription joined with its plan details.

        Args:
            subscription_id: Subscription ID

        Returns:
            Subscription dict with plan's included_tokens, or None
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT s.*, sp.included_tokens
                    FROM subscriptions s
                    JOIN subscription_plans sp ON s.plan_id = sp.plan_id
                    WHERE s.subscription_id = %s
                """, (subscription_id,))
                return cur.fetchone()
