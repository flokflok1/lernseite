"""
Validation Utilities

Input validation functions for security and data integrity.
"""

import re
from typing import Optional
from email_validator import validate_email as _validate_email, EmailNotValidError


class ValidationError(Exception):
    """Validation error exception."""
    pass


class Validators:
    """
    Input validation utility functions.

    Prevents injection attacks and ensures data integrity.
    """

    # Regular expressions
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
    PASSWORD_REGEX = re.compile(r'^.{8,}$')  # Min 8 chars
    UUID_REGEX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    SLUG_REGEX = re.compile(r'^[a-z0-9-]+$')
    PHONE_REGEX = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format

    @staticmethod
    def validate_email(email: str, check_deliverability: bool = False) -> bool:
        """
        Validate email address.

        Args:
            email: Email address to validate
            check_deliverability: Check if domain accepts email

        Returns:
            True if valid

        Raises:
            ValidationError: If email is invalid
        """
        if not email:
            raise ValidationError("Email address is required")

        try:
            # Use email-validator library
            validated = _validate_email(email, check_deliverability=check_deliverability)
            return True
        except EmailNotValidError as e:
            raise ValidationError(f"Invalid email address: {str(e)}")

    @staticmethod
    def validate_password(password: str, min_length: int = 8) -> bool:
        """
        Validate password strength.

        Requirements:
        - Minimum length (default 8)
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Args:
            password: Password to validate
            min_length: Minimum password length

        Returns:
            True if valid

        Raises:
            ValidationError: If password is invalid
        """
        if not password:
            raise ValidationError("Password is required")

        if len(password) < min_length:
            raise ValidationError(f"Password must be at least {min_length} characters")

        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter")

        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter")

        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character")

        return True

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format.

        Requirements:
        - 3-30 characters
        - Alphanumeric, underscore, hyphen only
        - No spaces

        Args:
            username: Username to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If username is invalid
        """
        if not username:
            raise ValidationError("Username is required")

        if not Validators.USERNAME_REGEX.match(username):
            raise ValidationError(
                "Username must be 3-30 characters, alphanumeric, underscore or hyphen only"
            )

        return True

    @staticmethod
    def validate_uuid(uuid: str) -> bool:
        """
        Validate UUID format.

        Args:
            uuid: UUID string to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If UUID is invalid
        """
        if not uuid:
            raise ValidationError("UUID is required")

        if not Validators.UUID_REGEX.match(uuid.lower()):
            raise ValidationError("Invalid UUID format")

        return True

    @staticmethod
    def validate_slug(slug: str) -> bool:
        """
        Validate URL slug format.

        Requirements:
        - Lowercase letters, numbers, hyphens only
        - No spaces

        Args:
            slug: Slug to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If slug is invalid
        """
        if not slug:
            raise ValidationError("Slug is required")

        if not Validators.SLUG_REGEX.match(slug):
            raise ValidationError("Slug must contain only lowercase letters, numbers, and hyphens")

        return True

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number (E.164 format).

        Args:
            phone: Phone number to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If phone is invalid
        """
        if not phone:
            raise ValidationError("Phone number is required")

        if not Validators.PHONE_REGEX.match(phone):
            raise ValidationError("Invalid phone number format (use E.164 format)")

        return True

    @staticmethod
    def sanitize_sql(value: str) -> str:
        """
        Sanitize value for SQL (basic protection).

        Note: Always use parameterized queries instead!

        Args:
            value: Value to sanitize

        Returns:
            Sanitized value
        """
        if not value:
            return ''

        # Remove SQL injection patterns
        dangerous_patterns = [
            r'(\-\-|;|\bOR\b|\bAND\b|\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)',
        ]

        sanitized = value
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

        return sanitized

    @staticmethod
    def sanitize_html(value: str) -> str:
        """
        Basic HTML sanitization (remove script tags).

        Note: Use proper HTML sanitizer library for production!

        Args:
            value: HTML to sanitize

        Returns:
            Sanitized HTML
        """
        if not value:
            return ''

        # Remove script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)

        # Remove onclick, onerror, etc.
        sanitized = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)

        return sanitized

    @staticmethod
    def validate_json_keys(data: dict, required_keys: list) -> bool:
        """
        Validate that dict contains required keys.

        Args:
            data: Dictionary to validate
            required_keys: List of required keys

        Returns:
            True if all keys present

        Raises:
            ValidationError: If keys are missing
        """
        if not data:
            raise ValidationError("Data is required")

        missing_keys = [key for key in required_keys if key not in data]

        if missing_keys:
            raise ValidationError(f"Missing required keys: {', '.join(missing_keys)}")

        return True

    @staticmethod
    def validate_range(value: int, min_val: int, max_val: int) -> bool:
        """
        Validate integer is within range.

        Args:
            value: Value to validate
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)

        Returns:
            True if in range

        Raises:
            ValidationError: If out of range
        """
        if not isinstance(value, int):
            raise ValidationError("Value must be an integer")

        if value < min_val or value > max_val:
            raise ValidationError(f"Value must be between {min_val} and {max_val}")

        return True
