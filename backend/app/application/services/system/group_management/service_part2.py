"""
Group Management Service - Membership & Organization Init (Part 2)

Handles:
- Membership management (add/remove users, batch operations)
- B2B SaaS organization setup (owner group creation, permission assignment)

PHASE B: Service layer for group-based authorization system.
"""

from typing import Optional, Dict, List
import logging

from app.infrastructure.persistence.repositories.group import (
    GroupRepository,
    GroupManagementRepository
)
from app.infrastructure.persistence.database.connection import execute_query, fetch_one

logger = logging.getLogger(__name__)


class MembershipAndOrgMixin:
    """
    Mixin for membership management and organization initialization.

    Provides:
    - add_user_to_group, remove_user_from_group, batch_add_users
    - create_owner_group_for_organization, _assign_owner_permissions

    Used by GroupManagementService via mixin inheritance.
    """

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
    # Organization Initialization (B2B SaaS Setup)
    # =====================================================

    @classmethod
    def create_owner_group_for_organization(
        cls,
        organisation_id: str,
        owner_user_id: str,
        created_by: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create an "Owner" group for a new organisation and assign owner.

        This is called during account creation for B2B customers.
        Creates organisation-specific owner group and adds the account creator to it.

        Args:
            organisation_id: Organization ID (B2B customer)
            owner_user_id: User ID of the organisation owner
            created_by: Admin user ID performing the operation (optional)

        Returns:
            Created group dict or None on failure

        Raises:
            ValueError: If organisation not found or owner user not found

        Example:
            >>> group = GroupManagementService.create_owner_group_for_organization(
            ...     organisation_id='org-uuid',
            ...     owner_user_id='user-uuid',
            ...     created_by='admin-uuid'
            ... )
        """
        try:
            # Verify organisation exists
            org_check = fetch_one(
                "SELECT id FROM organisations.organisations WHERE organisation_id = %s",
                (organisation_id,)
            )
            if not org_check:
                raise ValueError(f"Organization {organisation_id} not found")

            # Verify owner user exists
            user_check = fetch_one(
                "SELECT id FROM core.users WHERE id = %s",
                (owner_user_id,)
            )
            if not user_check:
                raise ValueError(f"User {owner_user_id} not found")

            # Create organisation-specific owner group
            owner_group = cls.create_group(
                name=f"Owner",
                slug=f"{organisation_id}-owner",
                organisation_id=organisation_id,
                group_type="org_admin",
                description=f"Owner group for organisation {organisation_id}",
                created_by=created_by
            )

            if not owner_group:
                logger.error(f"Failed to create owner group for organisation {organisation_id}")
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
                f"Created owner group for organisation {organisation_id}, "
                f"assigned user {owner_user_id}"
            )

            if created_by:
                execute_query(
                    """
                    INSERT INTO core.audit_logs (user_id, action, description, metadata)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (created_by, 'org.owner_group_created',
                     f"Created owner group for organisation {organisation_id}",
                     f'{{"group_id": "{owner_group["id"]}", "organisation_id": "{organisation_id}"}}')
                )

            return owner_group

        except Exception as e:
            logger.error(f"Error creating owner group for organisation {organisation_id}: {str(e)}")
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
