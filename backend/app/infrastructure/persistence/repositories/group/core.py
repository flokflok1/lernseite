"""
Group Repository - Database Access for Group Management

Implements RBAC 3.0 group-based authorization.
Handles group CRUD, membership management, and hierarchy operations.

PHASE B: Complete group-based system replaces RBAC 2.0 role-based system.
"""

from typing import Optional, Dict, List
from datetime import datetime
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query

logger = logging.getLogger(__name__)


class GroupRepository(BaseRepository):
    """Repository for group management operations"""

    table_name = 'core.groups'
    pk_column = 'group_id'

    # =====================================================
    # Core Group Operations
    # =====================================================

    @classmethod
    def find_by_id(cls, group_id: str) -> Optional[Dict]:
        """
        Get group by ID

        Args:
            group_id: Group ID (UUID)

        Returns:
            Group data dictionary or None if not found

        Example:
            >>> group = GroupRepository.find_by_id('group-uuid')
            >>> print(group['name'])
        """
        return fetch_one(
            """
            SELECT
                group_id,
                organisation_id,
                name,
                slug,
                description,
                group_type,
                is_system_group,
                is_protected,
                parent_group_id,
                metadata,
                created_at,
                updated_at
            FROM core.groups
            WHERE group_id = %s
            """,
            (group_id,)
        )

    @classmethod
    def find_by_slug(cls, slug: str, organisation_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get group by slug

        Args:
            slug: Group slug (unique identifier)
            organisation_id: Optional org ID for org-scoped lookup

        Returns:
            Group data dictionary or None if not found

        Example:
            >>> admin_group = GroupRepository.find_by_slug('system-admin')
            >>> student_group = GroupRepository.find_by_slug('premium-members', org_id)
        """
        if organisation_id:
            return fetch_one(
                """
                SELECT
                    group_id,
                    organisation_id,
                    name,
                    slug,
                    description,
                    group_type,
                    is_system_group,
                    is_protected,
                    parent_group_id,
                    metadata,
                    created_at,
                    updated_at
                FROM core.groups
                WHERE slug = %s AND organisation_id = %s
                """,
                (slug, organisation_id)
            )
        else:
            return fetch_one(
                """
                SELECT
                    group_id,
                    organisation_id,
                    name,
                    slug,
                    description,
                    group_type,
                    is_system_group,
                    is_protected,
                    parent_group_id,
                    metadata,
                    created_at,
                    updated_at
                FROM core.groups
                WHERE slug = %s
                """,
                (slug,)
            )

    @classmethod
    def find_all(
        cls,
        organisation_id: Optional[str] = None,
        group_type: Optional[str] = None,
        include_system: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        List all groups with optional filters

        Args:
            organisation_id: Filter by organisation (None for system groups)
            group_type: Filter by group type (department, class, team, custom, etc.)
            include_system: Include system groups in results
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            List of group dictionaries

        Example:
            >>> org_groups = GroupRepository.find_all(organisation_id='org-uuid')
            >>> system_groups = GroupRepository.find_all(organisation_id=None)
        """
        where_conditions = []
        params = []

        if organisation_id is not None:
            where_conditions.append("organisation_id = %s")
            params.append(organisation_id)

        if group_type:
            where_conditions.append("group_type = %s")
            params.append(group_type)

        if not include_system:
            where_conditions.append("is_system_group = false")

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        query = f"""
            SELECT
                group_id,
                organisation_id,
                name,
                slug,
                description,
                group_type,
                is_system_group,
                is_protected,
                parent_group_id,
                metadata,
                created_at,
                updated_at
            FROM core.groups
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        return fetch_all(query, tuple(params)) or []

    @classmethod
    def create(
        cls,
        name: str,
        slug: str,
        organisation_id: Optional[str],
        group_type: str = 'custom',
        description: Optional[str] = None,
        parent_group_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Create new group

        Args:
            name: Group name
            slug: Unique identifier (URL-safe)
            organisation_id: Organisation ID (None for system groups)
            group_type: Type of group (department, class, team, custom, etc.)
            description: Group description
            parent_group_id: Parent group ID for hierarchy
            metadata: Additional group-specific configuration

        Returns:
            Created group dictionary or None if failed

        Example:
            >>> group = GroupRepository.create(
            ...     name='Premium Members',
            ...     slug='premium-members',
            ...     organisation_id='org-uuid',
            ...     group_type='custom',
            ...     description='Premium tier members'
            ... )
        """
        return fetch_one(
            """
            INSERT INTO core.groups (
                organisation_id,
                name,
                slug,
                description,
                group_type,
                parent_group_id,
                is_system_group,
                is_protected,
                metadata,
                created_at,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, false, false, %s, NOW(), NOW())
            RETURNING
                group_id,
                organisation_id,
                name,
                slug,
                description,
                group_type,
                is_system_group,
                is_protected,
                parent_group_id,
                metadata,
                created_at,
                updated_at
            """,
            (organisation_id, name, slug, description, group_type, parent_group_id, metadata)
        )

    @classmethod
    def update(
        cls,
        group_id: str,
        updates: Dict
    ) -> Optional[Dict]:
        """
        Update group properties

        Args:
            group_id: Group ID to update
            updates: Dictionary of field=value pairs to update
                    Supported: name, description, metadata, parent_group_id

        Returns:
            Updated group dictionary or None if not found

        Example:
            >>> updated = GroupRepository.update(
            ...     'group-uuid',
            ...     {'name': 'New Name', 'description': 'New description'}
            ... )
        """
        # Build update clause
        set_clauses = []
        params = []

        allowed_fields = {'name', 'description', 'metadata', 'parent_group_id'}
        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = %s")
                params.append(value)

        if not set_clauses:
            return cls.find_by_id(group_id)

        set_clause = ", ".join(set_clauses)
        params.append(group_id)

        return fetch_one(
            f"""
            UPDATE core.groups
            SET {set_clause}, updated_at = NOW()
            WHERE group_id = %s
            RETURNING
                group_id,
                organisation_id,
                name,
                slug,
                description,
                group_type,
                is_system_group,
                is_protected,
                parent_group_id,
                metadata,
                created_at,
                updated_at
            """,
            tuple(params)
        )

    @classmethod
    def delete(cls, group_id: str) -> bool:
        """
        Delete group (soft delete - sets deleted_at)

        Args:
            group_id: Group ID to delete

        Returns:
            True if deleted successfully

        Note:
            - Cannot delete system groups (is_system_group = true)
            - Cannot delete protected groups (is_protected = true)
            - Will fail if users still members of group
        """
        # Check if group exists and is not protected
        group = cls.find_by_id(group_id)
        if not group:
            return False

        if group.get('is_system_group') or group.get('is_protected'):
            logger.warning(f"Attempt to delete protected group {group_id}")
            return False

        # Check if group has members
        member_count = fetch_one(
            "SELECT COUNT(*) as count FROM core.users_groups WHERE group_id = %s",
            (group_id,)
        )

        if member_count and member_count['count'] > 0:
            logger.warning(f"Cannot delete group {group_id} with {member_count['count']} members")
            return False

        # Soft delete
        result = execute_query(
            "UPDATE core.groups SET deleted_at = NOW() WHERE group_id = %s",
            (group_id,)
        )

        return result is not None

    # =====================================================
    # Group Membership Operations
    # =====================================================

    @classmethod
    def add_user(cls, group_id: str, user_id: str) -> bool:
        """
        Add user to group

        Args:
            group_id: Group ID
            user_id: User ID to add

        Returns:
            True if user added successfully

        Example:
            >>> GroupRepository.add_user('group-uuid', 'user-uuid')
        """
        result = execute_query(
            """
            INSERT INTO core.users_groups (group_id, user_id, created_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (group_id, user_id) DO NOTHING
            """,
            (group_id, user_id)
        )

        return result is not None

    @classmethod
    def remove_user(cls, group_id: str, user_id: str) -> bool:
        """
        Remove user from group

        Args:
            group_id: Group ID
            user_id: User ID to remove

        Returns:
            True if user removed successfully

        Example:
            >>> GroupRepository.remove_user('group-uuid', 'user-uuid')
        """
        result = execute_query(
            "DELETE FROM core.users_groups WHERE group_id = %s AND user_id = %s",
            (group_id, user_id)
        )

        return result is not None

    @classmethod
    def get_members(
        cls,
        group_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        Get group members with pagination

        Args:
            group_id: Group ID
            limit: Max results
            offset: Results to skip

        Returns:
            Dict with 'members' list and 'total' count

        Example:
            >>> result = GroupRepository.get_members('group-uuid')
            >>> print(f"Members: {len(result['members'])}")
        """
        # Get total count
        total_result = fetch_one(
            "SELECT COUNT(*) as count FROM core.users_groups WHERE group_id = %s",
            (group_id,)
        )
        total = total_result['count'] if total_result else 0

        # Get members
        members = fetch_all(
            """
            SELECT
                u.user_id,
                u.email,
                u.firstname,
                u.lastname,
                u.status,
                ug.created_at as joined_at
            FROM core.users_groups ug
            JOIN core.users u ON ug.user_id = u.user_id
            WHERE ug.group_id = %s
            ORDER BY ug.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (group_id, limit, offset)
        ) or []

        # Convert UUIDs to strings
        for member in members:
            if 'user_id' in member:
                member['user_id'] = str(member['user_id'])

        return {
            'members': members,
            'total': total
        }

    @classmethod
    def get_user_groups(cls, user_id: str) -> List[Dict]:
        """
        Get all groups a user belongs to

        Args:
            user_id: User ID

        Returns:
            List of group dictionaries

        Example:
            >>> groups = GroupRepository.get_user_groups('user-uuid')
            >>> print([g['name'] for g in groups])
        """
        return fetch_all(
            """
            SELECT
                g.group_id,
                g.organisation_id,
                g.name,
                g.slug,
                g.description,
                g.group_type,
                g.is_system_group,
                g.parent_group_id,
                ug.created_at as joined_at
            FROM core.users_groups ug
            JOIN core.groups g ON ug.group_id = g.group_id
            WHERE ug.user_id = %s
            ORDER BY g.name ASC
            """,
            (user_id,)
        ) or []

    # =====================================================
    # Group Hierarchy Operations
    # =====================================================

    @classmethod
    def get_child_groups(cls, parent_group_id: str) -> List[Dict]:
        """
        Get all child groups (one level down)

        Args:
            parent_group_id: Parent group ID

        Returns:
            List of child group dictionaries

        Example:
            >>> children = GroupRepository.get_child_groups('department-uuid')
        """
        return fetch_all(
            """
            SELECT
                group_id,
                organisation_id,
                name,
                slug,
                description,
                group_type,
                is_system_group,
                parent_group_id,
                created_at,
                updated_at
            FROM core.groups
            WHERE parent_group_id = %s AND deleted_at IS NULL
            ORDER BY name ASC
            """,
            (parent_group_id,)
        ) or []

    @classmethod
    def get_parent_group(cls, group_id: str) -> Optional[Dict]:
        """
        Get parent group

        Args:
            group_id: Group ID

        Returns:
            Parent group dictionary or None

        Example:
            >>> parent = GroupRepository.get_parent_group('class-uuid')
        """
        group = cls.find_by_id(group_id)
        if not group or not group.get('parent_group_id'):
            return None

        return cls.find_by_id(group['parent_group_id'])

    @classmethod
    def get_group_path(cls, group_id: str) -> List[Dict]:
        """
        Get full hierarchy path from root to group

        Args:
            group_id: Group ID

        Returns:
            List of groups from root to target (ordered top-down)

        Example:
            >>> path = GroupRepository.get_group_path('class-uuid')
            >>> print([g['name'] for g in path])  # ['Department', 'Team', 'Class']
        """
        path = []
        current_id = group_id

        while current_id:
            group = cls.find_by_id(current_id)
            if not group:
                break

            path.insert(0, group)
            current_id = group.get('parent_group_id')

        return path

    # =====================================================
    # Query & Analytics
    # =====================================================

    @classmethod
    def count(
        cls,
        organisation_id: Optional[str] = None,
        group_type: Optional[str] = None,
        include_deleted: bool = False
    ) -> int:
        """
        Count groups with optional filters

        Args:
            organisation_id: Filter by organisation
            group_type: Filter by group type
            include_deleted: Include soft-deleted groups

        Returns:
            Group count

        Example:
            >>> total = GroupRepository.count(organisation_id='org-uuid')
        """
        where_conditions = []
        params = []

        if organisation_id is not None:
            where_conditions.append("organisation_id = %s")
            params.append(organisation_id)

        if group_type:
            where_conditions.append("group_type = %s")
            params.append(group_type)

        if not include_deleted:
            where_conditions.append("deleted_at IS NULL")

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        result = fetch_one(
            f"SELECT COUNT(*) as count FROM core.groups WHERE {where_clause}",
            tuple(params)
        )

        return result['count'] if result else 0

    @classmethod
    def exists(cls, group_id: str) -> bool:
        """
        Check if group exists

        Args:
            group_id: Group ID

        Returns:
            True if group exists and not deleted

        Example:
            >>> if GroupRepository.exists('group-uuid'):
            ...     print("Group found")
        """
        result = fetch_one(
            "SELECT 1 FROM core.groups WHERE group_id = %s AND deleted_at IS NULL LIMIT 1",
            (group_id,)
        )

        return result is not None

    @classmethod
    def get_statistics(cls, organisation_id: Optional[str] = None) -> Dict:
        """
        Get group statistics

        Args:
            organisation_id: Filter by organisation (None for all)

        Returns:
            Dict with group statistics

        Example:
            >>> stats = GroupRepository.get_statistics('org-uuid')
            >>> print(f"Total groups: {stats['total_groups']}")
        """
        where_clause = (
            "WHERE organisation_id = %s AND deleted_at IS NULL"
            if organisation_id
            else "WHERE deleted_at IS NULL"
        )
        params = (organisation_id,) if organisation_id else ()

        # Total groups
        total_result = fetch_one(
            f"SELECT COUNT(*) as count FROM core.groups {where_clause}",
            params
        )
        total_groups = total_result['count'] if total_result else 0

        # Groups by type
        type_results = fetch_all(
            f"""
            SELECT group_type, COUNT(*) as count
            FROM core.groups {where_clause}
            GROUP BY group_type
            ORDER BY count DESC
            """,
            params
        ) or []

        # Average members per group
        avg_result = fetch_one(
            f"""
            SELECT AVG(member_count) as avg_members
            FROM (
                SELECT COUNT(user_id) as member_count
                FROM core.users_groups ug
                JOIN core.groups g ON ug.group_id = g.group_id
                {where_clause}
                GROUP BY ug.group_id
            ) stats
            """,
            params
        )

        return {
            'total_groups': total_groups,
            'by_type': {t['group_type']: t['count'] for t in type_results},
            'avg_members_per_group': float(avg_result['avg_members']) if avg_result and avg_result['avg_members'] else 0
        }
