"""
LernsystemX Organisation Models (Part 2)

Continuation of organisation.py - contains:
- Token pool and allocation models
- Organisation user association models
- Organisation class models (schools)
- Comprehensive organisation statistics response

ISO 9001:2015 compliant - Organisation management standards
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.domain.models.schemas.organisation import OrgRole


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
