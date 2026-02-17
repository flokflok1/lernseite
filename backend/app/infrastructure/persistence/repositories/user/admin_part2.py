"""
User Admin Moderation Operations

Handles admin moderation and lifecycle operations: ban, unban, delete, creator verification.
Core admin operations (listing, details, groups) are in admin.py.
"""

from typing import Optional
from datetime import datetime
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import execute_query

logger = logging.getLogger(__name__)


class UserAdminModerationRepository(BaseRepository):
    """Admin user moderation and lifecycle operations"""

    table_name = 'core.users'
    pk_column = 'user_id'

    @classmethod
    def admin_ban_user(
        cls,
        user_id: str,
        reason: str,
        banned_until: Optional[datetime],
        banned_by: str
    ) -> bool:
        """
        Ban a user (Admin only)

        Args:
            user_id: User ID to ban
            reason: Reason for ban
            banned_until: Ban expiry (None for permanent)
            banned_by: Admin user ID performing the ban

        Returns:
            bool: True if user banned successfully

        Example:
            >>> UserAdminModerationRepository.admin_ban_user(
            ...     'user-uuid',
            ...     'Violation of terms',
            ...     datetime(2025, 12, 31),
            ...     'admin-uuid'
            ... )
        """
        result = execute_query(
            """
            UPDATE core.users
            SET
                status = 'banned',
                banned_until = %s,
                updated_at = NOW()
            WHERE user_id = %s
            """,
            (banned_until, user_id),
            fetch_one=True
        )

        return result is not None

    @classmethod
    def admin_unban_user(cls, user_id: str, unbanned_by: str) -> bool:
        """
        Unban a user (Admin only)

        Args:
            user_id: User ID to unban
            unbanned_by: Admin user ID performing the unban

        Returns:
            bool: True if user unbanned successfully

        Example:
            >>> UserAdminModerationRepository.admin_unban_user('user-uuid', 'admin-uuid')
        """
        result = execute_query(
            """
            UPDATE core.users
            SET
                status = 'active',
                banned_until = NULL,
                updated_at = NOW()
            WHERE user_id = %s
            """,
            (user_id,),
            fetch_one=True
        )

        return result is not None

    @classmethod
    def admin_delete_user(
        cls,
        user_id: str,
        reason: str,
        deleted_by: str,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a user (Admin only)

        Args:
            user_id: User ID to delete
            reason: Reason for deletion
            deleted_by: Admin user ID performing the deletion
            hard_delete: If True, permanently delete; if False, soft delete

        Returns:
            bool: True if user deleted successfully

        Example:
            >>> UserAdminModerationRepository.admin_delete_user(
            ...     'user-uuid', 'GDPR request', 'admin-uuid', hard_delete=False
            ... )
        """
        if hard_delete:
            # Hard delete - permanently remove user
            result = execute_query(
                "DELETE FROM core.users WHERE user_id = %s",
                (user_id,),
                fetch_one=False
            )
        else:
            # Soft delete - set status to deleted
            result = execute_query(
                """
                UPDATE core.users
                SET
                    status = 'deleted',
                    deleted_at = NOW(),
                    updated_at = NOW()
                WHERE user_id = %s
                """,
                (user_id,),
                fetch_one=True
            )

        return result is not None

    @classmethod
    def admin_verify_creator(
        cls,
        user_id: str,
        verified: bool,
        verified_by: str
    ) -> bool:
        """
        Verify a creator (Admin only)

        Args:
            user_id: Creator user ID
            verified: Verification status
            verified_by: Admin user ID performing the verification

        Returns:
            bool: True if creator verified successfully

        Example:
            >>> UserAdminModerationRepository.admin_verify_creator(
            ...     'user-uuid', True, 'admin-uuid'
            ... )
        """
        result = execute_query(
            """
            UPDATE core.users
            SET
                creator_verified = %s,
                creator_verified_at = CASE WHEN %s THEN NOW() ELSE NULL END,
                updated_at = NOW()
            WHERE user_id = %s
            """,
            (verified, verified, user_id),
            fetch_one=True
        )

        return result is not None
