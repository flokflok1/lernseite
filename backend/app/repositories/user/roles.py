"""
User Role and Lifecycle Management

Handles role assignment, user activation/deactivation, and related operations.
"""

from typing import Optional, Dict, List
import logging

from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, fetch_all, execute_query

logger = logging.getLogger(__name__)


class UserRoleRepository(BaseRepository):
    """User role and lifecycle management"""

    table_name = 'core.users'
    pk_column = 'user_id'

    @classmethod
    def find_by_role(cls, role: str, active_only: bool = True) -> List[Dict]:
        """
        Find all users with specific role

        Args:
            role: User role name
            active_only: Only return active users (default: True)

        Returns:
            List of users

        Example:
            >>> admins = UserRoleRepository.find_by_role('admin')
            >>> premium_users = UserRoleRepository.find_by_role('premium', active_only=False)
        """
        # Get role_id from role name
        role_data = fetch_one("SELECT role_id FROM core.roles WHERE role_name = %s", (role,))
        if not role_data:
            return []

        if active_only:
            users = fetch_all(
                "SELECT * FROM core.users WHERE role_id = %s AND status = %s",
                (role_data['role_id'], 'active')
            )
        else:
            users = fetch_all(
                "SELECT * FROM core.users WHERE role_id = %s",
                (role_data['role_id'],)
            )

        # Remove password_hash from all users
        for user in users:
            user.pop('password_hash', None)

        return users

    @classmethod
    def find_by_organisation(cls, organization_id: int, active_only: bool = True) -> List[Dict]:
        """
        Find all users in an organisation

        Args:
            organization_id: Organisation ID
            active_only: Only return active users (default: True)

        Returns:
            List of users

        Example:
            >>> org_users = UserRoleRepository.find_by_organisation(5)
        """
        # Note: users table does NOT have organization_id column
        # This requires querying via organization_members table
        if active_only:
            users = fetch_all(
                """
                SELECT u.* FROM core.users u
                JOIN organisations.organization_members om ON u.user_id = om.user_id
                WHERE om.organization_id = %s AND u.status = %s
                """,
                (organization_id, 'active')
            )
        else:
            users = fetch_all(
                """
                SELECT u.* FROM core.users u
                JOIN organisations.organization_members om ON u.user_id = om.user_id
                WHERE om.organization_id = %s
                """,
                (organization_id,)
            )

        # Remove password_hash from all users
        for user in users:
            user.pop('password_hash', None)

        return users

    @classmethod
    def deactivate_user(cls, user_id: int) -> bool:
        """
        Deactivate user account

        Args:
            user_id: User ID

        Returns:
            bool: True if user deactivated successfully

        Example:
            >>> UserRoleRepository.deactivate_user(123)
        """
        execute_query(
            "UPDATE core.users SET status = %s WHERE user_id = %s",
            ('inactive', user_id)
        )
        return True

    @classmethod
    def activate_user(cls, user_id: int) -> bool:
        """
        Activate user account

        Args:
            user_id: User ID

        Returns:
            bool: True if user activated successfully

        Example:
            >>> UserRoleRepository.activate_user(123)
        """
        execute_query(
            "UPDATE core.users SET status = %s WHERE user_id = %s",
            ('active', user_id)
        )
        return True
