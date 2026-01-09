"""
Organisation Domain Value Objects

DDD Value Objects for Organisation domain:
- OrgType: Organisation type with business rules
- MemberRole: Member role with permissions
- BillingModel: Billing model with behavior

Value Objects are immutable and enforce domain constraints.

ISO 27001:2013 compliant - Type-safe domain concepts
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class OrgType:
    """
    Organisation Type Value Object.

    Immutable representation of organisation type with validation and business rules.

    Valid Types:
        - school: Educational institution
        - company: Business organisation
        - teacher_team: Collaborative teacher group
        - creator_team: Content creator team

    Business Rules:
        - Enterprise types (school, company) get higher token pools
        - Team types have member limits
        - Token allocation differs by type
    """

    value: str

    # Type Constants
    SCHOOL = 'school'
    COMPANY = 'company'
    TEACHER_TEAM = 'teacher_team'
    CREATOR_TEAM = 'creator_team'

    VALID_TYPES = [SCHOOL, COMPANY, TEACHER_TEAM, CREATOR_TEAM]

    def __post_init__(self):
        """Validate organisation type on creation"""
        if self.value not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid organisation type: {self.value}. "
                f"Must be one of: {', '.join(self.VALID_TYPES)}"
            )

    @property
    def is_enterprise(self) -> bool:
        """Check if organisation is enterprise type (school or company)"""
        return self.value in [self.SCHOOL, self.COMPANY]

    @property
    def is_team(self) -> bool:
        """Check if organisation is team type"""
        return self.value in [self.TEACHER_TEAM, self.CREATOR_TEAM]

    @property
    def default_token_pool(self) -> int:
        """
        Get default token pool based on organisation type.

        Business Rules:
            - school: 50,000 tokens
            - company: 100,000 tokens
            - teacher_team: 10,000 tokens
            - creator_team: 25,000 tokens
        """
        token_pools = {
            self.SCHOOL: 50000,
            self.COMPANY: 100000,
            self.TEACHER_TEAM: 10000,
            self.CREATOR_TEAM: 25000
        }
        return token_pools.get(self.value, 0)

    @property
    def default_member_limit(self) -> Optional[int]:
        """
        Get default member limit based on organisation type.

        Business Rules:
            - school: No limit (None)
            - company: No limit (None)
            - teacher_team: 20 members
            - creator_team: 10 members
        """
        limits = {
            self.SCHOOL: None,
            self.COMPANY: None,
            self.TEACHER_TEAM: 20,
            self.CREATOR_TEAM: 10
        }
        return limits.get(self.value)

    @property
    def default_billing_model(self) -> str:
        """
        Get default billing model based on organisation type.

        Business Rules:
            - school: per_user
            - company: per_user
            - teacher_team: flat
            - creator_team: flat
        """
        models = {
            self.SCHOOL: 'per_user',
            self.COMPANY: 'per_user',
            self.TEACHER_TEAM: 'flat',
            self.CREATOR_TEAM: 'flat'
        }
        return models.get(self.value, 'per_user')

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if isinstance(other, OrgType):
            return self.value == other.value
        return self.value == other


@dataclass(frozen=True)
class MemberRole:
    """
    Member Role Value Object.

    Immutable representation of organisation member roles with permissions.

    Valid Roles:
        - org_admin: Organisation administrator (full control)
        - teacher: Teaching staff (can manage students)
        - trainer: Corporate trainer (can manage employees)
        - student: Student (limited access)
        - employee: Company employee (limited access)
        - member: General member (basic access)

    Business Rules:
        - Only org_admin can manage members
        - Teacher/Trainer can view analytics
        - Students/Employees have read-only access
    """

    value: str

    # Role Constants
    ORG_ADMIN = 'org_admin'
    TEACHER = 'teacher'
    TRAINER = 'trainer'
    STUDENT = 'student'
    EMPLOYEE = 'employee'
    MEMBER = 'member'

    VALID_ROLES = [ORG_ADMIN, TEACHER, TRAINER, STUDENT, EMPLOYEE, MEMBER]

    def __post_init__(self):
        """Validate member role on creation"""
        if self.value not in self.VALID_ROLES:
            raise ValueError(
                f"Invalid member role: {self.value}. "
                f"Must be one of: {', '.join(self.VALID_ROLES)}"
            )

    @property
    def can_manage_members(self) -> bool:
        """Check if role can manage organisation members"""
        return self.value == self.ORG_ADMIN

    @property
    def can_view_analytics(self) -> bool:
        """Check if role can view organisation analytics"""
        return self.value in [self.ORG_ADMIN, self.TEACHER, self.TRAINER]

    @property
    def can_edit_settings(self) -> bool:
        """Check if role can edit organisation settings"""
        return self.value == self.ORG_ADMIN

    @property
    def can_manage_courses(self) -> bool:
        """Check if role can manage courses"""
        return self.value in [self.ORG_ADMIN, self.TEACHER, self.TRAINER]

    @property
    def is_staff(self) -> bool:
        """Check if role is staff (not student/employee)"""
        return self.value in [self.ORG_ADMIN, self.TEACHER, self.TRAINER]

    @property
    def hierarchy_level(self) -> int:
        """
        Get role hierarchy level (higher = more permissions).

        Used for permission checks and role comparison.
        """
        levels = {
            self.ORG_ADMIN: 100,
            self.TEACHER: 50,
            self.TRAINER: 50,
            self.MEMBER: 20,
            self.STUDENT: 10,
            self.EMPLOYEE: 10
        }
        return levels.get(self.value, 0)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if isinstance(other, MemberRole):
            return self.value == other.value
        return self.value == other

    def __lt__(self, other) -> bool:
        """Compare roles by hierarchy level"""
        if isinstance(other, MemberRole):
            return self.hierarchy_level < other.hierarchy_level
        return False


@dataclass(frozen=True)
class BillingModel:
    """
    Billing Model Value Object.

    Immutable representation of organisation billing model.

    Valid Models:
        - per_user: Billed per active user
        - flat: Flat rate regardless of users
        - hybrid: Combination of flat base + per user

    Business Rules:
        - per_user: Requires user count tracking
        - flat: Fixed monthly/annual fee
        - hybrid: Base fee + per user above threshold
    """

    value: str

    # Model Constants
    PER_USER = 'per_user'
    FLAT = 'flat'
    HYBRID = 'hybrid'

    VALID_MODELS = [PER_USER, FLAT, HYBRID]

    def __post_init__(self):
        """Validate billing model on creation"""
        if self.value not in self.VALID_MODELS:
            raise ValueError(
                f"Invalid billing model: {self.value}. "
                f"Must be one of: {', '.join(self.VALID_MODELS)}"
            )

    @property
    def requires_user_count(self) -> bool:
        """Check if billing model requires user count tracking"""
        return self.value in [self.PER_USER, self.HYBRID]

    @property
    def requires_base_fee(self) -> bool:
        """Check if billing model requires base fee"""
        return self.value in [self.FLAT, self.HYBRID]

    @property
    def is_usage_based(self) -> bool:
        """Check if billing is usage-based"""
        return self.value in [self.PER_USER, self.HYBRID]

    def calculate_cost(
        self,
        base_fee: float,
        per_user_fee: float,
        user_count: int,
        free_tier_users: int = 0
    ) -> float:
        """
        Calculate billing cost based on model and parameters.

        Args:
            base_fee: Base monthly/annual fee
            per_user_fee: Fee per user
            user_count: Number of active users
            free_tier_users: Number of users included in base fee (default: 0)

        Returns:
            Total cost in billing currency
        """
        if self.value == self.FLAT:
            return base_fee

        elif self.value == self.PER_USER:
            billable_users = max(0, user_count - free_tier_users)
            return billable_users * per_user_fee

        elif self.value == self.HYBRID:
            billable_users = max(0, user_count - free_tier_users)
            return base_fee + (billable_users * per_user_fee)

        return 0.0

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if isinstance(other, BillingModel):
            return self.value == other.value
        return self.value == other
