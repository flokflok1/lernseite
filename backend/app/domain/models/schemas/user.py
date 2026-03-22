"""
LernsystemX User Models

Pydantic models for user-related operations:
- User registration and authentication
- Profile management
- Password operations
- Email verification
- Two-factor authentication

ISO 27001:2013 compliant - Secure user data handling
"""

from typing import Optional, List, Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
import re

# Import shared validators to eliminate duplication
from app.domain.models.schemas.validators import (
    validate_password_strength,
    validate_role,
    validate_totp_code
)


class UserBase(BaseModel):
    """
    Base user model with common fields

    Used as foundation for other user models.
    DB schema uses full_name (not separate first_name/last_name).
    """
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="User full name")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserCreate(UserBase):
    """
    User registration model

    Example:
        >>> user_data = UserCreate(
        ...     email="user@example.com",
        ...     password="SecurePass123!",
        ...     full_name="John Doe",
        ...     username="johndoe"
        ... )
    """
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]{3,50}$',
        description="Username (3-50 chars, alphanumeric + _ -)"
    )
    password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="User password (min 12 chars, must contain uppercase, lowercase, digit, special char)"
    )
    role: Optional[str] = Field(
        default="user",
        description="User role (user, premium, teacher, admin, etc.)"
    )
    organisation_id: Optional[int] = Field(
        default=None,
        description="Organisation ID (for school/company users)"
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength_validator(cls, v: str) -> str:
        """
        Validate password strength.

        Delegates to shared validate_password_strength() validator.
        """
        return validate_password_strength(v)

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate user role"""
        valid_roles = [
            'user', 'premium', 'creator', 'teacher',
            'school_admin', 'company_admin', 'moderator',
            'support', 'admin', 'superadmin'
        ]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


class UserUpdate(BaseModel):
    """
    User profile update model

    All fields are optional for partial updates.

    Example:
        >>> update_data = UserUpdate(full_name="Jane Doe")
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = None
    organisation_id: Optional[int] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """
    User login model

    Example:
        >>> login_data = UserLogin(
        ...     email="user@example.com",
        ...     password="SecurePass123!"
        ... )
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    totp_code: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=6,
        description="6-digit TOTP code (if 2FA enabled)"
    )

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """
    User response model (safe for API responses)

    Excludes sensitive fields like password_hash.
    Uses Group-Based Architecture (GBA) - authorization via groups only, no role field.

    Example:
        >>> user = UserResponse(
        ...     user_id="8828daa5-213d-46b9-981a-a1c6f3233afd",
        ...     email="user@example.com",
        ...     full_name="John Doe",
        ...     email_verified=True,
        ...     is_active=True,
        ...     created_at=datetime.now()
        ... )
    """
    user_id: Union[str, UUID] = Field(..., description="User ID (UUID)")
    organisation_id: Optional[Union[str, UUID]] = Field(None, description="Organisation ID (UUID)")

    @field_validator('user_id', 'organisation_id', mode='before')
    @classmethod
    def coerce_uuid_to_str(cls, v):
        if v is not None:
            return str(v)
        return v
    two_factor_enabled: bool = Field(default=False, description="2FA enabled")
    email_verified: bool = Field(default=False, description="Email verified")
    is_active: bool = Field(default=True, description="Account active status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserProfile(UserResponse):
    """
    Extended user profile with additional information

    Example:
        >>> profile = UserProfile(
        ...     user_id="8828daa5-213d-46b9-981a-a1c6f3233afd",
        ...     email="user@example.com",
        ...     full_name="John Doe",
        ...     subscription_plan="premium",
        ...     token_balance=5000
        ... )
    """
    subscription_plan: Optional[str] = Field(None, description="Subscription plan (free, premium, pro)")
    subscription_status: Optional[str] = Field(None, description="Subscription status")
    token_balance: Optional[int] = Field(None, description="Available AI tokens")
    courses_enrolled: Optional[int] = Field(None, description="Number of enrolled courses")
    courses_created: Optional[int] = Field(None, description="Number of created courses")

    model_config = ConfigDict(from_attributes=True)


class PasswordChange(BaseModel):
    """
    Password change model

    Example:
        >>> pwd_change = PasswordChange(
        ...     current_password="OldPass123!",
        ...     new_password="NewPass456!",
        ...     confirm_password="NewPass456!"
        ... )
    """
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="New password"
    )
    confirm_password: str = Field(..., description="Confirm new password")

    @field_validator('new_password')
    @classmethod
    def validate_password_strength_validator(cls, v: str) -> str:
        """
        Validate new password strength.

        Delegates to shared validate_password_strength() validator.
        """
        return validate_password_strength(v)

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Validate that passwords match"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v

    model_config = ConfigDict(from_attributes=True)


class PasswordReset(BaseModel):
    """
    Password reset model (via email token)

    Example:
        >>> reset = PasswordReset(
        ...     token="abc123...",
        ...     new_password="NewPass456!",
        ...     confirm_password="NewPass456!"
        ... )
    """
    token: str = Field(..., description="Password reset token from email")
    new_password: str = Field(..., min_length=12, max_length=128)
    confirm_password: str = Field(...)

    @field_validator('new_password')
    @classmethod
    def validate_password_strength_validator(cls, v: str) -> str:
        """
        Validate password strength.

        Delegates to shared validate_password_strength() validator.
        """
        return validate_password_strength(v)

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Validate that passwords match"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v

    model_config = ConfigDict(from_attributes=True)


class EmailVerification(BaseModel):
    """
    Email verification model

    Example:
        >>> verification = EmailVerification(token="xyz789...")
    """
    token: str = Field(..., description="Email verification token")

    model_config = ConfigDict(from_attributes=True)


class TwoFactorSetup(BaseModel):
    """
    Two-factor authentication setup model

    Example:
        >>> twofa = TwoFactorSetup(
        ...     totp_code="123456"
        ... )
    """
    totp_code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6-digit TOTP code for verification"
    )

    @field_validator('totp_code')
    @classmethod
    def validate_totp_code_validator(cls, v: str) -> str:
        """
        Validate TOTP code format.

        Delegates to shared validate_totp_code() validator.
        """
        return validate_totp_code(v)

    model_config = ConfigDict(from_attributes=True)


class TwoFactorDisable(BaseModel):
    """
    Two-factor authentication disable model

    Example:
        >>> disable_2fa = TwoFactorDisable(
        ...     password="CurrentPass123!",
        ...     totp_code="123456"
        ... )
    """
    password: str = Field(..., description="Current password for verification")
    totp_code: str = Field(..., min_length=6, max_length=6, description="Current TOTP code")

    @field_validator('totp_code')
    @classmethod
    def validate_totp_code_validator(cls, v: str) -> str:
        """
        Validate TOTP code format.

        Delegates to shared validate_totp_code() validator.
        """
        return validate_totp_code(v)

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """
    Paginated user list response

    Example:
        >>> user_list = UserListResponse(
        ...     items=[user1, user2, user3],
        ...     total=100,
        ...     page=1,
        ...     per_page=10,
        ...     total_pages=10
        ... )
    """
    items: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_prev: bool = Field(..., description="Has previous page")
    has_next: bool = Field(..., description="Has next page")

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """
    JWT token response

    Example:
        >>> token = TokenResponse(
        ...     access_token="eyJ0eXAiOiJKV1QiLCJhbGc...",
        ...     token_type="bearer",
        ...     expires_in=3600
        ... )
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="Authenticated user data")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Theme Preference Models (Phase B24 - Theme Support)
# ============================================================================

class ThemePreferenceResponse(BaseModel):
    """
    Theme preference response model

    Returns the current theme setting for a user.

    Example:
        >>> theme = ThemePreferenceResponse(theme="dark")
    """
    theme: str = Field(
        ...,
        description="User theme preference (system, light, or dark)",
        pattern="^(system|light|dark)$"
    )

    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v: str) -> str:
        """Validate theme value"""
        valid_themes = ['system', 'light', 'dark']
        if v not in valid_themes:
            raise ValueError(f'Theme must be one of: {", ".join(valid_themes)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class ThemePreferenceUpdateRequest(BaseModel):
    """
    Theme preference update request model

    Used to update a user's theme preference.

    Example:
        >>> update = ThemePreferenceUpdateRequest(theme="light")
    """
    theme: str = Field(
        ...,
        description="New theme preference (system, light, or dark)",
        pattern="^(system|light|dark)$"
    )

    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v: str) -> str:
        """
        Validate theme value

        Args:
            v: Theme value to validate

        Returns:
            Validated theme value

        Raises:
            ValueError: If theme is not one of the valid values
        """
        valid_themes = ['system', 'light', 'dark']
        if v not in valid_themes:
            raise ValueError(f'Theme must be one of: {", ".join(valid_themes)}')
        return v

    model_config = ConfigDict(from_attributes=True)
