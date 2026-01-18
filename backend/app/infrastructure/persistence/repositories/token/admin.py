"""
Token Admin Repository

Admin-only data access layer for token administration:
- Grant tokens to users as admin action
- Admin-level token adjustments and auditing

ISO 27001:2013 compliant - Admin actions with audit trails.

Uses psycopg connection pooling with explicit transaction management.
"""

from typing import Optional
from psycopg.rows import dict_row

from app.core.bootstrap.extensions import db_pool
from .wallet import TokenWalletRepository
from .transactions import TokenTransactionRepository


class TokenAdminRepository:
    """
    Token Admin Repository

    Provides admin-level token management operations with full audit trails.
    Restricted to admin users via RBAC middleware.
    """

    @classmethod
    def admin_grant_tokens(
        cls,
        user_id: str,
        amount: int,
        reason: str,
        granted_by: str
    ) -> Optional[int]:
        """
        Grant tokens to user as admin action.

        Admin-only operation to add tokens to user account.
        All grants are logged with admin user ID for audit trail.

        Args:
            user_id: User UUID to grant tokens to
            amount: Number of tokens to grant (must be positive)
            reason: Admin reason for granting tokens
            granted_by: Admin user UUID performing the grant

        Returns:
            New token balance after grant, or None if user not found

        Raises:
            ValueError: If amount is not positive or grant fails

        Example:
            >>> new_balance = TokenAdminRepository.admin_grant_tokens(
            ...     user_id='user-uuid',
            ...     amount=5000,
            ...     reason='Goodwill gesture for support issue',
            ...     granted_by='admin-uuid'
            ... )
            >>> print(f"New balance: {new_balance} tokens")
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                try:
                    # Get or create wallet for user
                    wallet = TokenWalletRepository.get_or_create_user_wallet(user_id)

                    if not wallet:
                        return None

                    # Grant tokens using transaction repository
                    # This ensures proper balance updates and audit logging
                    TokenTransactionRepository.change_balance(
                        wallet_id=wallet['wallet_id'],
                        amount=amount,
                        reason=f"Admin grant: {reason}",
                        meta={
                            'granted_by': granted_by,
                            'admin_action': True
                        }
                    )

                    # Get updated balance for confirmation
                    cur.execute("""
                        SELECT balance FROM billing_storage.token_wallets
                        WHERE wallet_id = %s
                    """, (wallet['wallet_id'],))

                    result = cur.fetchone()
                    return result['balance'] if result else None

                except Exception as e:
                    raise ValueError(f"Failed to grant tokens: {str(e)}")
