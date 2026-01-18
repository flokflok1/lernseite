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
        Find user by ID with role name included

        Args:
            user_id: User ID (UUID)

        Returns:
            User data with role name (without password_hash) or None

        Example:
            >>> user = UserCrudRepository.find_by_id('8828daa5-213d-46b9-981a-a1c6f3233afd')
            >>> print(user['role'])  # 'admin' (not role_id)
        """
        user = fetch_one(
            """
            SELECT u.*, r.role_name as role, r.hierarchy_level
            FROM core.users u
            JOIN core.roles r ON u.role_id = r.role_id
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
        limit: int = 10,
        role: Optional[str] = None
    ) -> List[Dict]:
        """
        Search users by email, first name, or last name

        Args:
            query: Search query
            limit: Maximum number of results
            role: Filter by role name (optional)

        Returns:
            List of matching users

        Example:
            >>> users = UserCrudRepository.search_users('john', limit=5)
            >>> admins = UserCrudRepository.search_users('john', role='admin')
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
        """
        params = [search_pattern, search_pattern, search_pattern]

        if role:
            # Get role_id from role name
            role_data = fetch_one("SELECT role_id FROM core.roles WHERE role_name = %s", (role,))
            if role_data:
                sql += " AND role_id = %s"
                params.append(role_data['role_id'])

        sql += f" LIMIT {limit}"

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
            Dictionary with user counts by role and status

        Example:
            >>> stats = UserCrudRepository.get_user_stats()
            >>> print(f"Total users: {stats['total']}")
            >>> print(f"Premium users: {stats['by_role']['premium']}")
        """
        # Total users
        total_result = fetch_one("SELECT COUNT(*) as count FROM users")
        total = total_result['count'] if total_result else 0

        # Active users
        active_result = fetch_one("SELECT COUNT(*) as count FROM core.users WHERE status = 'active'")
        active = active_result['count'] if active_result else 0

        # Users by role (with role names)
        by_role_query = """
            SELECT r.role_name, COUNT(u.user_id) as count
            FROM core.users u
            JOIN core.roles r ON u.role_id = r.role_id
            WHERE u.status = 'active'
            GROUP BY r.role_name
        """
        by_role = fetch_all(by_role_query)
        by_role_dict = {row['role_name']: row['count'] for row in by_role}

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
            'by_role': by_role_dict
        }
