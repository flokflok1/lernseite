"""
Role Studio Service

Provides business logic for managing role-studio-mode configurations.
Handles role management, permission assignment, and studio mode determination.

ISO 9001:2015 compliant - Standardized business operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging

from app.repositories.role_studio_mode import RoleStudioModeRepository

logger = logging.getLogger(__name__)


class RoleStudioService:
    """
    Service for role studio mode management

    Provides business logic for:
    - Retrieving role-to-studio-mode mappings
    - Managing role permissions
    - Determining user's studio mode based on role
    - Auditing role changes
    """

    # ==================== ROLE RETRIEVAL ====================

    @staticmethod
    def get_role_studio_mode(role_code: str) -> Optional[Dict]:
        """
        Get the studio mode configuration for a given role

        Args:
            role_code: The role code (e.g., 'admin', 'teacher', 'user')

        Returns:
            Role studio mode configuration or None if not found

        Example:
            >>> config = RoleStudioService.get_role_studio_mode('admin')
            >>> if config:
            ...     print(f"Studio mode: {config['studio_mode']}")
        """
        try:
            config = RoleStudioModeRepository.find_by_code(role_code)

            if not config:
                logger.warning(f"Role studio mode not found: {role_code}")
                return None

            # Parse permissions if stored as JSON string
            if isinstance(config.get('permissions'), str):
                try:
                    config['permissions'] = json.loads(config['permissions'])
                except (json.JSONDecodeError, TypeError):
                    config['permissions'] = {}

            return config

        except Exception as e:
            logger.error(f"Error retrieving role studio mode {role_code}: {str(e)}")
            raise

    @staticmethod
    def get_all_active_roles() -> List[Dict]:
        """
        Get all active role studio modes

        Returns:
            List of active role configurations

        Example:
            >>> active_roles = RoleStudioService.get_all_active_roles()
            >>> for role in active_roles:
            ...     print(f"{role['role_code']}: {role['studio_mode']}")
        """
        try:
            roles = RoleStudioModeRepository.find_all_active()

            # Parse permissions for all roles
            for role in roles:
                if isinstance(role.get('permissions'), str):
                    try:
                        role['permissions'] = json.loads(role['permissions'])
                    except (json.JSONDecodeError, TypeError):
                        role['permissions'] = {}

            return roles

        except Exception as e:
            logger.error(f"Error retrieving active roles: {str(e)}")
            raise

    @staticmethod
    def get_roles_by_studio_mode(studio_mode: str) -> List[Dict]:
        """
        Get all roles assigned to a specific studio mode

        Args:
            studio_mode: The studio mode (e.g., 'admin', 'moderator', 'user')

        Returns:
            List of roles assigned to that studio mode

        Example:
            >>> admin_roles = RoleStudioService.get_roles_by_studio_mode('admin')
        """
        try:
            roles = RoleStudioModeRepository.find_by_studio_mode(studio_mode)

            # Parse permissions
            for role in roles:
                if isinstance(role.get('permissions'), str):
                    try:
                        role['permissions'] = json.loads(role['permissions'])
                    except (json.JSONDecodeError, TypeError):
                        role['permissions'] = {}

            return roles

        except Exception as e:
            logger.error(f"Error retrieving roles for studio mode {studio_mode}: {str(e)}")
            raise

    # ==================== ROLE MANAGEMENT ====================

    @staticmethod
    def create_role(
        role_code: str,
        display_name: str,
        studio_mode: str,
        permissions: Dict[str, bool],
        requires_organization: bool = False,
        description: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create a new role studio mode configuration

        Args:
            role_code: Unique role identifier
            display_name: Human-readable role name
            studio_mode: The studio mode this role should access
            permissions: Dictionary of permission flags
            requires_organization: Whether this role requires organization membership
            description: Optional description of the role

        Returns:
            Created role configuration or None if failed

        Example:
            >>> role = RoleStudioService.create_role(
            ...     role_code='content_reviewer',
            ...     display_name='Content Reviewer',
            ...     studio_mode='moderator',
            ...     permissions={'can_moderate': True, 'can_view_analytics': True}
            ... )
        """
        try:
            # Validate studio mode
            valid_modes = ['admin', 'moderator', 'org_admin', 'org_member', 'teacher', 'user', 'guest']
            if studio_mode not in valid_modes:
                raise ValueError(f"Invalid studio mode: {studio_mode}. Must be one of: {valid_modes}")

            # Check if role already exists
            existing = RoleStudioModeRepository.find_by_code(role_code)
            if existing:
                raise ValueError(f"Role {role_code} already exists")

            # Prepare data
            data = {
                'role_code': role_code,
                'display_name': display_name,
                'studio_mode': studio_mode,
                'permissions': json.dumps(permissions) if isinstance(permissions, dict) else permissions,
                'requires_organization': requires_organization,
                'is_active': True,
                'description': description
            }

            created = RoleStudioModeRepository.create(data)

            logger.info(f"Role created: {role_code} -> {studio_mode}")
            return created

        except Exception as e:
            logger.error(f"Error creating role {role_code}: {str(e)}")
            raise

    @staticmethod
    def update_role(
        role_code: str,
        updates: Dict[str, Any],
        changed_by: str,
        change_reason: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update a role studio mode configuration

        Args:
            role_code: The role to update
            updates: Dictionary of fields to update
            changed_by: User ID making the change
            change_reason: Reason for the change (for audit trail)

        Returns:
            Updated role configuration or None if not found

        Example:
            >>> role = RoleStudioService.update_role(
            ...     role_code='teacher',
            ...     updates={'display_name': 'Instructor'},
            ...     changed_by='admin_user_id',
            ...     change_reason='Updated terminology'
            ... )
        """
        try:
            # Get current role for audit trail
            current = RoleStudioModeRepository.find_by_code(role_code)
            if not current:
                raise ValueError(f"Role {role_code} not found")

            # Prepare audit data
            audit_changes = {
                'previous_display_name': current.get('display_name'),
                'previous_studio_mode': current.get('studio_mode'),
                'previous_permissions': current.get('permissions')
            }

            # Prepare update data
            if 'permissions' in updates and isinstance(updates['permissions'], dict):
                updates['permissions'] = json.dumps(updates['permissions'])

            # Update the role
            updated = RoleStudioModeRepository.update(role_code, updates)

            if updated:
                # Log the change to audit trail
                audit_changes['new_display_name'] = updated.get('display_name')
                audit_changes['new_studio_mode'] = updated.get('studio_mode')
                audit_changes['new_permissions'] = updated.get('permissions')

                RoleStudioModeRepository.audit_log(
                    role_code=role_code,
                    changes=audit_changes,
                    changed_by=changed_by,
                    change_reason=change_reason
                )

                logger.info(f"Role updated: {role_code} by {changed_by}")

            return updated

        except Exception as e:
            logger.error(f"Error updating role {role_code}: {str(e)}")
            raise

    @staticmethod
    def deactivate_role(
        role_code: str,
        changed_by: str,
        change_reason: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Deactivate a role (soft delete)

        Args:
            role_code: The role to deactivate
            changed_by: User ID making the change
            change_reason: Reason for deactivation

        Returns:
            Updated role configuration or None if not found
        """
        try:
            # Get current role
            current = RoleStudioModeRepository.find_by_code(role_code)
            if not current:
                raise ValueError(f"Role {role_code} not found")

            # Deactivate
            updated = RoleStudioModeRepository.update(
                role_code,
                {'is_active': False}
            )

            if updated:
                # Log to audit trail
                RoleStudioModeRepository.audit_log(
                    role_code=role_code,
                    changes={
                        'previous_display_name': current.get('display_name'),
                        'new_display_name': current.get('display_name'),
                        'previous_studio_mode': current.get('studio_mode'),
                        'new_studio_mode': current.get('studio_mode')
                    },
                    changed_by=changed_by,
                    change_reason=change_reason or 'Role deactivated'
                )

                logger.info(f"Role deactivated: {role_code} by {changed_by}")

            return updated

        except Exception as e:
            logger.error(f"Error deactivating role {role_code}: {str(e)}")
            raise

    # ==================== PERMISSION MANAGEMENT ====================

    @staticmethod
    def get_role_permissions(role_code: str) -> Dict[str, bool]:
        """
        Get all permissions for a role

        Args:
            role_code: The role code

        Returns:
            Dictionary of permissions and their boolean values

        Example:
            >>> perms = RoleStudioService.get_role_permissions('admin')
            >>> if perms.get('can_manage_users'):
            ...     print("Can manage users!")
        """
        try:
            config = RoleStudioService.get_role_studio_mode(role_code)
            if not config:
                return {}

            permissions = config.get('permissions', {})
            if isinstance(permissions, str):
                try:
                    permissions = json.loads(permissions)
                except (json.JSONDecodeError, TypeError):
                    permissions = {}

            return permissions

        except Exception as e:
            logger.error(f"Error retrieving permissions for role {role_code}: {str(e)}")
            raise

    @staticmethod
    def has_permission(role_code: str, permission: str) -> bool:
        """
        Check if a role has a specific permission

        Args:
            role_code: The role code
            permission: The permission to check

        Returns:
            True if the role has the permission, False otherwise

        Example:
            >>> if RoleStudioService.has_permission('teacher', 'can_create_course'):
            ...     print("Teacher can create courses")
        """
        try:
            permissions = RoleStudioService.get_role_permissions(role_code)
            return permissions.get(permission, False)

        except Exception as e:
            logger.error(f"Error checking permission {permission} for role {role_code}: {str(e)}")
            return False

    @staticmethod
    def update_permissions(
        role_code: str,
        permissions: Dict[str, bool],
        changed_by: str,
        change_reason: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update permissions for a role

        Args:
            role_code: The role to update
            permissions: New permissions dictionary
            changed_by: User ID making the change
            change_reason: Reason for the change

        Returns:
            Updated role configuration or None if not found
        """
        try:
            return RoleStudioService.update_role(
                role_code=role_code,
                updates={'permissions': permissions},
                changed_by=changed_by,
                change_reason=change_reason or 'Permissions updated'
            )

        except Exception as e:
            logger.error(f"Error updating permissions for role {role_code}: {str(e)}")
            raise

    # ==================== AUDIT TRAIL ====================

    @staticmethod
    def get_role_change_history(role_code: str, limit: int = 50) -> List[Dict]:
        """
        Get change history for a role

        Args:
            role_code: The role to get history for
            limit: Maximum number of history records

        Returns:
            List of change history records

        Example:
            >>> history = RoleStudioService.get_role_change_history('admin')
            >>> for change in history:
            ...     print(f"Changed at {change['changed_at']} by {change['changed_by']}")
        """
        try:
            return RoleStudioModeRepository.get_history(role_code, limit=limit)

        except Exception as e:
            logger.error(f"Error retrieving change history for role {role_code}: {str(e)}")
            raise

    # ==================== ORGANIZATION ROLES ====================

    @staticmethod
    def get_organization_required_roles() -> List[Dict]:
        """
        Get all roles that require organization membership

        Returns:
            List of roles that require organization membership

        Example:
            >>> org_roles = RoleStudioService.get_organization_required_roles()
        """
        try:
            return RoleStudioModeRepository.find_by_filters(
                {'requires_organization': True, 'is_active': True}
            )

        except Exception as e:
            logger.error(f"Error retrieving organization-required roles: {str(e)}")
            raise

    @staticmethod
    def get_global_roles() -> List[Dict]:
        """
        Get all roles that do NOT require organization membership

        Returns:
            List of global (non-organization) roles

        Example:
            >>> global_roles = RoleStudioService.get_global_roles()
        """
        try:
            return RoleStudioModeRepository.find_by_filters(
                {'requires_organization': False, 'is_active': True}
            )

        except Exception as e:
            logger.error(f"Error retrieving global roles: {str(e)}")
            raise
