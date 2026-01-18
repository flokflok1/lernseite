"""
Token Analytics Repository

Data access layer for token usage statistics and reporting:
- User token statistics (consumption, purchases, grants)
- Organisation token statistics
- Global system-wide statistics
- Usage breakdown by method and reason

Uses psycopg connection pooling for efficient analytics queries.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from psycopg.rows import dict_row

from app.extensions import db_pool
from .wallet import TokenWalletRepository


class TokenAnalyticsRepository:
    """
    Token Analytics Repository

    Provides statistical views of token usage for users, organisations, and system.
    All queries use read-only operations for performance.
    """

    @classmethod
    def get_user_token_stats(cls, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Get token usage statistics for user.

        Provides comprehensive token usage analytics including:
        - Current balance and lifetime statistics
        - Consumption breakdown by transaction reason
        - AI usage breakdown by learning method

        Args:
            user_id: User UUID
            period_days: Period for recent statistics (default: 30 days)

        Returns:
            Statistics dictionary with keys:
            - user_id: The user
            - current_balance: Current token balance
            - total_tokens_used: Lifetime tokens consumed
            - total_tokens_bought: Lifetime tokens purchased
            - total_tokens_granted: Lifetime tokens granted
            - by_reason: Dict of consumption by transaction reason
            - by_method: Dict of AI usage by learning method
            - period_start: Start of analysis period
            - period_end: End of analysis period

        Example:
            >>> stats = TokenAnalyticsRepository.get_user_token_stats(
            ...     'user-123',
            ...     period_days=30
            ... )
            >>> print(f"Balance: {stats['current_balance']}")
            >>> print(f"Used: {stats['total_tokens_used']}")
        """
        period_start = datetime.now() - timedelta(days=period_days)

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get or create wallet to ensure we have latest data
                wallet = TokenWalletRepository.get_or_create_user_wallet(user_id)

                # Get consumption breakdown by transaction reason
                cur.execute("""
                    SELECT
                        description as reason,
                        SUM(ABS(amount)) as total
                    FROM billing_storage.token_transactions
                    WHERE wallet_id = %s
                    AND created_at >= %s
                    AND amount < 0
                    GROUP BY description
                    ORDER BY total DESC
                """, (wallet['wallet_id'], period_start))

                by_reason = {row['reason']: row['total'] for row in cur.fetchall()}

                # Get AI usage breakdown by learning method
                cur.execute("""
                    SELECT
                        lm.name as method_name,
                        SUM(atu.total_tokens) as total
                    FROM ai_token_usage atu
                    JOIN learning_methods lm ON atu.method_id = lm.method_id
                    WHERE atu.user_id = %s
                    AND atu.used_at >= %s
                    GROUP BY lm.name
                    ORDER BY total DESC
                """, (user_id, period_start))

                by_method = {row['method_name']: row['total'] for row in cur.fetchall()}

                return {
                    'user_id': user_id,
                    'current_balance': wallet['balance'],
                    'total_tokens_used': wallet['total_consumed'],
                    'total_tokens_bought': wallet['total_purchased'],
                    'total_tokens_granted': wallet['total_granted'],
                    'by_reason': by_reason,
                    'by_method': by_method,
                    'period_start': period_start,
                    'period_end': datetime.now()
                }

    @classmethod
    def get_org_token_stats(cls, organization_id: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Get token usage statistics for organisation.

        Provides comprehensive token usage analytics for organisation including:
        - Current balance and lifetime statistics
        - Consumption breakdown by transaction reason

        Args:
            organization_id: Organisation UUID
            period_days: Period for recent statistics (default: 30 days)

        Returns:
            Statistics dictionary with keys:
            - organization_id: The organisation
            - current_balance: Current token balance
            - total_tokens_used: Lifetime tokens consumed
            - total_tokens_bought: Lifetime tokens purchased
            - total_tokens_granted: Lifetime tokens granted
            - by_reason: Dict of consumption by transaction reason
            - period_start: Start of analysis period
            - period_end: End of analysis period

        Example:
            >>> stats = TokenAnalyticsRepository.get_org_token_stats(
            ...     'org-123',
            ...     period_days=30
            ... )
            >>> print(f"Balance: {stats['current_balance']}")
        """
        period_start = datetime.now() - timedelta(days=period_days)

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get or create wallet to ensure we have latest data
                wallet = TokenWalletRepository.get_or_create_organisation_wallet(
                    organization_id
                )

                # Get consumption breakdown by transaction reason
                cur.execute("""
                    SELECT
                        description as reason,
                        SUM(ABS(amount)) as total
                    FROM billing_storage.token_transactions
                    WHERE wallet_id = %s
                    AND created_at >= %s
                    AND amount < 0
                    GROUP BY description
                    ORDER BY total DESC
                """, (wallet['wallet_id'], period_start))

                by_reason = {row['reason']: row['total'] for row in cur.fetchall()}

                return {
                    'organization_id': organization_id,
                    'current_balance': wallet['balance'],
                    'total_tokens_used': wallet['total_consumed'],
                    'total_tokens_bought': wallet['total_purchased'],
                    'total_tokens_granted': wallet['total_granted'],
                    'by_reason': by_reason,
                    'period_start': period_start,
                    'period_end': datetime.now()
                }

    @classmethod
    def get_global_token_stats(cls) -> Dict[str, Any]:
        """
        Get global system-wide token usage statistics.

        Provides aggregate statistics across entire system for:
        - Total wallets
        - Aggregate balances and consumption

        Returns:
            Global statistics dictionary with keys:
            - total_wallets: Number of wallets in system
            - total_balance: Sum of all wallet balances
            - total_purchased: Total tokens purchased system-wide
            - total_granted: Total tokens granted system-wide
            - total_consumed: Total tokens consumed system-wide

        Returns:
            Empty dictionaries default to 0 for null aggregates.

        Example:
            >>> stats = TokenAnalyticsRepository.get_global_token_stats()
            >>> print(f"Total wallets: {stats['total_wallets']}")
            >>> print(f"Total system balance: {stats['total_balance']}")
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) as total_wallets,
                        SUM(balance) as total_balance,
                        SUM(total_purchased) as total_purchased,
                        SUM(total_granted) as total_granted,
                        SUM(total_consumed) as total_consumed
                    FROM billing_storage.token_wallets
                """)

                stats = cur.fetchone()

                return {
                    'total_wallets': stats['total_wallets'],
                    'total_balance': stats['total_balance'] or 0,
                    'total_purchased': stats['total_purchased'] or 0,
                    'total_granted': stats['total_granted'] or 0,
                    'total_consumed': stats['total_consumed'] or 0
                }
