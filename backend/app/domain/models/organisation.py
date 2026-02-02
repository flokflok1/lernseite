"""
LernsystemX Organisation Models

Pydantic models for organisation-related operations:
- Organisation creation and management
- Branding configuration
- Organisation settings
- Multi-tenancy support

ISO 9001:2015 compliant - Organisation management standards
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict


class OrganisationType(str, Enum):
    """
    Organisation type enumeration

    Based on 25_Organisation-System.md:
    - school: Educational institutions (K-12, universities)
    - company: Corporate training and enterprise
    - teacher_team: Small teacher collaboration groups
    - creator_team: Content creator teams
    """
    SCHOOL = 'school'
    COMPANY = 'company'
    TEACHER_TEAM = 'teacher_team'
    CREATOR_TEAM = 'creator_team'


class OrgRole(str, Enum):
    """
    Organisation user role enumeration

    Roles within an organisation (from 01_Rollenmodell.md):
    - org_admin: Full organisation administration
    - teacher: Teacher/instructor role (schools)
    - trainer: Corporate trainer role (companies)
    - student: Student role (schools)
    - employee: Employee role (companies)
    """
    ORG_ADMIN = 'org_admin'
    TEACHER = 'teacher'
    TRAINER = 'trainer'
    STUDENT = 'student'
    EMPLOYEE = 'employee'


class BillingModel(str, Enum):
    """
    Organisation billing model enumeration

    From 25_Organisation-System.md and 06_Premium-Modell.md:
    - per_user: Charge per active user
    - flat: Flat monthly/annual fee
    - hybrid: Combination of base fee + per user
    """
    PER_USER = 'per_user'
    FLAT = 'flat'
    HYBRID = 'hybrid'


class OrgStatus(str, Enum):
    """
    Organisation status enumeration

    - active: Organisation is active and operational
    - suspended: Temporarily suspended (payment issues, violations)
    - deleted: Soft-deleted, pending permanent deletion
    """
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    DELETED = 'deleted'


class BrandingConfig(BaseModel):
    """
    Organisation branding configuration

    Example:
        >>> branding = BrandingConfig(
        ...     primary_color="#3b82f6",
        ...     secondary_color="#1e40af",
        ...     logo_url="/uploads/logo.png"
        ... )
    """
    primary_color: Optional[str] = Field(
        default="#2563eb",
        description="Primary brand color (hex)",
        pattern=r'^#[0-9a-fA-F]{6}$'
    )
    secondary_color: Optional[str] = Field(
        default="#1e40af",
        description="Secondary brand color (hex)",
        pattern=r'^#[0-9a-fA-F]{6}$'
    )
    logo_url: Optional[str] = Field(None, description="Logo image URL")
    favicon_url: Optional[str] = Field(None, description="Favicon URL")
    custom_css: Optional[str] = Field(None, description="Custom CSS")
    font_family: Optional[str] = Field(default="Inter", description="Custom font family")

    model_config = ConfigDict(from_attributes=True)


class OrganisationSettings(BaseModel):
    """
    Organisation settings

    From 25_Organisation-System.md - JSONB settings structure

    Example:
        >>> settings = OrganisationSettings(
        ...     allow_public_courses=False,
        ...     require_email_verification=True,
        ...     max_users=1000,
        ...     liveroom_enabled=True
        ... )
    """
    # Feature flags
    liveroom_enabled: bool = Field(default=True, description="Enable LiveRoom features")
    whiteboard_enabled: bool = Field(default=True, description="Enable whiteboard in LiveRooms")
    exams_enabled: bool = Field(default=True, description="Enable exam system")
    ai_enabled: bool = Field(default=True, description="Enable AI features")

    # User management
    allow_public_courses: bool = Field(default=True, description="Allow public courses")
    allow_user_creation: bool = Field(default=True, description="Allow user self-registration")
    require_email_verification: bool = Field(default=True, description="Require email verification")

    # Limits
    max_users: Optional[int] = Field(None, ge=0, description="Maximum users (None = unlimited)")
    max_classes: Optional[int] = Field(None, ge=0, description="Maximum classes (schools)")
    max_courses: Optional[int] = Field(None, ge=0, description="Maximum courses")

    # Preferences
    language: str = Field(default="de", description="Default language (de/en)")
    timezone: str = Field(default="Europe/Berlin", description="Organisation timezone")

    # Privacy and security
    dsgvo_mode: bool = Field(default=False, description="DSGVO school mode (strict privacy)")
    corporate_security: bool = Field(default=False, description="Corporate security mode")

    # Welcome message
    welcome_message: Optional[str] = Field(None, description="Custom welcome message for users")

    model_config = ConfigDict(from_attributes=True)


class OrganisationBase(BaseModel):
    """
    Base organisation model

    Example:
        >>> org = OrganisationBase(
        ...     name="Example School",
        ...     org_type="school"
        ... )
    """
    name: str = Field(..., min_length=2, max_length=255, description="Organisation name")
    org_type: str = Field(..., description="Organisation type (school, company, teacher_team, creator_team)")

    @field_validator('org_type')
    @classmethod
    def validate_org_type(cls, v: str) -> str:
        """Validate organisation type"""
        valid_types = [t.value for t in OrganisationType]
        if v not in valid_types:
            raise ValueError(f'org_type must be one of: {", ".join(valid_types)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class OrganisationCreate(OrganisationBase):
    """
    Organisation creation model

    Example:
        >>> org_data = OrganisationCreate(
        ...     name="Tech University",
        ...     org_type="school",
        ...     domain="tech.edu",
        ...     billing_model="per_user",
        ...     branding={"primary_color": "#ff5733"},
        ...     settings={"max_users": 5000}
        ... )
    """
    domain: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Organisation domain (must be unique)"
    )
    billing_model: str = Field(
        default="per_user",
        description="Billing model (per_user, flat, hybrid)"
    )
    token_pool: int = Field(
        default=0,
        ge=0,
        description="Initial token pool for AI features"
    )
    branding: Optional[BrandingConfig] = Field(None, description="Branding configuration")
    settings: Optional[OrganisationSettings] = Field(None, description="Organisation settings")

    @field_validator('billing_model')
    @classmethod
    def validate_billing_model(cls, v: str) -> str:
        """Validate billing model"""
        valid_models = [m.value for m in BillingModel]
        if v not in valid_models:
            raise ValueError(f'billing_model must be one of: {", ".join(valid_models)}')
        return v

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        """Validate domain format"""
        if v is None:
            return v

        # Basic domain validation (simplified)
        import re
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, v):
            raise ValueError('Invalid domain format')
        return v.lower()

    model_config = ConfigDict(from_attributes=True)


class OrganisationUpdate(BaseModel):
    """
    Organisation update model

    All fields are optional for partial updates.

    Example:
        >>> update = OrganisationUpdate(name="Updated Name", status="active")
    """
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    domain: Optional[str] = Field(None, min_length=3, max_length=255)
    billing_model: Optional[str] = None
    branding: Optional[BrandingConfig] = None
    settings: Optional[OrganisationSettings] = None
    status: Optional[str] = None

    @field_validator('billing_model')
    @classmethod
    def validate_billing_model(cls, v: Optional[str]) -> Optional[str]:
        """Validate billing model"""
        if v is None:
            return v
        valid_models = [m.value for m in BillingModel]
        if v not in valid_models:
            raise ValueError(f'billing_model must be one of: {", ".join(valid_models)}')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status"""
        if v is None:
            return v
        valid_statuses = [s.value for s in OrgStatus]
        if v not in valid_statuses:
            raise ValueError(f'status must be one of: {", ".join(valid_statuses)}')
        return v

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        """Validate domain format"""
        if v is None:
            return v

        import re
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, v):
            raise ValueError('Invalid domain format')
        return v.lower()

    model_config = ConfigDict(from_attributes=True)


class OrganisationResponse(OrganisationBase):
    """
    Organisation response model

    Example:
        >>> org = OrganisationResponse(
        ...     org_id=1,
        ...     name="LSX Academy",
        ...     org_type="school",
        ...     domain="lsx.de",
        ...     status="active",
        ...     created_at=datetime.now()
        ... )
    """
    org_id: int = Field(..., description="Organisation ID")
    domain: Optional[str] = Field(None, description="Organisation domain")
    billing_model: str = Field(..., description="Billing model")
    token_pool: int = Field(default=0, description="Token pool balance")
    token_used: int = Field(default=0, description="Tokens consumed")
    branding: Optional[Dict[str, Any]] = Field(None, description="Branding configuration")
    settings: Optional[Dict[str, Any]] = Field(None, description="Organisation settings")
    status: str = Field(default="active", description="Organisation status")
    created_at: datetime = Field(..., description="Organisation creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Additional computed fields (optional)
    user_count: Optional[int] = Field(None, description="Number of users")
    course_count: Optional[int] = Field(None, description="Number of courses")

    model_config = ConfigDict(from_attributes=True)


class OrganisationDetailResponse(OrganisationResponse):
    """
    Detailed organisation response with settings

    Example:
        >>> org = OrganisationDetailResponse(
        ...     organisation_id=1,
        ...     name="LSX Academy",
        ...     type="system",
        ...     settings={...},
        ...     branding={...}
        ... )
    """
    settings: Optional[Dict[str, Any]] = Field(None, description="Organisation settings")
    subscription_plan: Optional[str] = Field(None, description="Subscription plan")
    subscription_status: Optional[str] = Field(None, description="Subscription status")

    model_config = ConfigDict(from_attributes=True)


class OrganisationListResponse(BaseModel):
    """
    Paginated organisation list response

    Example:
        >>> org_list = OrganisationListResponse(
        ...     items=[org1, org2],
        ...     total=25,
        ...     page=1,
        ...     per_page=10
        ... )
    """
    items: List[OrganisationResponse] = Field(..., description="List of organisations")
    total: int = Field(..., description="Total number of organisations")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_prev: bool = Field(..., description="Has previous page")
    has_next: bool = Field(..., description="Has next page")

    model_config = ConfigDict(from_attributes=True)


class OrganisationStats(BaseModel):
    """
    Organisation statistics

    Example:
        >>> stats = OrganisationStats(
        ...     total_users=1500,
        ...     active_users=1200,
        ...     total_courses=85,
        ...     published_courses=70
        ... )
    """
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    total_courses: int = Field(..., description="Total number of courses")
    published_courses: int = Field(..., description="Number of published courses")
    total_enrollments: int = Field(..., description="Total course enrollments")
    token_usage: Optional[int] = Field(None, description="Total AI tokens used")
    token_balance: Optional[int] = Field(None, description="Remaining AI token balance")

    model_config = ConfigDict(from_attributes=True)


class TokenPoolCreate(BaseModel):
    """
    Token pool creation for organisation

    Example:
        >>> pool = TokenPoolCreate(
        ...     organisation_id=5,
        ...     initial_tokens=50000
        ... )
    """
    organisation_id: int = Field(..., description="Organisation ID")
    initial_tokens: int = Field(default=10000, ge=0, description="Initial token amount")

    model_config = ConfigDict(from_attributes=True)


class TokenAllocation(BaseModel):
    """
    Allocate tokens to user from organisation pool

    Example:
        >>> allocation = TokenAllocation(
        ...     user_id=10,
        ...     amount=1000
        ... )
    """
    user_id: int = Field(..., description="User ID to allocate tokens to")
    amount: int = Field(..., gt=0, description="Number of tokens to allocate")

    model_config = ConfigDict(from_attributes=True)


# Organisation User Models

class OrganisationUserBase(BaseModel):
    """
    Base model for organisation user association

    Example:
        >>> org_user = OrganisationUserBase(
        ...     user_id=123,
        ...     org_role="teacher"
        ... )
    """
    user_id: int = Field(..., description="User ID")
    org_role: str = Field(..., description="Role within organisation")

    @field_validator('org_role')
    @classmethod
    def validate_org_role(cls, v: str) -> str:
        """Validate organisation role"""
        valid_roles = [r.value for r in OrgRole]
        if v not in valid_roles:
            raise ValueError(f'org_role must be one of: {", ".join(valid_roles)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class OrganisationUserResponse(OrganisationUserBase):
    """
    Organisation user response model

    Example:
        >>> org_user = OrganisationUserResponse(
        ...     id=1,
        ...     org_id=5,
        ...     user_id=123,
        ...     org_role="teacher",
        ...     status="active",
        ...     joined_at=datetime.now()
        ... )
    """
    id: int = Field(..., description="Organisation user association ID")
    org_id: int = Field(..., description="Organisation ID")
    status: str = Field(default="active", description="User status in organisation")
    joined_at: datetime = Field(..., description="Date joined organisation")
    created_at: datetime = Field(..., description="Record creation timestamp")

    # User details (optional, joined from users table)
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    email: Optional[str] = Field(None, description="User email")

    model_config = ConfigDict(from_attributes=True)


class OrganisationAssignUserRequest(BaseModel):
    """
    Request model for assigning user to organisation

    Example:
        >>> request = OrganisationAssignUserRequest(
        ...     user_id=123,
        ...     org_role="student"
        ... )
    """
    user_id: int = Field(..., description="User ID to assign")
    org_role: str = Field(default="student", description="Role to assign")

    @field_validator('org_role')
    @classmethod
    def validate_org_role(cls, v: str) -> str:
        """Validate organisation role"""
        valid_roles = [r.value for r in OrgRole]
        if v not in valid_roles:
            raise ValueError(f'org_role must be one of: {", ".join(valid_roles)}')
        return v

    model_config = ConfigDict(from_attributes=True)


# Organisation Class Models

class OrganisationClassBase(BaseModel):
    """
    Base model for organisation classes (schools)

    Example:
        >>> class_data = OrganisationClassBase(
        ...     name="Mathematik 10a",
        ...     description="Klasse 10a Mathematik"
        ... )
    """
    name: str = Field(..., min_length=1, max_length=255, description="Class name")
    description: Optional[str] = Field(None, description="Class description")
    year: Optional[int] = Field(None, ge=2020, le=2100, description="School year")
    semester: Optional[str] = Field(None, description="Semester (WS, SS, Q1, Q2, etc.)")

    model_config = ConfigDict(from_attributes=True)


class OrganisationClassResponse(OrganisationClassBase):
    """
    Organisation class response model

    Example:
        >>> class_obj = OrganisationClassResponse(
        ...     class_id=1,
        ...     org_id=5,
        ...     name="Klasse 10a",
        ...     year=2024,
        ...     created_at=datetime.now()
        ... )
    """
    class_id: int = Field(..., description="Class ID")
    org_id: int = Field(..., description="Organisation ID")
    created_at: datetime = Field(..., description="Class creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Optional computed fields
    student_count: Optional[int] = Field(None, description="Number of students")
    teacher_count: Optional[int] = Field(None, description="Number of teachers")

    model_config = ConfigDict(from_attributes=True)


# Organisation Statistics Response (with billing/token integration)

class OrganisationStatsResponse(BaseModel):
    """
    Comprehensive organisation statistics response

    Includes integration with subscription and token systems as requested.

    Example:
        >>> stats = OrganisationStatsResponse(
        ...     org_id=5,
        ...     total_users=150,
        ...     active_users=142,
        ...     total_courses=25,
        ...     subscription_plan="school_plan",
        ...     token_wallet={"balance": 50000, "used": 12000}
        ... )
    """
    # Organisation ID
    org_id: int = Field(..., description="Organisation ID")

    # User statistics
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    users_by_role: Optional[Dict[str, int]] = Field(
        None,
        description="User counts by role (org_admin, teacher, student, etc.)"
    )

    # Course statistics
    total_courses: int = Field(..., description="Total number of courses")
    active_courses: int = Field(..., description="Number of active/published courses")
    total_enrollments: Optional[int] = Field(None, description="Total course enrollments")

    # Class statistics (for schools)
    total_classes: Optional[int] = Field(None, description="Total number of classes")

    # Token usage (integrated with TokenRepository)
    token_wallet: Dict[str, Any] = Field(
        ...,
        description="Token wallet info (balance, used, reserved, etc.)"
    )

    # Subscription info (integrated with SubscriptionRepository)
    subscription_plan: Optional[str] = Field(None, description="Subscription plan name")
    subscription_status: Optional[str] = Field(None, description="Subscription status")
    subscription_expires_at: Optional[datetime] = Field(None, description="Subscription expiry date")

    # AI usage aggregated (optional)
    ai_usage: Optional[Dict[str, Any]] = Field(
        None,
        description="AI usage statistics (optional)"
    )

    model_config = ConfigDict(from_attributes=True)
