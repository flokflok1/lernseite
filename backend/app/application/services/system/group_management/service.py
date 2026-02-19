"""
Group Management Service - Business Logic for RBAC 3.0 Groups

Implements group management operations with:
- Validation and business rule enforcement
- Permission checking
- Audit logging
- Error handling

Membership management and organization initialization are in service_part2.py (MembershipAndOrgMixin).

PHASE B: Service layer for group-based authorization system.
"""

from typing import Optional, Dict, List
import logging
import re

from app.infrastructure.persistence.repositories.group import (
    GroupRepository,
    GroupManagementRepository
)
from app.infrastructure.persistence.database.connection import execute_query, fetch_one
from app.application.services.system.group_management.service_part2 import MembershipAndOrgMixin

logger = logging.getLogger(__name__)


class GroupManagementService(MembershipAndOrgMixin):
    """Service for group management operations"""

    # System groups that cannot be deleted
    SYSTEM_GROUPS = {
        'system-admin',
        'system-teacher',
        'system-student',
        'system-moderator',
        'system-support',
        'system-guest'
    }

    @classmethod
    def _validate_slug(cls, slug: str) -> bool:
        """
        Validate group slug format

        Args:
            slug: Slug to validate

        Returns:
            True if valid

        Raises:
            ValueError: If invalid
        """
        pattern = r'^[a-z0-9_-]+$'
        if not re.match(pattern, slug) or len(slug) < 3 or len(slug) > 50:
            raise ValueError(
                "Slug must be 3-50 chars, lowercase, alphanumeric, underscore, hyphen only"
            )
        return True

    @classmethod
    def _validate_group_name(cls, name: str) -> bool:
        """
        Validate group name

        Args:
            name: Name to validate

        Returns:
            True if valid

        Raises:
            ValueError: If invalid
        """
        if not name or len(name) < 2 or len(name) > 100:
            raise ValueError("Group name must be 2-100 characters")
        return True

    # =====================================================
    # Group CRUD Operations
    # =====================================================

    @classmethod
    def create_group(
        cls,
        name: str,
        slug: str,
        organisation_id: Optional[str],
        group_type: str = 'custom',
        description: Optional[str] = None,
        parent_group_id: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Dict:
        """
        Create new group with validation

        Args:
            name: Group name
            slug: URL-safe identifier
            organisation_id: Organisation ID (None for system groups)
            group_type: Group type (department, class, team, custom, etc.)
            description: Optional description
            parent_group_id: Optional parent group for hierarchy
            created_by: Admin user ID creating the group

        Returns:
            Created group dictionary

        Raises:
            ValueError: If validation fails
            Exception: If database error occurs

        Example:
            >>> group = GroupManagementService.create_group(
            ...     name='Premium Members',
            ...     slug='premium-members',
            ...     organisation_id='org-uuid',
            ...     group_type='custom',
            ...     description='Premium tier members',
            ...     created_by='admin-uuid'
            ... )
        """
        # Validate inputs
        cls._validate_group_name(name)
        cls._validate_slug(slug)

        # Check slug uniqueness
        existing = GroupRepository.find_by_slug(slug, organisation_id)
        if existing:
            raise ValueError(f"Slug '{slug}' already exists in this organisation")

        # Check parent group exists if specified
        if parent_group_id:
            parent = GroupRepository.find_by_id(parent_group_id)
            if not parent:
                raise ValueError(f"Parent group {parent_group_id} not found")

        # Create group
        group = GroupRepository.create(
            name=name,
            slug=slug,
            organisation_id=organisation_id,
            group_type=group_type,
            description=description,
            parent_group_id=parent_group_id
        )

        if not group:
            raise Exception("Failed to create group")

        # Log creation
        if created_by:
            execute_query(
                """
                INSERT INTO core.audit_logs (user_id, action, description, metadata)
                VALUES (%s, %s, %s, %s)
                """,
                (created_by, 'admin.groups.created', f"Created group: {name}", f'{{"group_id": "{group["group_id"]}"}}')
            )

        logger.info(f"Group created: {slug} (ID: {group['group_id']})")
        return group

    @classmethod
    def update_group(
        cls,
        group_id: str,
        updates: Dict,
        updated_by: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update group with validation

        Args:
            group_id: Group ID to update
            updates: Dictionary of updates (name, description, metadata)
            updated_by: Admin user ID performing update

        Returns:
            Updated group or None if not found

        Raises:
            ValueError: If validation fails or update is forbidden
            Exception: If database error occurs

        Example:
            >>> updated = GroupManagementService.update_group(
            ...     'group-uuid',
            ...     {'name': 'New Name', 'description': 'New desc'},
            ...     'admin-uuid'
            ... )
        """
        group = GroupRepository.find_by_id(group_id)
        if not group:
            raise ValueError(f"Group {group_id} not found")

        # Check if system group
        if group.get('is_system_group'):
            raise ValueError("Cannot modify system groups")

        # Validate updates
        if 'name' in updates:
            cls._validate_group_name(updates['name'])

        # Update group
        updated = GroupRepository.update(group_id, updates)

        if updated and updated_by:
            execute_query(
                """
                INSERT INTO core.audit_logs (user_id, action, description, metadata)
                VALUES (%s, %s, %s, %s)
                """,
                (updated_by, 'admin.groups.updated', f"Updated group: {group['name']}", f'{{"group_id": "{group_id}"}}')
            )

        logger.info(f"Group updated: {group['slug']} (ID: {group_id})")
        return updated

    @classmethod
    def delete_group(
        cls,
        group_id: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Delete group with protection checks

        Args:
            group_id: Group ID to delete
            deleted_by: Admin user ID performing deletion

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If deletion is forbidden
            Exception: If database error occurs

        Example:
            >>> deleted = GroupManagementService.delete_group('group-uuid', 'admin-uuid')
        """
        group = GroupRepository.find_by_id(group_id)
        if not group:
            raise ValueError(f"Group {group_id} not found")

        # Check if system group or protected
        if group.get('is_system_group') or group.get('is_protected'):
            raise ValueError("Cannot delete system or protected groups")

        # Check if group has members
        members = fetch_one(
            "SELECT COUNT(*) as count FROM core.users_groups WHERE group_id = %s",
            (group_id,)
        )

        if members and members['count'] > 0:
            raise ValueError(
                f"Cannot delete group with {members['count']} members. Remove all members first."
            )

        # Check if group has child groups
        children = GroupRepository.get_child_groups(group_id)
        if children:
            raise ValueError(
                f"Cannot delete group with {len(children)} child groups. Delete children first."
            )

        # Delete group
        result = GroupRepository.delete(group_id)

        if result and deleted_by:
            execute_query(
                """
                INSERT INTO core.audit_logs (user_id, action, description, metadata)
                VALUES (%s, %s, %s, %s)
                """,
                (deleted_by, 'admin.groups.deleted', f"Deleted group: {group['name']}", f'{{"group_id": "{group_id}"}}')
            )

        logger.info(f"Group deleted: {group['slug']} (ID: {group_id})")
        return result

    # =====================================================
    # Permission Management
    # =====================================================

    @classmethod
    def assign_permission(
        cls,
        group_id: str,
        permission_key: str,
        assigned_by: Optional[str] = None
    ) -> bool:
        """
        Assign permission to group

        Args:
            group_id: Group ID
            permission_key: Permission key
            assigned_by: Admin user ID

        Returns:
            True if assigned

        Raises:
            ValueError: If group not found

        Example:
            >>> GroupManagementService.assign_permission(
            ...     'group-uuid',
            ...     'admin:users',
            ...     'admin-uuid'
            ... )
        """
        if not GroupRepository.exists(group_id):
            raise ValueError(f"Group {group_id} not found")

        result = GroupManagementRepository.assign_permission_to_group(
            group_id, permission_key, assigned_by
        )

        if result and assigned_by:
            execute_query(
                """
                INSERT INTO core.audit_logs (user_id, action, description, metadata)
                VALUES (%s, %s, %s, %s)
                """,
                (assigned_by, 'admin.groups.permission_assigned', f"Permission assigned",
                 f'{{"group_id": "{group_id}", "permission": "{permission_key}"}}')
            )

        return result

    @classmethod
    def revoke_permission(
        cls,
        group_id: str,
        permission_key: str,
        revoked_by: Optional[str] = None
    ) -> bool:
        """
        Revoke permission from group

        Args:
            group_id: Group ID
            permission_key: Permission key
            revoked_by: Admin user ID

        Returns:
            True if revoked

        Example:
            >>> GroupManagementService.revoke_permission(
            ...     'group-uuid',
            ...     'admin:users',
            ...     'admin-uuid'
            ... )
        """
        result = GroupManagementRepository.revoke_permission_from_group(
            group_id, permission_key, revoked_by
        )

        if result and revoked_by:
            execute_query(
                """
                INSERT INTO core.audit_logs (user_id, action, description, metadata)
                VALUES (%s, %s, %s, %s)
                """,
                (revoked_by, 'admin.groups.permission_revoked', f"Permission revoked",
                 f'{{"group_id": "{group_id}", "permission": "{permission_key}"}}')
            )

        return result

    # =====================================================
    # Query Methods (delegation to repositories)
    # =====================================================

    @classmethod
    def get_group(cls, group_id: str) -> Optional[Dict]:
        """Get group by ID"""
        return GroupRepository.find_by_id(group_id)

    @classmethod
    def get_group_members(
        cls,
        group_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get group members with pagination"""
        return GroupRepository.get_members(group_id, limit, offset)

    @classmethod
    def get_user_groups(cls, user_id: str) -> List[Dict]:
        """Get all groups for user"""
        return GroupRepository.get_user_groups(user_id)

    @classmethod
    def get_group_permissions(cls, group_id: str) -> List[str]:
        """Get all permissions for group"""
        return GroupManagementRepository.get_group_permissions(group_id)

    @classmethod
    def search_groups(
        cls,
        query: str,
        organisation_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Search groups"""
        return GroupManagementRepository.search_groups(query, organisation_id, limit)

    @classmethod
    def get_statistics(cls, organisation_id: Optional[str] = None) -> Dict:
        """Get group statistics"""
        return GroupRepository.get_statistics(organisation_id)

