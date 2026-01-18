"""
Shared Pydantic Validators Module

Centralizes reusable validators for Pydantic models to eliminate code duplication
and ensure consistent validation across the application.

This module provides:
- Password strength validation (extract from UserCreate, PasswordChange, PasswordReset)
- TOTP code validation (extract from TwoFactorSetup, TwoFactorDisable)
- Generic validators for enum-like fields (role, language)
- Complex validators (ownership/XOR, content presence, slug format, hex color)

All validators follow Pydantic v2 @field_validator pattern and include
error messages compatible with the i18n system.

ISO 27001:2013 compliant - Input validation
"""

from typing import List, Optional
import re
from pydantic import field_validator, ValidationInfo


# ============================================================================
# PASSWORD VALIDATORS (Extracted from 3 duplicate locations)
# ============================================================================

def validate_password_strength(v: str) -> str:
    """
    Validate password strength for user creation and password changes.

    Requirements:
    - At least 12 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one digit (0-9)
    - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

    Args:
        v: Password string to validate

    Returns:
        The validated password string

    Raises:
        ValueError: If password does not meet requirements

    Example:
        >>> validate_password_strength("SecurePass123!")
        'SecurePass123!'

        >>> validate_password_strength("weak")  # Too short
        ValueError: Password must be at least 12 characters long
    """
    if len(v) < 12:
        raise ValueError('PASSWORD_TOO_SHORT')

    if not any(c.isupper() for c in v):
        raise ValueError('PASSWORD_MISSING_UPPERCASE')

    if not any(c.islower() for c in v):
        raise ValueError('PASSWORD_MISSING_LOWERCASE')

    if not any(c.isdigit() for c in v):
        raise ValueError('PASSWORD_MISSING_DIGIT')

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in v):
        raise ValueError('PASSWORD_MISSING_SPECIAL')

    return v


def validate_password_mismatch(new_password: str, confirm_password: str) -> None:
    """
    Validate that two passwords match.

    Used for password change and reset forms where confirmation is required.

    Args:
        new_password: New password value
        confirm_password: Confirmation password value

    Raises:
        ValueError: If passwords do not match

    Example:
        >>> validate_password_mismatch("SecurePass123!", "SecurePass123!")
        # No error

        >>> validate_password_mismatch("SecurePass123!", "DifferentPass456!")
        ValueError: PASSWORD_MISMATCH
    """
    if new_password != confirm_password:
        raise ValueError('PASSWORD_MISMATCH')


# ============================================================================
# TOTP (TWO-FACTOR AUTHENTICATION) VALIDATORS (Extracted from 2 locations)
# ============================================================================

def validate_totp_code(v: str) -> str:
    """
    Validate TOTP (Time-based One-Time Password) code format.

    Requirements:
    - Exactly 6 digits
    - Only numeric characters

    Args:
        v: TOTP code string to validate

    Returns:
        The validated TOTP code string

    Raises:
        ValueError: If code format is invalid

    Example:
        >>> validate_totp_code("123456")
        '123456'

        >>> validate_totp_code("12345")  # Too short
        ValueError: TOTP_INVALID_LENGTH

        >>> validate_totp_code("12345a")  # Contains non-digit
        ValueError: TOTP_INVALID_FORMAT
    """
    if not v.isdigit():
        raise ValueError('TOTP_INVALID_FORMAT')

    if len(v) != 6:
        raise ValueError('TOTP_INVALID_LENGTH')

    return v


# ============================================================================
# ENUM/ROLE VALIDATORS (Generic, used across multiple models)
# ============================================================================

def validate_role(v: str, valid_roles: Optional[List[str]] = None) -> str:
    """
    Validate user role against allowed values.

    Args:
        v: Role string to validate
        valid_roles: List of allowed roles. If None, uses default LSX roles.

    Returns:
        The validated role string

    Raises:
        ValueError: If role not in allowed list

    Example:
        >>> validate_role("admin")
        'admin'

        >>> validate_role("invalid_role")
        ValueError: ROLE_INVALID
    """
    if valid_roles is None:
        valid_roles = [
            'user',
            'premium',
            'creator',
            'teacher',
            'school_admin',
            'company_admin',
            'moderator',
            'support',
            'admin',
            'superadmin'
        ]

    if v not in valid_roles:
        raise ValueError('ROLE_INVALID')

    return v


def validate_language(v: str, valid_languages: Optional[List[str]] = None) -> str:
    """
    Validate language code against supported languages.

    Args:
        v: Language code to validate (e.g., 'en', 'de', 'pl')
        valid_languages: List of allowed language codes. If None, uses default LSX languages.

    Returns:
        The validated language code string

    Raises:
        ValueError: If language not supported

    Example:
        >>> validate_language("de")
        'de'

        >>> validate_language("xx")
        ValueError: LANGUAGE_UNSUPPORTED
    """
    if valid_languages is None:
        valid_languages = ['de', 'en', 'pl']  # LSX supported languages

    if v not in valid_languages:
        raise ValueError('LANGUAGE_UNSUPPORTED')

    return v


# ============================================================================
# COMPLEX VALIDATORS (Multi-field, ownership, content presence)
# ============================================================================

def validate_ownership_xor(
    obj: dict,
    field_a: str,
    field_b: str,
    error_code: str = 'OWNERSHIP_XOR_INVALID'
) -> None:
    """
    Validate XOR (exclusive OR) constraint: either field_a or field_b must be set, but not both.

    Used for ownership fields like (user_id OR organization_id, but not both).

    Args:
        obj: Dictionary containing the field values
        field_a: Name of first field
        field_b: Name of second field
        error_code: Error code to raise if validation fails

    Raises:
        ValueError: If both fields are set or both are empty

    Example:
        >>> validate_ownership_xor({'user_id': '123', 'org_id': None}, 'user_id', 'org_id')
        # Valid

        >>> validate_ownership_xor({'user_id': '123', 'org_id': '456'}, 'user_id', 'org_id')
        ValueError: OWNERSHIP_XOR_INVALID
    """
    has_a = obj.get(field_a) is not None and obj.get(field_a) != ''
    has_b = obj.get(field_b) is not None and obj.get(field_b) != ''

    if (has_a and has_b) or (not has_a and not has_b):
        raise ValueError(error_code)


def validate_content_presence(
    obj: dict,
    fields: List[str],
    error_code: str = 'CONTENT_REQUIRED'
) -> None:
    """
    Validate that at least one of the specified fields has content (is non-empty).

    Used for posts, comments, etc. where at least one of (content, media) must be provided.

    Args:
        obj: Dictionary containing the field values
        fields: List of field names (at least one must have content)
        error_code: Error code to raise if validation fails

    Raises:
        ValueError: If all fields are empty

    Example:
        >>> validate_content_presence({'content': 'Hello', 'media': None}, ['content', 'media'])
        # Valid

        >>> validate_content_presence({'content': '', 'media': None}, ['content', 'media'])
        ValueError: CONTENT_REQUIRED
    """
    for field in fields:
        value = obj.get(field)
        if value and str(value).strip():  # Check if not empty
            return

    raise ValueError(error_code)


# ============================================================================
# FORMAT VALIDATORS (Slug, hex color, etc.)
# ============================================================================

def validate_slug(v: str) -> str:
    """
    Validate slug format for URLs and identifiers.

    Requirements:
    - Only lowercase letters, digits, and hyphens
    - Must start with letter or digit
    - Must end with letter or digit
    - At least 1 character

    Args:
        v: Slug string to validate

    Returns:
        The validated slug string

    Raises:
        ValueError: If slug format is invalid

    Example:
        >>> validate_slug("my-course-title")
        'my-course-title'

        >>> validate_slug("My-Course-Title")  # Contains uppercase
        ValueError: SLUG_INVALID_FORMAT
    """
    if not v:
        raise ValueError('SLUG_REQUIRED')

    if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', v):
        raise ValueError('SLUG_INVALID_FORMAT')

    return v


def validate_hex_color(v: str) -> str:
    """
    Validate hexadecimal color format.

    Requirements:
    - Starts with # or valid hex without #
    - Contains exactly 6 hexadecimal digits

    Args:
        v: Color string to validate (e.g., '#FF5733' or 'FF5733')

    Returns:
        The normalized color string (with #)

    Raises:
        ValueError: If color format is invalid

    Example:
        >>> validate_hex_color("#FF5733")
        '#FF5733'

        >>> validate_hex_color("FF5733")
        '#FF5733'

        >>> validate_hex_color("GGGGGG")  # Invalid hex
        ValueError: COLOR_INVALID_HEX
    """
    # Remove # if present
    clean_color = v.lstrip('#')

    # Check format: exactly 6 hex digits
    if not re.match(r'^[0-9A-Fa-f]{6}$', clean_color):
        raise ValueError('COLOR_INVALID_HEX')

    # Return normalized format with #
    return f'#{clean_color.upper()}'


# ============================================================================
# COMPOSITE VALIDATOR CLASSES (Used as field_validator decorators)
# ============================================================================

class PasswordValidators:
    """
    Composite validators for password fields.

    Used as @field_validator decorator methods in Pydantic models.
    """

    @staticmethod
    def validate_strength(v: str) -> str:
        """Validate password strength strength."""
        return validate_password_strength(v)

    @staticmethod
    def validate_match(v: str, info: ValidationInfo) -> str:
        """Validate password confirmation matches."""
        if 'new_password' in info.data:
            if v != info.data['new_password']:
                raise ValueError('PASSWORD_MISMATCH')
        elif 'password' in info.data:
            if v != info.data['password']:
                raise ValueError('PASSWORD_MISMATCH')
        return v


class TOTPValidators:
    """
    Composite validators for TOTP fields.

    Used as @field_validator decorator methods in Pydantic models.
    """

    @staticmethod
    def validate_format(v: str) -> str:
        """Validate TOTP code format."""
        return validate_totp_code(v)
