"""
Token Wallet Repository

Data access layer for token wallet CRUD operations:
- Get or create user/organisation wallets
- Retrieve wallet information
- Wallet lifecycle management

Uses psycopg connection pooling for efficient database access.
"""

from typing import Dict, Any, Optional
from psycopg.rows import dict_row

from app.core.bootstrap.extensions import db_pool


class TokenWalletRepository:
    """
    Token Wallet Repository

    Handles wallet creation, retrieval, and basic wallet operations.
    All methods use psycopg connection pool and return dictionaries.
    """

    @classmethod
    def get_or_create_user_wallet(cls, user_id: str) -> Dict[str, Any]:
        """
        Get or create token wallet for user.

        Creates a new wallet with zero balance if one doesn't exist.

        Args:
            user_id: User UUID

        Returns:
            Wallet dictionary with keys:
            - wallet_id: UUID of the wallet
            - user_id: Associated user UUID
            - balance: Current token balance
            - total_purchased: Total tokens purchased
            - total_granted: Total tokens granted
            - total_consumed: Total tokens consumed

        Raises:
            Exception: On database connection or query error
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Try to get existing wallet
                cur.execute("""
                    SELECT * FROM billing_storage.token_wallets
                    WHERE user_id = %s
                """, (user_id,))

                wallet = cur.fetchone()

                if not wallet:
                    # Create new wallet with zero balance
                    cur.execute("""
                        INSERT INTO billing_storage.token_wallets (
                            user_id, balance, total_purchased, total_granted, total_consumed
                        ) VALUES (%s, 0, 0, 0, 0)
                        RETURNING *
                    """, (user_id,))

                    wallet = cur.fetchone()
                    conn.commit()

                return wallet

    @classmethod
    def get_or_create_organisation_wallet(cls, organization_id: str) -> Dict[str, Any]:
        """
        Get or create token wallet for organisation.

        Creates a new wallet with zero balance if one doesn't exist.

        Args:
            organization_id: Organisation UUID

        Returns:
            Wallet dictionary with keys:
            - wallet_id: UUID of the wallet
            - organization_id: Associated organisation UUID
            - balance: Current token balance
            - total_purchased: Total tokens purchased
            - total_granted: Total tokens granted
            - total_consumed: Total tokens consumed

        Raises:
            Exception: On database connection or query error
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Try to get existing wallet
                cur.execute("""
                    SELECT * FROM billing_storage.token_wallets
                    WHERE organization_id = %s
                """, (organization_id,))

                wallet = cur.fetchone()

                if not wallet:
                    # Create new wallet with zero balance
                    cur.execute("""
                        INSERT INTO billing_storage.token_wallets (
                            organization_id, balance, total_purchased, total_granted, total_consumed
                        ) VALUES (%s, 0, 0, 0, 0)
                        RETURNING *
                    """, (organization_id,))

                    wallet = cur.fetchone()
                    conn.commit()

                return wallet

    @classmethod
    def get_wallet_by_id(cls, wallet_id: str) -> Optional[Dict[str, Any]]:
        """
        Get wallet by UUID.

        Retrieves wallet information without modifying it.

        Args:
            wallet_id: Wallet UUID

        Returns:
            Wallet dictionary if found, None otherwise

        Raises:
            Exception: On database connection or query error
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM billing_storage.token_wallets
                    WHERE wallet_id = %s
                """, (wallet_id,))

                return cur.fetchone()

    @classmethod
    def get_wallet_for_user(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get wallet for user (without creating).

        Retrieves existing wallet without auto-creation.

        Args:
            user_id: User UUID

        Returns:
            Wallet dictionary if found, None otherwise

        Raises:
            Exception: On database connection or query error
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM billing_storage.token_wallets
                    WHERE user_id = %s
                """, (user_id,))

                return cur.fetchone()

    @classmethod
    def get_wallet_for_organisation(cls, organization_id: str) -> Optional[Dict[str, Any]]:
        """
        Get wallet for organisation (without creating).

        Retrieves existing wallet without auto-creation.

        Args:
            organization_id: Organisation UUID

        Returns:
            Wallet dictionary if found, None otherwise

        Raises:
            Exception: On database connection or query error
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT * FROM billing_storage.token_wallets
                    WHERE organization_id = %s
                """, (organization_id,))

                return cur.fetchone()
