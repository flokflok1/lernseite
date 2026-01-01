"""
LernsystemX Token Repository

Data access layer for token wallet and transaction operations:
- Token wallet CRUD (user and organisation wallets)
- Token transactions (consumption, purchases, grants)
- Balance management with transaction safety
- Token usage statistics and analytics

Uses:
- Pure psycopg for PostgreSQL access
- Connection pooling for performance
- Transaction management for consistency

ISO 27001:2013 compliant - Token management and billing security
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import psycopg
from psycopg.rows import dict_row

from app.extensions import db_pool


class TokenRepository:
    """
    Token Repository for wallet and transaction management

    All methods use psycopg connection pool and return dictionaries.
    """

    @classmethod
    def get_or_create_user_wallet(cls, user_id: str) -> Dict[str, Any]:
        """
        Get or create token wallet for user

        Args:
            user_id: User UUID

        Returns:
            Wallet dictionary
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Try to get existing wallet
                cur.execute("""
                    SELECT * FROM token_wallets
                    WHERE user_id = %s
                """, (user_id,))

                wallet = cur.fetchone()

                if not wallet:
                    # Create new wallet
                    cur.execute("""
                        INSERT INTO token_wallets (
                            user_id, balance, total_purchased, total_granted, total_consumed
                        ) VALUES (%s, 0, 0, 0, 0)
                        RETURNING *
                    """, (user_id,))

                    wallet = cur.fetchone()
                    conn.commit()

                return wallet

    @classmethod
    def get_or_create_organisation_wallet(cls, organisation_id: str) -> Dict[str, Any]:
        """
        Get or create token wallet for organisation

        Args:
            organisation_id: Organisation UUID

        Returns:
            Wallet dictionary
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Try to get existing wallet
                cur.execute("""
                    SELECT * FROM token_wallets
                    WHERE organization_id = %s
                """, (organisation_id,))

                wallet = cur.fetchone()

                if not wallet:
                    # Create new wallet
                    cur.execute("""
                        INSERT INTO token_wallets (
                            organization_id, balance, total_purchased, total_granted, total_consumed
                        ) VALUES (%s, 0, 0, 0, 0)
                        RETURNING *
                    """, (organisation_id,))

                    wallet = cur.fetchone()
                    conn.commit()

                return wallet

    @classmethod
    def get_wallet_by_id(cls, wallet_id: str) -> Optional[Dict[str, Any]]:
        """Get wallet by UUID"""
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM token_wallets
                    WHERE wallet_id = %s
                """, (wallet_id,))

                return cur.fetchone()

    @classmethod
    def get_wallet_for_user(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Get wallet for user (without creating)"""
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM token_wallets
                    WHERE user_id = %s
                """, (user_id,))

                return cur.fetchone()

    @classmethod
    def get_wallet_for_organisation(cls, organisation_id: str) -> Optional[Dict[str, Any]]:
        """Get wallet for organisation (without creating)"""
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM token_wallets
                    WHERE organization_id = %s
                """, (organisation_id,))

                return cur.fetchone()

    @classmethod
    def change_balance(
        cls,
        wallet_id: str,
        amount: int,
        reason: str,
        meta: Optional[Dict[str, Any]] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Change wallet balance with transaction logging

        Args:
            wallet_id: Wallet ID
            amount: Amount to add (positive) or subtract (negative)
            reason: Transaction reason
            meta: Additional metadata
            reference_type: Reference type (e.g., 'ai_execution')
            reference_id: Reference ID

        Returns:
            Transaction record

        Raises:
            ValueError: If insufficient balance
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Start transaction
                conn.execute("BEGIN")

                try:
                    # Get current wallet with lock
                    cur.execute("""
                        SELECT * FROM token_wallets
                        WHERE wallet_id = %s
                        FOR UPDATE
                    """, (wallet_id,))

                    wallet = cur.fetchone()

                    if not wallet:
                        raise ValueError(f'Wallet {wallet_id} not found')

                    # Check balance for negative amounts
                    new_balance = wallet['balance'] + amount
                    if new_balance < 0:
                        raise ValueError(f'Insufficient balance: {wallet["balance"]} tokens, need {abs(amount)} tokens')

                    # Update wallet balance
                    if amount > 0:
                        # Grant tokens
                        cur.execute("""
                            UPDATE token_wallets
                            SET balance = balance + %s,
                                total_granted = total_granted + %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE wallet_id = %s
                            RETURNING balance
                        """, (amount, amount, wallet_id))
                    else:
                        # Consume tokens
                        cur.execute("""
                            UPDATE token_wallets
                            SET balance = balance + %s,
                                total_consumed = total_consumed + %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE wallet_id = %s
                            RETURNING balance
                        """, (amount, abs(amount), wallet_id))

                    result = cur.fetchone()
                    balance_after = result['balance']

                    # Create transaction record
                    cur.execute("""
                        INSERT INTO token_transactions (
                            wallet_id, user_id, organization_id, transaction_type, amount, balance_after,
                            description, reference_type, reference_id, ai_module
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        RETURNING *
                    """, (
                        wallet_id,
                        wallet['user_id'],
                        wallet['organization_id'],
                        'grant' if amount > 0 else 'consumption',
                        amount,
                        balance_after,
                        reason,
                        reference_type,
                        reference_id,
                        meta.get('ai_module') if meta else None
                    ))

                    transaction = cur.fetchone()

                    conn.commit()
                    return transaction

                except Exception as e:
                    conn.rollback()
                    raise

    @classmethod
    def log_usage_from_ai(
        cls,
        user_id: Optional[str],
        organisation_id: Optional[str],
        method_id: str,
        tokens_used: int,
        provider: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log AI usage (does NOT deduct tokens - use change_balance for that)

        Args:
            user_id: User ID
            organisation_id: Organisation ID
            method_id: Learning method ID
            tokens_used: Tokens consumed
            provider: AI provider
            meta: Additional metadata

        Returns:
            AI usage log record
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Use ai_token_usage table with correct schema
                model = meta.get('model', 'unknown') if meta else 'unknown'
                input_tokens = meta.get('input_tokens', 0) if meta else 0
                output_tokens = meta.get('output_tokens', 0) if meta else 0
                cost_eur = meta.get('cost_eur', 0) if meta else 0

                cur.execute("""
                    INSERT INTO ai_token_usage (
                        user_id, organization_id, method_id,
                        input_tokens, output_tokens, total_tokens,
                        provider, model, cost_eur
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    user_id,
                    organisation_id,
                    method_id,
                    input_tokens,
                    output_tokens,
                    tokens_used,
                    provider,
                    model,
                    cost_eur
                ))

                conn.commit()
                return cur.fetchone()

    @classmethod
    def get_user_token_stats(cls, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Get token usage statistics for user

        Args:
            user_id: User ID
            period_days: Period in days

        Returns:
            Statistics dictionary
        """
        period_start = datetime.now() - timedelta(days=period_days)

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get wallet info
                wallet = cls.get_or_create_user_wallet(user_id)

                # Get transactions by reason
                cur.execute("""
                    SELECT
                        description as reason,
                        SUM(ABS(amount)) as total
                    FROM token_transactions
                    WHERE wallet_id = %s
                    AND created_at >= %s
                    AND amount < 0
                    GROUP BY description
                """, (wallet['wallet_id'], period_start))

                by_reason = {row['reason']: row['total'] for row in cur.fetchall()}

                # Get AI usage by method
                cur.execute("""
                    SELECT
                        lm.name as method_name,
                        SUM(atu.total_tokens) as total
                    FROM ai_token_usage atu
                    JOIN learning_methods lm ON atu.method_id = lm.method_id
                    WHERE atu.user_id = %s
                    AND atu.used_at >= %s
                    GROUP BY lm.name
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
    def get_org_token_stats(cls, organisation_id: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Get token usage statistics for organisation

        Args:
            organisation_id: Organisation UUID
            period_days: Period in days

        Returns:
            Statistics dictionary
        """
        period_start = datetime.now() - timedelta(days=period_days)

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get wallet info
                wallet = cls.get_or_create_organisation_wallet(organisation_id)

                # Get transactions by reason
                cur.execute("""
                    SELECT
                        description as reason,
                        SUM(ABS(amount)) as total
                    FROM token_transactions
                    WHERE wallet_id = %s
                    AND created_at >= %s
                    AND amount < 0
                    GROUP BY description
                """, (wallet['wallet_id'], period_start))

                by_reason = {row['reason']: row['total'] for row in cur.fetchall()}

                return {
                    'organisation_id': organisation_id,
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
        Get global token usage statistics

        Returns:
            Global statistics dictionary
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
                    FROM token_wallets
                """)

                stats = cur.fetchone()

                return {
                    'total_wallets': stats['total_wallets'],
                    'total_balance': stats['total_balance'] or 0,
                    'total_purchased': stats['total_purchased'] or 0,
                    'total_granted': stats['total_granted'] or 0,
                    'total_consumed': stats['total_consumed'] or 0
                }

    @classmethod
    def get_transactions(
        cls,
        wallet_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get transactions for wallet

        Args:
            wallet_id: Wallet ID
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of transaction records
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM token_transactions
                    WHERE wallet_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (wallet_id, limit, offset))

                return cur.fetchall()

    # ============================================================================
    # ADMIN METHODS (Phase B24 - Admin System)
    # ============================================================================

    @classmethod
    def admin_grant_tokens(
        cls,
        user_id: str,
        amount: int,
        reason: str,
        granted_by: str
    ) -> Optional[int]:
        """
        Grant tokens to user as admin (Admin only)

        Args:
            user_id: User ID to grant tokens to
            amount: Number of tokens to grant (positive)
            reason: Reason for granting tokens
            granted_by: Admin user ID granting the tokens

        Returns:
            New token balance, or None if user not found

        Example:
            >>> new_balance = TokenRepository.admin_grant_tokens(
            ...     'user-uuid', 5000, 'Goodwill gesture', 'admin-uuid'
            ... )
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get or create wallet for user
                try:
                    wallet = cls.get_or_create_user_wallet(user_id)
                except Exception:
                    return None

                if not wallet:
                    return None

                # Grant tokens using change_balance
                try:
                    cls.change_balance(
                        wallet_id=wallet['wallet_id'],
                        amount=amount,
                        reason=f"Admin grant: {reason}",
                        meta={'granted_by': granted_by, 'admin_action': True}
                    )

                    # Get updated balance
                    cur.execute("""
                        SELECT balance FROM token_wallets
                        WHERE wallet_id = %s
                    """, (wallet['wallet_id'],))

                    result = cur.fetchone()
                    return result['balance'] if result else None

                except Exception as e:
                    raise ValueError(f"Failed to grant tokens: {str(e)}")
