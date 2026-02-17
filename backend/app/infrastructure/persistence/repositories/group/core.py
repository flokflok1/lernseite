"""
Group Repository - Database Access for Group Management

Implements RBAC 3.0 group-based authorization.
Handles group CRUD operations.

PHASE B: Complete group-based system replaces RBAC 2.0 role-based system.

Membership, hierarchy, and analytics operations are in core_part2.py
(split to comply with Quality Gate G01 - max 500 lines per file).
"""

from typing import Optional, Dict, List
from datetime import datetime
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.repositories.group.core_part2 import GroupMembershipMixin
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query

logger = logging.getLogger(__name__)


class GroupRepository(GroupMembershipMixin, BaseRepository):
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
