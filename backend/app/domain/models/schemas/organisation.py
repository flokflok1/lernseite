"""
LernsystemX Organisation Models

Pydantic models for organisation-related operations:
- Organisation creation and management
- Branding configuration
- Organisation settings
- Multi-tenancy support

For token, user association, class, and stats models see organisation_part2.py

ISO 9001:2015 compliant - Organisation management standards
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict

from app.domain.models.enums import OrganisationType, OrgRole, BillingModel, OrgStatus


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
