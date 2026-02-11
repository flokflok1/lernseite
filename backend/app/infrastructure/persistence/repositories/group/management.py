"""
Group Management Operations - Admin-Level Group Management

Advanced group operations: batch operations, permission management, analytics.

PHASE B: Administrative interface for RBAC 3.0 group-based system.
"""

from typing import Optional, Dict, List
from datetime import datetime
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query

logger = logging.getLogger(__name__)


class GroupManagementRepository(BaseRepository):
    """Advanced group management operations for administrators"""

    table_name = 'core.groups'
    pk_column = 'group_id'

    # =====================================================
    # Batch User Operations
    # =====================================================

    @classmethod
    def add_users_to_group(
        cls,
        group_id: str,
        user_ids: List[str],
        added_by: str
    ) -> Dict:
        """
        Add multiple users to group

        Args:
            group_id: Group ID
            user_ids: List of user IDs to add
            added_by: Admin user ID performing the operation

        Returns:
            Dict with 'added', 'already_members', 'not_found' counts

        Example:
            >>> result = GroupManagementRepository.add_users_to_group(
            ...     'group-uuid',
            ...     ['user-1', 'user-2', 'user-3'],
            ...     'admin-uuid'
            ... )
            >>> print(f"Added: {result['added']}, Already members: {result['already_members']}")
        """
        if not user_ids:
            return {'added': 0, 'already_members': 0, 'not_found': 0}

        # Check which users exist
        existing_users = fetch_all(
            "SELECT user_id FROM core.users WHERE user_id = ANY(%s)",
            (user_ids,)
        ) or []
        existing_user_ids = {u['user_id'] for u in existing_users}

        # Get already members
        already_members = fetch_all(
            """
            SELECT DISTINCT user_id
            FROM core.users_groups
            WHERE group_id = %s AND user_id = ANY(%s)
            """,
            (group_id, user_ids)
        ) or []
        already_member_ids = {u['user_id'] for u in already_members}

        # Add new members
        to_add = [uid for uid in user_ids if uid in existing_user_ids and uid not in already_member_ids]

        added_count = 0
        for user_id in to_add:
            result = execute_query(
                """
                INSERT INTO core.users_groups (group_id, user_id, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (group_id, user_id) DO NOTHING
                """,
                (group_id, user_id)
            )
            if result:
                added_count += 1

        not_found = len(user_ids) - len(existing_user_ids)

        return {
            'added': added_count,
            'already_members': len(already_member_ids),
            'not_found': not_found
        }

    @classmethod
    def remove_users_from_group(
        cls,
        group_id: str,
        user_ids: List[str],
        removed_by: str
    ) -> Dict:
        """
        Remove multiple users from group

        Args:
            group_id: Group ID
            user_ids: List of user IDs to remove
            removed_by: Admin user ID performing the operation

        Returns:
            Dict with 'removed', 'not_members', 'not_found' counts

        Example:
            >>> result = GroupManagementRepository.remove_users_from_group(
            ...     'group-uuid',
            ...     ['user-1', 'user-2'],
            ...     'admin-uuid'
            ... )
        """
        if not user_ids:
            return {'removed': 0, 'not_members': 0, 'not_found': 0}

        # Check which users exist
        existing_users = fetch_all(
            "SELECT user_id FROM core.users WHERE user_id = ANY(%s)",
            (user_ids,)
        ) or []
        existing_user_ids = {u['user_id'] for u in existing_users}

        # Get current members
        current_members = fetch_all(
            """
            SELECT DISTINCT user_id
            FROM core.users_groups
            WHERE group_id = %s AND user_id = ANY(%s)
            """,
            (group_id, user_ids)
        ) or []
        current_member_ids = {u['user_id'] for u in current_members}

        # Remove members
        removed_count = 0
        for user_id in current_member_ids:
            result = execute_query(
                "DELETE FROM core.users_groups WHERE group_id = %s AND user_id = %s",
                (group_id, user_id)
            )
            if result:
                removed_count += 1

        not_members = len(existing_user_ids) - len(current_member_ids)
        not_found = len(user_ids) - len(existing_user_ids)

        return {
            'removed': removed_count,
            'not_members': not_members,
            'not_found': not_found
        }

    @classmethod
    def replace_group_members(
        cls,
        group_id: str,
        user_ids: List[str],
        replaced_by: str
    ) -> bool:
        """
        Replace all group members with new list

        Args:
            group_id: Group ID
            user_ids: New list of user IDs
            replaced_by: Admin user ID performing the operation

        Returns:
            True if successful

        Example:
            >>> GroupManagementRepository.replace_group_members(
            ...     'group-uuid',
            ...     ['user-1', 'user-2', 'user-3'],
            ...     'admin-uuid'
            ... )
        """
        # Delete all current members
        execute_query(
            "DELETE FROM core.users_groups WHERE group_id = %s",
            (group_id,)
        )

        # Add new members
        if user_ids:
            result = cls.add_users_to_group(group_id, user_ids, replaced_by)
            return result['added'] > 0

        return True

    # =====================================================
    # Permission Management
    # =====================================================

    @classmethod
    def assign_permission_to_group(
        cls,
        group_id: str,
        permission_key: str,
        assigned_by: str
    ) -> bool:
        """
        Assign permission to group

        Args:
            group_id: Group ID
            permission_key: Permission key (e.g., 'admin:users.delete')
            assigned_by: Admin user ID

        Returns:
            True if assigned successfully

        Example:
            >>> GroupManagementRepository.assign_permission_to_group(
            ...     'group-uuid',
            ...     'admin:users.delete',
            ...     'admin-uuid'
            ... )
        """
        result = execute_query(
            """
            INSERT INTO core.group_permissions (group_id, permission_key, created_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (group_id, permission_key) DO NOTHING
            """,
            (group_id, permission_key)
        )

        return result is not None

    @classmethod
    def revoke_permission_from_group(
        cls,
        group_id: str,
        permission_key: str,
        revoked_by: str
    ) -> bool:
        """
        Revoke permission from group

        Args:
            group_id: Group ID
            permission_key: Permission key
            revoked_by: Admin user ID

        Returns:
            True if revoked successfully

        Example:
            >>> GroupManagementRepository.revoke_permission_from_group(
            ...     'group-uuid',
            ...     'admin:users.delete',
            ...     'admin-uuid'
            ... )
        """
        result = execute_query(
            "DELETE FROM core.group_permissions WHERE group_id = %s AND permission_key = %s",
            (group_id, permission_key)
        )

        return result is not None

    @classmethod
    def get_group_permissions(cls, group_id: str) -> List[str]:
        """
        Get all permissions assigned to group

        Args:
            group_id: Group ID

        Returns:
            List of permission keys

        Example:
            >>> perms = GroupManagementRepository.get_group_permissions('group-uuid')
            >>> print(perms)  # ['admin:users', 'courses:edit', ...]
        """
        results = fetch_all(
            """
            SELECT permission_key
            FROM core.group_permissions
            WHERE group_id = %s
            ORDER BY permission_key ASC
            """,
            (group_id,)
        ) or []

        return [r['permission_key'] for r in results]

    @classmethod
    def batch_assign_permissions(
        cls,
        group_id: str,
        permission_keys: List[str],
        assigned_by: str
    ) -> Dict:
        """
        Assign multiple permissions to group

        Args:
            group_id: Group ID
            permission_keys: List of permission keys
            assigned_by: Admin user ID

        Returns:
            Dict with 'assigned', 'already_granted' counts

        Example:
            >>> result = GroupManagementRepository.batch_assign_permissions(
            ...     'group-uuid',
            ...     ['admin:users', 'admin:courses', 'admin:analytics'],
            ...     'admin-uuid'
            ... )
        """
        if not permission_keys:
            return {'assigned': 0, 'already_granted': 0}

        # Get existing permissions
        existing = fetch_all(
            """
            SELECT permission_key
            FROM core.group_permissions
            WHERE group_id = %s AND permission_key = ANY(%s)
            """,
            (group_id, permission_keys)
        ) or []
        existing_perms = {p['permission_key'] for p in existing}

        # Assign new permissions
        assigned_count = 0
        for perm_key in permission_keys:
            if perm_key not in existing_perms:
                result = execute_query(
                    """
                    INSERT INTO core.group_permissions (group_id, permission_key, created_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (group_id, permission_key) DO NOTHING
                    """,
                    (group_id, perm_key)
                )
                if result:
                    assigned_count += 1

        return {
            'assigned': assigned_count,
            'already_granted': len(existing_perms)
        }

    # =====================================================
    # Group Audit & Analytics
    # =====================================================

    @classmethod
    def get_group_activity(
        cls,
        group_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get recent activity for group

        Args:
            group_id: Group ID
            limit: Max activity records

        Returns:
            List of activity records

        Example:
            >>> activity = GroupManagementRepository.get_group_activity('group-uuid')
        """
        return fetch_all(
            """
            SELECT
                user_id,
                action,
                description,
                created_at,
                metadata
            FROM core.audit_logs
            WHERE
                (action LIKE 'group.%' OR action LIKE 'admin.groups.%')
                AND metadata->>'group_id' = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (group_id, limit)
        ) or []

    @classmethod
    def search_groups(
        cls,
        query: str,
        organisation_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search groups by name or slug

        Args:
            query: Search query
            organisation_id: Filter by organisation
            limit: Max results

        Returns:
            List of matching group dictionaries

        Example:
            >>> results = GroupManagementRepository.search_groups('premium', org_id)
        """
        where_clause = "WHERE (name ILIKE %s OR slug ILIKE %s)"
        params = [f"%{query}%", f"%{query}%"]

        if organisation_id:
            where_clause += " AND organisation_id = %s"
            params.append(organisation_id)

        where_clause += " ORDER BY name ASC LIMIT %s"
        params.append(limit)

        return fetch_all(
            f"""
            SELECT
                group_id,
                organisation_id,
                name,
                slug,
                description,
                group_type,
                is_system_group,
                created_at
            FROM core.groups
            {where_clause}
            """,
            tuple(params)
        ) or []

    @classmethod
    def export_group_membership(
        cls,
        group_id: str,
        format: str = 'json'
    ) -> Optional[List[Dict]]:
        """
        Export group membership data

        Args:
            group_id: Group ID
            format: Export format (json, csv)

        Returns:
            List of member data dictionaries

        Example:
            >>> members = GroupManagementRepository.export_group_membership('group-uuid')
        """
        members = fetch_all(
            """
            SELECT
                u.user_id,
                u.email,
                u.firstname,
                u.lastname,
                u.status,
                ug.created_at as joined_date
            FROM core.users_groups ug
            JOIN core.users u ON ug.user_id = u.user_id
            WHERE ug.group_id = %s
            ORDER BY u.lastname, u.firstname
            """,
            (group_id,)
        ) or []

        # Convert UUIDs to strings
        for member in members:
            if 'user_id' in member:
                member['user_id'] = str(member['user_id'])

        return members
