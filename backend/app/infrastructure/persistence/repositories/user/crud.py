"""
User CRUD Operations

Handles user creation, retrieval, search, and statistics.
"""

from typing import Optional, Dict, List
import logging

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
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

        Note:
            PHASE B: User roles/permissions are now managed through the groups system.
            Use UserGroupRepository to get user's group memberships.

        Example:
            >>> user = UserCrudRepository.find_by_id('8828daa5-213d-46b9-981a-a1c6f3233afd')
            >>> print(user['email'])
        """
        user = fetch_one(
            """
            SELECT u.*
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

        return user

    @classmethod
    def find_by_email(cls, email: str) -> Optional[Dict]:
        """
        Find user by email

        Args:
            email: User email

        Returns:
            User data (without password_hash) or None

        Example:
            >>> user = UserCrudRepository.find_by_email('user@example.com')
        """
        user = fetch_one("SELECT * FROM core.users WHERE email = %s", (email,))

        if user:
            user.pop('password_hash', None)

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
