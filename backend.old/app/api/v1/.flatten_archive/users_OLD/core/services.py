"""
LernsystemX Users Domain - Domain Services

Domain-Driven Design (DDD) Domain Services for User domain.
Services encapsulate domain logic that doesn't naturally fit into entities or value objects.

Per DDD: Domain Services are stateless operations on domain objects.

ISO 27001:2013 A.9 - Access control domain logic
"""

from typing import Dict, Any, Optional, Set
from .value_objects import UserRole, AccountStatus, PermissionScope, UserType


class UserService:
    """
    Domain service for user-related business logic.

    Stateless operations that coordinate between aggregates or
    implement domain rules that span multiple objects.
    """

    @staticmethod
    def can_assign_role(current_role: UserRole | str, target_role: UserRole | str) -> bool:
        """
        Check if current user role can assign target role.

        Business Rule: Users can only assign roles below their hierarchy level.

        Args:
            current_role: Role of user attempting assignment
            target_role: Role to be assigned

        Returns:
            True if assignment is allowed
        """
        current = UserRole(current_role) if isinstance(current_role, str) else current_role
        target = UserRole(target_role) if isinstance(target_role, str) else target_role

        return current.can_manage_role(target)

    @staticmethod
    def can_manage_user(
        current_user: Dict[str, Any],
        target_user: Dict[str, Any]
    ) -> bool:
        """
        Check if current user can manage target user.

        Business Rules:
        - Admins can manage users with lower hierarchy
        - Org admins can manage users in same org with lower hierarchy
        - Users cannot manage themselves for critical operations

        Args:
            current_user: Current user dict
            target_user: Target user dict

        Returns:
            True if management is allowed
        """
        current_role = UserRole(current_user['role'])
        target_role = UserRole(target_user['role'])

        # Superadmins can manage anyone
        if current_role == UserRole.SUPERADMIN:
            return True

        # Admins can manage non-admins
        if current_role == UserRole.ADMIN:
            return target_role not in [UserRole.ADMIN, UserRole.SUPERADMIN]

        # Org admins can manage users in their org with lower hierarchy
        if current_role in [UserRole.SCHOOL_ADMIN, UserRole.COMPANY_ADMIN]:
            same_org = (
                current_user.get('organization_id') ==
                target_user.get('organization_id')
            )
            return same_org and current_role.can_manage_role(target_role)

        return False

    @staticmethod
    def has_permission(
        user: Dict[str, Any],
        permission: str,
        resource_owner_id: Optional[str] = None,
        resource_org_id: Optional[int] = None
    ) -> bool:
        """
        Check if user has permission to access resource.

        Args:
            user: User dict
            permission: Permission string (e.g., 'user.read')
            resource_owner_id: Optional owner of resource
            resource_org_id: Optional organisation of resource

        Returns:
            True if permission is granted
        """
        role = UserRole(user['role'])
        scope = PermissionScope.for_role(role, user.get('organization_id') is not None)

        # Superadmins and admins have all permissions
        if scope == PermissionScope.ALL:
            return True

        # Organisation scope
        if scope == PermissionScope.ORGANISATION:
            if resource_org_id:
                return user.get('organization_id') == resource_org_id
            # If no org specified, assume allowed
            return True

        # Own scope
        if scope == PermissionScope.OWN:
            if resource_owner_id:
                return user['user_id'] == resource_owner_id
            # If no owner specified, assume allowed (public resource)
            return True

        return False

    @staticmethod
    def get_accessible_roles(role: UserRole | str) -> Set[UserRole]:
        """
        Get roles that can be assigned by the given role.

        Args:
            role: Current user role

        Returns:
            Set of assignable roles
        """
        return UserRole.get_accessible_roles(role)

    @staticmethod
    def get_user_type(user: Dict[str, Any]) -> UserType:
        """
        Determine user type from user data.

        Args:
            user: User dict

        Returns:
            UserType enum
        """
        role = UserRole(user['role'])
        has_org = user.get('organization_id') is not None
        return UserType.from_role(role, has_org)

    @staticmethod
    def is_account_usable(user: Dict[str, Any]) -> bool:
        """
        Check if account can be used (not banned, suspended, etc.).

        Args:
            user: User dict

        Returns:
            True if account is usable
        """
        if not user.get('is_active', False):
            return False

        status = AccountStatus(user.get('status', AccountStatus.INACTIVE.value))
        return status.is_usable

    @staticmethod
    def can_access_organisation(
        user: Dict[str, Any],
        org_id: int
    ) -> bool:
        """
        Check if user can access organisation data.

        Business Rules:
        - Superadmins and admins can access all organisations
        - Org admins can access their own organisation
        - Members can access their own organisation

        Args:
            user: User dict
            org_id: Organisation ID

        Returns:
            True if access is allowed
        """
        role = UserRole(user['role'])

        # System admins can access all
        if role in [UserRole.SUPERADMIN, UserRole.ADMIN]:
            return True

        # Check membership
        return user.get('organization_id') == org_id

    @staticmethod
    def validate_role_change(
        current_role: UserRole | str,
        new_role: UserRole | str,
        performed_by_role: UserRole | str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if role change is allowed.

        Args:
            current_role: User's current role
            new_role: Desired new role
            performed_by_role: Role of user performing change

        Returns:
            Tuple of (is_valid, error_message)
        """
        current = UserRole(current_role) if isinstance(current_role, str) else current_role
        new = UserRole(new_role) if isinstance(new_role, str) else new_role
        performer = UserRole(performed_by_role) if isinstance(performed_by_role, str) else performed_by_role

        # Cannot downgrade superadmin
        if current == UserRole.SUPERADMIN:
            return False, "Cannot change superadmin role"

        # Performer must be able to manage both current and new role
        if not (performer.can_manage_role(current) and performer.can_manage_role(new)):
            return False, "Insufficient permissions for role change"

        return True, None


__all__ = ['UserService']
