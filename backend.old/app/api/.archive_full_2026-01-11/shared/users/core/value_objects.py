"""
LernsystemX Users Domain - Value Objects

Domain-Driven Design (DDD) Value Objects for User domain.
Immutable value types representing user domain concepts.

Per DDD: Value Objects are immutable objects defined by their attributes.
They have no identity and are compared by value, not identity.

ISO 27001:2013 A.9 - Access control value definitions
"""

from enum import Enum
from typing import List, Set


class UserRole(str, Enum):
    """
    User role enumeration with hierarchy.

    Hierarchy levels (1-9):
    - Level 9: superadmin (highest)
    - Level 8: admin
    - Level 7: company_admin, school_admin
    - Level 6: moderator
    - Level 5: support
    - Level 4: teacher
    - Level 3: creator
    - Level 2: premium
    - Level 1: free (lowest)
    """
    FREE = 'free'
    PREMIUM = 'premium'
    CREATOR = 'creator'
    TEACHER = 'teacher'
    SUPPORT = 'support'
    MODERATOR = 'moderator'
    SCHOOL_ADMIN = 'school_admin'
    COMPANY_ADMIN = 'company_admin'
    ADMIN = 'admin'
    SUPERADMIN = 'superadmin'

    @property
    def hierarchy_level(self) -> int:
        """Get the hierarchy level of this role."""
        levels = {
            UserRole.FREE: 1,
            UserRole.PREMIUM: 2,
            UserRole.CREATOR: 3,
            UserRole.TEACHER: 4,
            UserRole.SUPPORT: 5,
            UserRole.MODERATOR: 6,
            UserRole.SCHOOL_ADMIN: 7,
            UserRole.COMPANY_ADMIN: 7,
            UserRole.ADMIN: 8,
            UserRole.SUPERADMIN: 9,
        }
        return levels[self]

    def can_manage_role(self, target_role: 'UserRole') -> bool:
        """Check if this role can manage target role."""
        return self.hierarchy_level > target_role.hierarchy_level

    @classmethod
    def get_accessible_roles(cls, role: 'UserRole') -> Set['UserRole']:
        """Get roles that can be assigned by the given role."""
        role_enum = cls(role) if isinstance(role, str) else role
        level = role_enum.hierarchy_level
        return {r for r in cls if r.hierarchy_level < level}


class AccountStatus(str, Enum):
    """
    User account status.

    States:
    - ACTIVE: Normal active account
    - INACTIVE: Deactivated by user or admin
    - SUSPENDED: Temporarily suspended (e.g., pending investigation)
    - BANNED: Permanently banned
    - PENDING: Awaiting email verification
    """
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    BANNED = 'banned'
    PENDING = 'pending'

    @property
    def is_usable(self) -> bool:
        """Check if account can be used for authentication."""
        return self == AccountStatus.ACTIVE

    @property
    def can_login(self) -> bool:
        """Check if user can log in."""
        return self == AccountStatus.ACTIVE


class UserType(str, Enum):
    """
    User type classification for different contexts.

    Types:
    - INDIVIDUAL: Regular individual user
    - ORGANISATION_MEMBER: Member of school/company
    - ORGANISATION_ADMIN: Admin of school/company
    - SYSTEM_ADMIN: Platform administrator
    """
    INDIVIDUAL = 'individual'
    ORGANISATION_MEMBER = 'organisation_member'
    ORGANISATION_ADMIN = 'organisation_admin'
    SYSTEM_ADMIN = 'system_admin'

    @classmethod
    def from_role(cls, role: UserRole, has_organisation: bool = False) -> 'UserType':
        """Determine user type from role and organisation membership."""
        if role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            return cls.SYSTEM_ADMIN
        elif role in [UserRole.SCHOOL_ADMIN, UserRole.COMPANY_ADMIN]:
            return cls.ORGANISATION_ADMIN
        elif has_organisation:
            return cls.ORGANISATION_MEMBER
        else:
            return cls.INDIVIDUAL


class PermissionScope(str, Enum):
    """
    Permission scope definitions.

    Scopes:
    - OWN: Only own resources
    - ORGANISATION: Resources within own organisation
    - ALL: All resources (platform-wide)
    """
    OWN = 'own'
    ORGANISATION = 'organisation'
    ALL = 'all'

    @classmethod
    def for_role(cls, role: UserRole, has_organisation: bool = False) -> 'PermissionScope':
        """Determine permission scope for a role."""
        if role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            return cls.ALL
        elif role in [UserRole.SCHOOL_ADMIN, UserRole.COMPANY_ADMIN] and has_organisation:
            return cls.ORGANISATION
        else:
            return cls.OWN


# Type aliases for clarity
UserId = str  # UUID string
Email = str
OrganisationId = int | None


__all__ = [
    'UserRole',
    'AccountStatus',
    'UserType',
    'PermissionScope',
    'UserId',
    'Email',
    'OrganisationId',
]
