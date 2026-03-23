"""
User CRUD Operations

Handles user creation, retrieval, search, and statistics.
"""

from typing import Optional, Dict, List
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query

logger = logging.getLogger(__name__)


class UserCrudRepository(BaseRepository):
    """User CRUD operations (Create, Read, Search)"""

    table_name = 'core.users'
    pk_column = 'user_id'

    @classmethod
    def find_by_id(cls, user_id: str) -> Optional[Dict]:
        """
        Find user by ID

        Args:
            user_id: User ID (UUID)

        Returns:
            User data (without password_hash) or None
            Includes 'role' field derived from user's highest-level group

        Note:
            PHASE B: User roles/permissions are now managed through the groups system.
            The 'role' field is derived from the user's primary group (highest hierarchy).
            Use UserGroupRepository to get user's group memberships.

        Example:
            >>> user = UserCrudRepository.find_by_id('8828daa5-213d-46b9-981a-a1c6f3233afd')
            >>> print(user['email'])
            >>> print(user['role'])  # e.g., 'owner', 'admin', 'user'
        """
        # Get user with their primary group (highest hierarchy level)
        user = fetch_one(
            """
            SELECT
                u.*,
                COALESCE(
                    (SELECT g.slug
                     FROM core.users_groups ug
                     JOIN core.groups g ON ug.group_id = g.id
                     WHERE ug.user_id = u.user_id
                       AND ug.is_active = TRUE
                       AND ug.left_at IS NULL
                     ORDER BY g.hierarchy_level DESC
                     LIMIT 1),
                    'user'
                ) AS role,
                COALESCE(
                    (SELECT g.hierarchy_level
                     FROM core.users_groups ug
                     JOIN core.groups g ON ug.group_id = g.id
                     WHERE ug.user_id = u.user_id
                       AND ug.is_active = TRUE
                       AND ug.left_at IS NULL
                     ORDER BY g.hierarchy_level DESC
                     LIMIT 1),
                    0
                ) AS hierarchy_level
            FROM core.users u
            WHERE u.user_id = %s
            """,
            (user_id,)
        )

        if user:
            user.pop('password_hash', None)
            # Convert UUID to string for Pydantic
            if 'user_id' in user and user['user_id']:
                user['user_id'] = str(user['user_id'])
            # Convert organisation_id UUID to string if present
            if 'organisation_id' in user and user['organisation_id']:
                user['organisation_id'] = str(user['organisation_id'])

        return user

    @classmethod
    def update(cls, user_id: str, data: Dict) -> Optional[Dict]:
        """
        Update user fields

        Args:
            user_id: User ID (UUID)
            data: Dictionary of fields to update

        Returns:
            Updated user data or None
        """
        allowed_fields = {'full_name', 'username', 'email', 'is_active', 'password_hash'}
        filtered = {k: v for k, v in data.items() if k in allowed_fields}

        if not filtered:
            return cls.find_by_id(user_id)

        set_clause = ', '.join(f"{k} = %s" for k in filtered)
        values = list(filtered.values()) + [user_id]

        execute_query(
            f"UPDATE core.users SET {set_clause}, updated_at = NOW() WHERE user_id = %s",
            values
        )

        return cls.find_by_id(user_id)

    @classmethod
    def find_by_email(cls, email: str) -> Optional[Dict]:
        """
        Find user by email

        Args:
            email: User email

        Returns:
            User data (without password_hash) or None
            Includes 'role' field derived from user's highest-level group

        Example:
            >>> user = UserCrudRepository.find_by_email('user@example.com')
        """
        # Get user with their primary group (highest hierarchy level)
        user = fetch_one(
            """
            SELECT
                u.*,
                COALESCE(
                    (SELECT g.slug
                     FROM core.users_groups ug
                     JOIN core.groups g ON ug.group_id = g.id
                     WHERE ug.user_id = u.user_id
                       AND ug.is_active = TRUE
                       AND ug.left_at IS NULL
                     ORDER BY g.hierarchy_level DESC
                     LIMIT 1),
                    'user'
                ) AS role
            FROM core.users u
            WHERE u.email = %s
            """,
            (email,)
        )

        if user:
            user.pop('password_hash', None)
            # Convert UUIDs to strings for Pydantic
            if 'user_id' in user and user['user_id']:
                user['user_id'] = str(user['user_id'])
            if 'organisation_id' in user and user['organisation_id']:
                user['organisation_id'] = str(user['organisation_id'])

        return user

    @classmethod
    def search_users(
        cls,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search users by email, first name, or last name

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching users

        Note:
            PHASE B: Role filtering removed - users are now assigned to groups.
            Use UserGroupRepository to filter by group membership if needed.

        Example:
            >>> users = UserCrudRepository.search_users('john', limit=5)
        """
        search_pattern = f"%{query}%"

        sql = """
            SELECT * FROM core.users
            WHERE (
                email ILIKE %s
                OR firstname ILIKE %s
                OR lastname ILIKE %s
            )
            AND status = 'active'
            LIMIT %s
        """
        params = [search_pattern, search_pattern, search_pattern, limit]

        users = fetch_all(sql, tuple(params))

        # Remove password_hash from all users
        for user in users:
            user.pop('password_hash', None)

        return users

    @classmethod
    def get_user_stats(cls) -> Dict:
        """
        Get user statistics

        Returns:
            Dictionary with user counts by status and admin status

        Note:
            PHASE B: Role-based stats removed. Changed to track by status and is_owner flag.
            For group-based statistics, use UserGroupRepository.

        Example:
            >>> stats = UserCrudRepository.get_user_stats()
            >>> print(f"Total users: {stats['total']}")
            >>> print(f"Admins (is_owner): {stats['admins']}")
        """
        # Total users
        total_result = fetch_one("SELECT COUNT(*) as count FROM core.users")
        total = total_result['count'] if total_result else 0

        # Active users
        active_result = fetch_one("SELECT COUNT(*) as count FROM core.users WHERE status = 'active'")
        active = active_result['count'] if active_result else 0

        # Admin users (is_owner = true)
        admin_result = fetch_one("SELECT COUNT(*) as count FROM core.users WHERE is_owner = true")
        admins = admin_result['count'] if admin_result else 0

        # Email verified
        verified_result = fetch_one(
            "SELECT COUNT(*) as count FROM core.users WHERE email_verified = true AND status = 'active'"
        )
        verified = verified_result['count'] if verified_result else 0

        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'verified': verified,
            'admins': admins
        }

    # =========================================================================
    # TWO-FACTOR AUTHENTICATION
    # =========================================================================

    @classmethod
    def set_two_factor_secret(cls, user_id: str, totp_secret: str) -> None:
        """Store TOTP secret for 2FA setup (before verification)."""
        execute_query(
            "UPDATE core.users SET two_factor_secret = %s WHERE user_id = %s",
            (totp_secret, user_id)
        )

    @classmethod
    def enable_two_factor(cls, user_id: str) -> None:
        """Enable 2FA after successful verification."""
        execute_query(
            "UPDATE core.users SET two_factor_enabled = true WHERE user_id = %s",
            (user_id,)
        )

    @classmethod
    def disable_two_factor(cls, user_id: str) -> None:
        """Disable 2FA and clear secret."""
        execute_query(
            """
            UPDATE core.users
            SET two_factor_enabled = false, two_factor_secret = NULL
            WHERE user_id = %s
            """,
            (user_id,)
        )
