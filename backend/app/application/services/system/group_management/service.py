"""
Group Management Service - Business Logic for RBAC 3.0 Groups

Implements group management operations with:
- Validation and business rule enforcement
- Permission checking
- Audit logging
- Error handling

PHASE B: Service layer for group-based authorization system.
"""

from typing import Optional, Dict, List
from datetime import datetime
import logging
import re

from app.infrastructure.persistence.repositories.group import (
    GroupRepository,
    GroupManagementRepository
)
from app.infrastructure.persistence.database.connection import execute_query, fetch_one

logger = logging.getLogger(__name__)


class GroupManagementService:
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
    # Membership Management
    # =====================================================

    @classmethod
    def add_user_to_group(
        cls,
        group_id: str,
        user_id: str,
        added_by: Optional[str] = None
    ) -> bool:
        """
        Add user to group

        Args:
            group_id: Group ID
            user_id: User ID to add
            added_by: Admin user ID performing operation

        Returns:
            True if user added

        Raises:
            ValueError: If group or user not found

        Example:
            >>> GroupManagementService.add_user_to_group(
            ...     'group-uuid',
            ...     'user-uuid',
            ...     'admin-uuid'
            ... )
        """
        # Verify group exists
        if not GroupRepository.exists(group_id):
            raise ValueError(f"Group {group_id} not found")

        # Verify user exists
        user = fetch_one("SELECT user_id FROM core.users WHERE user_id = %s", (user_id,))
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Add user
        result = GroupRepository.add_user(group_id, user_id)

        if result and added_by:
            execute_query(
                """
                INSERT INTO core.audit_logs (user_id, action, description, metadata)
                VALUES (%s, %s, %s, %s)
                """,
                (added_by, 'admin.groups.user_added', f"Added user to group",
                 f'{{"group_id": "{group_id}", "user_id": "{user_id}"}}')
            )

        return result

    @classmethod
    def remove_user_from_group(
        cls,
        group_id: str,
        user_id: str,
        removed_by: Optional[str] = None
    ) -> bool:
        """
        Remove user from group

        Args:
            group_id: Group ID
            user_id: User ID to remove
            removed_by: Admin user ID performing operation

        Returns:
            True if user removed

        Example:
            >>> GroupManagementService.remove_user_from_group(
            ...     'group-uuid',
            ...     'user-uuid',
            ...     'admin-uuid'
            ... )
        """
        result = GroupRepository.remove_user(group_id, user_id)

        if result and removed_by:
            execute_query(
                """
                INSERT INTO core.audit_logs (user_id, action, description, metadata)
                VALUES (%s, %s, %s, %s)
                """,
                (removed_by, 'admin.groups.user_removed', f"Removed user from group",
                 f'{{"group_id": "{group_id}", "user_id": "{user_id}"}}')
            )

        return result

    @classmethod
    def batch_add_users(
        cls,
        group_id: str,
        user_ids: List[str],
        added_by: Optional[str] = None
    ) -> Dict:
        """
        Add multiple users to group

        Args:
            group_id: Group ID
            user_ids: List of user IDs
            added_by: Admin user ID

        Returns:
            Operation result dictionary

        Example:
            >>> result = GroupManagementService.batch_add_users(
            ...     'group-uuid',
            ...     ['user-1', 'user-2', 'user-3'],
            ...     'admin-uuid'
            ... )
        """
        if not GroupRepository.exists(group_id):
            raise ValueError(f"Group {group_id} not found")

        result = GroupManagementRepository.add_users_to_group(group_id, user_ids, added_by)

        if result['added'] > 0 and added_by:
            execute_query(
                """
                INSERT INTO core.audit_logs (user_id, action, description, metadata)
                VALUES (%s, %s, %s, %s)
                """,
                (added_by, 'admin.groups.batch_users_added', f"Added {result['added']} users",
                 f'{{"group_id": "{group_id}", "count": {result["added"]}}}')
            )

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

    # =====================================================
    # Organization Initialization (B2B SaaS Setup)
    # =====================================================

    @classmethod
    def create_owner_group_for_organization(
        cls,
        organization_id: str,
        owner_user_id: str,
        created_by: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create an "Owner" group for a new organization and assign owner.

        This is called during account creation for B2B customers.
        Creates organization-specific owner group and adds the account creator to it.

        Args:
            organization_id: Organization ID (B2B customer)
            owner_user_id: User ID of the organization owner
            created_by: Admin user ID performing the operation (optional)

        Returns:
            Created group dict or None on failure

        Raises:
            ValueError: If organization not found or owner user not found

        Example:
            >>> group = GroupManagementService.create_owner_group_for_organization(
            ...     organization_id='org-uuid',
            ...     owner_user_id='user-uuid',
            ...     created_by='admin-uuid'
            ... )
        """
        try:
            # Verify organization exists
            org_check = fetch_one(
                "SELECT id FROM organisations.organisations WHERE organization_id = %s",
                (organization_id,)
            )
            if not org_check:
                raise ValueError(f"Organization {organization_id} not found")

            # Verify owner user exists
            user_check = fetch_one(
                "SELECT id FROM core.users WHERE id = %s",
                (owner_user_id,)
            )
            if not user_check:
                raise ValueError(f"User {owner_user_id} not found")

            # Create organization-specific owner group
            owner_group = cls.create_group(
                name=f"Owner",
                slug=f"{organization_id}-owner",
                organisation_id=organization_id,
                group_type="org_admin",
                description=f"Owner group for organization {organization_id}",
                created_by=created_by
            )

            if not owner_group:
                logger.error(f"Failed to create owner group for organization {organization_id}")
                return None

            # Add owner user to the group
            cls.add_user_to_group(
                group_id=owner_group['id'],
                user_id=owner_user_id,
                added_by=created_by
            )

            # Assign all necessary permissions to owner group
            cls._assign_owner_permissions(owner_group['id'], created_by)

            logger.info(
                f"Created owner group for organization {organization_id}, "
                f"assigned user {owner_user_id}"
            )

            if created_by:
                execute_query(
                    """
                    INSERT INTO core.audit_logs (user_id, action, description, metadata)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (created_by, 'org.owner_group_created',
                     f"Created owner group for organization {organization_id}",
                     f'{{"group_id": "{owner_group["id"]}", "organization_id": "{organization_id}"}}')
                )

            return owner_group

        except Exception as e:
            logger.error(f"Error creating owner group for organization {organization_id}: {str(e)}")
            raise

    @classmethod
    def _assign_owner_permissions(
        cls,
        group_id: str,
        assigned_by: Optional[str] = None
    ) -> bool:
        """
        Assign all necessary permissions to owner group.

        Owner should have all admin-level permissions.

        Args:
            group_id: Group ID to assign permissions to
            assigned_by: Admin user ID performing the assignment

        Returns:
            True if successful
        """
        try:
            # Get all admin-level permissions
            admin_permissions = fetch_one(
                """
                SELECT id FROM core.permissions
                WHERE required_hierarchy_level >= 3
                ORDER BY code
                """
            )

            if not admin_permissions:
                logger.warning(f"No admin permissions found to assign to owner group {group_id}")
                return False

            # Assign each permission
            execute_query(
                """
                INSERT INTO core.group_permissions (group_id, permission_id, granted_by)
                SELECT %s, id, %s FROM core.permissions
                WHERE required_hierarchy_level >= 3
                ON CONFLICT (group_id, permission_id) DO NOTHING
                """,
                (group_id, assigned_by)
            )

            logger.info(f"Assigned admin permissions to owner group {group_id}")
            return True

        except Exception as e:
            logger.error(f"Error assigning owner permissions to group {group_id}: {str(e)}")
            return False
