"""
Token Transaction Repository

Data access layer for token balance changes and transaction logging:
- Update wallet balances with transaction safety
- Log token consumption and grants
- Record AI usage for billing and analytics

ISO 27001:2013 compliant - Transaction management and data integrity.

Uses psycopg connection pooling with explicit transaction management.
"""

from typing import Dict, Any, Optional
from psycopg.rows import dict_row

from app.extensions import db_pool
from .wallet import TokenWalletRepository


class TokenTransactionRepository:
    """
    Token Transaction Repository

    Handles balance changes, transaction recording, and AI usage logging.
    All operations use explicit transaction control for data consistency.
    """

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
        Change wallet balance with transaction logging.

        Updates wallet balance atomically and creates transaction record.
        Validates sufficient balance for negative amounts (withdrawals).

        Args:
            wallet_id: Wallet UUID to modify
            amount: Amount to add (positive) or subtract (negative)
            reason: Transaction reason/description
            meta: Additional metadata (e.g., {'ai_module': 'content_gen'})
            reference_type: Reference type (e.g., 'ai_execution', 'purchase')
            reference_id: Reference ID for traceability

        Returns:
            Transaction dictionary with keys:
            - transaction_id: UUID of the transaction
            - wallet_id: Associated wallet
            - amount: Transaction amount
            - balance_after: Wallet balance after transaction
            - transaction_type: 'grant' or 'consumption'
            - created_at: Transaction timestamp

        Raises:
            ValueError: If wallet not found or insufficient balance for withdrawal

        Example:
            >>> transaction = TokenTransactionRepository.change_balance(
            ...     'wallet-uuid',
            ...     -500,
            ...     'AI module execution',
            ...     meta={'ai_module': 'content_generation'},
            ...     reference_type='ai_execution',
            ...     reference_id='job-123'
            ... )
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Start transaction
                conn.execute("BEGIN")

                try:
                    # Get current wallet with row lock for consistency
                    cur.execute("""
                        SELECT * FROM billing_storage.token_wallets
                        WHERE wallet_id = %s
                        FOR UPDATE
                    """, (wallet_id,))

                    wallet = cur.fetchone()

                    if not wallet:
                        raise ValueError(f'Wallet {wallet_id} not found')

                    # Validate sufficient balance for withdrawals
                    new_balance = wallet['balance'] + amount
                    if new_balance < 0:
                        raise ValueError(
                            f'Insufficient balance: {wallet["balance"]} tokens, '
                            f'need {abs(amount)} tokens'
                        )

                    # Update wallet balance based on transaction type
                    if amount > 0:
                        # Grant tokens (increase total_granted counter)
                        cur.execute("""
                            UPDATE billing_storage.token_wallets
                            SET balance = balance + %s,
                                total_granted = total_granted + %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE wallet_id = %s
                            RETURNING balance
                        """, (amount, amount, wallet_id))
                    else:
                        # Consume tokens (increase total_consumed counter)
                        cur.execute("""
                            UPDATE billing_storage.token_wallets
                            SET balance = balance + %s,
                                total_consumed = total_consumed + %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE wallet_id = %s
                            RETURNING balance
                        """, (amount, abs(amount), wallet_id))

                    result = cur.fetchone()
                    balance_after = result['balance']

                    # Create transaction record for audit trail
                    cur.execute("""
                        INSERT INTO billing_storage.token_transactions (
                            wallet_id, user_id, organization_id, transaction_type, amount,
                            balance_after, description, reference_type, reference_id, ai_module
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
        organization_id: Optional[str],
        method_id: str,
        tokens_used: int,
        provider: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log AI usage and token consumption.

        Records AI model execution for billing and analytics.
        Does NOT deduct tokens - use change_balance() for wallet updates.

        Args:
            user_id: User UUID (may be None for org-level requests)
            organization_id: Organisation UUID (may be None for user requests)
            method_id: Learning method ID or AI operation type
            tokens_used: Total tokens consumed
            provider: AI provider ('anthropic', 'openai', 'deepl', etc.)
            meta: Additional metadata containing:
                - model: Model name (e.g., 'claude-opus-4.5')
                - input_tokens: Input token count
                - output_tokens: Output token count
                - cost_eur: Estimated cost in EUR

        Returns:
            AI usage log dictionary with keys:
            - usage_id: UUID of the usage record
            - user_id: Associated user
            - organization_id: Associated organisation
            - total_tokens: Tokens used
            - provider: AI provider
            - model: Model used
            - cost_eur: Cost in EUR

        Raises:
            Exception: On database connection or query error

        Example:
            >>> usage = TokenTransactionRepository.log_usage_from_ai(
            ...     user_id='user-123',
            ...     organization_id=None,
            ...     method_id='LM00',
            ...     tokens_used=4500,
            ...     provider='anthropic',
            ...     meta={
            ...         'model': 'claude-opus-4.5',
            ...         'input_tokens': 2000,
            ...         'output_tokens': 2500,
            ...         'cost_eur': 0.18
            ...     }
            ... )
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Extract metadata with safe defaults
                model = meta.get('model', 'unknown') if meta else 'unknown'
                input_tokens = meta.get('input_tokens', 0) if meta else 0
                output_tokens = meta.get('output_tokens', 0) if meta else 0
                cost_eur = meta.get('cost_eur', 0) if meta else 0

                # Record AI usage for analytics and cost tracking
                cur.execute("""
                    INSERT INTO ai_token_usage (
                        user_id, organization_id, method_id,
                        input_tokens, output_tokens, total_tokens,
                        provider, model, cost_eur
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    user_id,
                    organization_id,
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
    def get_transactions(
        cls,
        wallet_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[Dict[str, Any]]:
        """
        Get transaction history for wallet.

        Retrieves paginated transaction records in reverse chronological order.

        Args:
            wallet_id: Wallet UUID
            limit: Maximum number of records (default: 50)
            offset: Result offset for pagination (default: 0)

        Returns:
            List of transaction dictionaries with keys:
            - transaction_id: UUID
            - wallet_id: Associated wallet
            - transaction_type: 'grant' or 'consumption'
            - amount: Transaction amount
            - balance_after: Wallet balance after transaction
            - description: Transaction reason
            - created_at: Transaction timestamp

        Raises:
            Exception: On database connection or query error

        Example:
            >>> transactions = TokenTransactionRepository.get_transactions(
            ...     'wallet-123',
            ...     limit=100,
            ...     offset=0
            ... )
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM billing_storage.token_transactions
                    WHERE wallet_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (wallet_id, limit, offset))

                return cur.fetchall()
