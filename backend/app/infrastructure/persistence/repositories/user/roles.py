"""
User Role and Lifecycle Management

Handles role assignment, user activation/deactivation, and related operations.
"""

from typing import Optional, Dict, List
import logging

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query

logger = logging.getLogger(__name__)


class UserRoleRepository(BaseRepository):
    """User role and lifecycle management"""

    table_name = 'core.users'
    pk_column = 'user_id'

    @classmethod
    def find_by_group(cls, group_slug: str, active_only: bool = True) -> List[Dict]:
        """
        Find all users in a specific group

        Args:
            group_slug: Group slug (e.g., 'system-admin', 'premium-members')
            active_only: Only return active users (default: True)

        Returns:
            List of users

        Note:
            PHASE B: Replaces find_by_role() which used deleted core.roles table.
            Users are now organized through core.users_groups junction table.

        Example:
            >>> admins = UserRoleRepository.find_by_group('system-admin')
            >>> premium_users = UserRoleRepository.find_by_group('premium-members', active_only=False)
        """
        if active_only:
            users = fetch_all(
                """
                SELECT DISTINCT u.* FROM core.users u
                JOIN core.users_groups ug ON u.user_id = ug.user_id
                JOIN core.groups g ON ug.group_id = g.group_id
                WHERE g.slug = %s AND u.status = %s
                """,
                (group_slug, 'active')
            )
        else:
            users = fetch_all(
                """
                SELECT DISTINCT u.* FROM core.users u
                JOIN core.users_groups ug ON u.user_id = ug.user_id
                JOIN core.groups g ON ug.group_id = g.group_id
                WHERE g.slug = %s
                """,
                (group_slug,)
            )

        # Remove password_hash from all users
        for user in users:
            user.pop('password_hash', None)

        return users

    @classmethod
    def find_by_organisation(cls, organisation_id: int, active_only: bool = True) -> List[Dict]:
        """
        Find all users in an organisation

        Args:
            organisation_id: Organisation ID
            active_only: Only return active users (default: True)

        Returns:
            List of users

        Example:
            >>> org_users = UserRoleRepository.find_by_organisation(5)
        """
        # Note: users table does NOT have organisation_id column
        # This requires querying via organisation_members table
        if active_only:
            users = fetch_all(
                """
                SELECT u.* FROM core.users u
                JOIN organisations.organisation_members om ON u.user_id = om.user_id
                WHERE om.organisation_id = %s AND u.status = %s
                """,
                (organisation_id, 'active')
            )
        else:
            users = fetch_all(
                """
                SELECT u.* FROM core.users u
                JOIN organisations.organisation_members om ON u.user_id = om.user_id
                WHERE om.organisation_id = %s
                """,
                (organisation_id,)
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
