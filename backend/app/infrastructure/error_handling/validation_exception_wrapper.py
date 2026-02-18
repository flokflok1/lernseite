"""
Validation Exception Wrapper.

Converts Pydantic ValidationError exceptions to custom ValidationError exceptions
with ErrorCode values for i18n support.

This wrapper bridges the gap between:
1. Pydantic v2 ValidationError (validation framework errors)
2. Custom ValidationError (APIException with ErrorCode for i18n)
3. TranslationManager (i18n translation lookup)

Flow:
    Pydantic ValidationError (field="email", msg="value_error.email.invalid")
    → ValidationErrorWrapper.convert()
    → Custom ValidationError with ErrorCode="VALIDATION_INVALID_FORMAT", details={'field': 'email'}
    → Frontend uses ErrorCode to lookup i18n key and display translated message
"""

from typing import Optional, Dict, Any
from pydantic import ValidationError as PydanticValidationError
from app.infrastructure.error_handling.exceptions import ValidationError
from app.infrastructure.error_handling.validation_error_mapping import ValidationErrorMapping
from app.infrastructure.i18n.error_code_i18n_mapping import get_i18n_key


class ValidationErrorWrapper:
    """
    Wrapper to convert Pydantic ValidationError to custom ValidationError.

    Handles:
    1. Extraction of validation error messages from Pydantic ValidationError
    2. Mapping of standardized error messages to ErrorCode values
    3. Creation of custom ValidationError with ErrorCode
    4. Support for i18n translation lookup

    Examples:
        >>> try:
        ...     UserCreateSchema(email="invalid", username="ab")
        ... except PydanticValidationError as e:
        ...     custom_error = ValidationErrorWrapper.convert(e)
        ...     raise custom_error

        >>> # Result:
        >>> # ValidationError(
        >>> #     message="email cannot be empty",
        >>> #     error_code="VALIDATION_FIELD_EMPTY",
        >>> #     status_code=400,
        >>> #     details={'field': 'email', 'i18n_key': 'error.validation.fieldEmpty'}
        >>> # )
    """

    @staticmethod
    def convert(
        pydantic_error: PydanticValidationError,
        language_code: str = "en"
    ) -> ValidationError:
        """
        Convert Pydantic ValidationError to custom ValidationError with ErrorCode.

        Args:
            pydantic_error: Pydantic v2 ValidationError
            language_code: Language code for i18n lookup (default: 'en')

        Returns:
            Custom ValidationError with ErrorCode and i18n details

        Raises:
            ValueError: If validation error cannot be converted
        """
        errors = pydantic_error.errors()

        if not errors:
            # Fallback for empty error list
            return ValidationError(
                message="Validation failed",
                error_code="VALIDATION_ERROR"
            )

        # Use first error for initial message
        first_error = errors[0]
        field_path = _get_field_path(first_error)
        error_message = _get_error_message(first_error)

        # Map to ErrorCode
        error_code, details = ValidationErrorMapping.get_error_code(error_message)

        # Add i18n key to details
        try:
            i18n_key = get_i18n_key(error_code)
            if details is None:
                details = {}
            details["i18n_key"] = i18n_key
            details["field_path"] = field_path  # Full path for complex nested errors
        except KeyError:
            # ErrorCode not in mapping, just use the message
            pass

        # Create custom ValidationError
        custom_error = ValidationError(
            message=error_message,
            error_code=error_code,
            status_code=400
        )

        # Add details for frontend
        custom_error.details = details or {}

        # Include all errors if multiple validation errors
        if len(errors) > 1:
            custom_error.details["all_errors"] = [
                {
                    "field": _get_field_path(err),
                    "message": _get_error_message(err),
                    "type": err.get("type", "unknown")
                }
                for err in errors
            ]

        return custom_error

    @staticmethod
    def convert_multiple(
        pydantic_error: PydanticValidationError,
        language_code: str = "en"
    ) -> Dict[str, Any]:
        """
        Convert all Pydantic validation errors to a structured format.

        Useful for endpoints that need to return multiple validation errors at once.

        Args:
            pydantic_error: Pydantic v2 ValidationError
            language_code: Language code for i18n lookup

        Returns:
            Dictionary with:
            - total_errors: Number of validation errors
            - errors: List of error details
            - first_error: First error details (for fallback)

        Example:
            >>> error_dict = ValidationErrorWrapper.convert_multiple(pydantic_error)
            >>> # {
            >>> #     'total_errors': 2,
            >>> #     'errors': [
            >>> #         {'field': 'email', 'message': '...', 'code': 'VALIDATION_...'},
            >>> #         {'field': 'username', 'message': '...', 'code': 'VALIDATION_...'}
            >>> #     ],
            >>> #     'first_error': {...}
            >>> # }
        """
        errors = pydantic_error.errors()

        converted_errors = []
        for error in errors:
            field_path = _get_field_path(error)
            error_message = _get_error_message(error)
            error_code, details = ValidationErrorMapping.get_error_code(error_message)

            try:
                i18n_key = get_i18n_key(error_code)
            except KeyError:
                i18n_key = None

            converted_errors.append({
                "field": field_path,
                "message": error_message,
                "error_code": error_code,
                "i18n_key": i18n_key,
                "type": error.get("type", "unknown"),
                "details": details or {}
            })

        return {
            "total_errors": len(errors),
            "errors": converted_errors,
            "first_error": converted_errors[0] if converted_errors else None
        }

    @staticmethod
    def is_validation_error(error: Exception) -> bool:
        """
        Check if an exception is a Pydantic ValidationError.

        Args:
            error: Exception to check

        Returns:
            True if error is a Pydantic ValidationError, False otherwise
        """
        return isinstance(error, PydanticValidationError)


def _get_field_path(error: Dict[str, Any]) -> str:
    """
    Extract field path from Pydantic error dict.

    Handles nested field errors (e.g., 'user.email').

    Args:
        error: Pydantic error dictionary

    Returns:
        Field path string (e.g., 'email', 'user.0.email')
    """
    loc = error.get("loc", ())
    if isinstance(loc, tuple):
        return ".".join(str(l) for l in loc)
    return str(loc)


def _get_error_message(error: Dict[str, Any]) -> str:
    """
    Extract human-readable error message from Pydantic error dict.

    Converts Pydantic error types to standardized messages when possible.

    Args:
        error: Pydantic error dictionary

    Returns:
        Human-readable error message
    """
    msg = error.get("msg", "")
    ctx = error.get("ctx", {})

    # For string_type, pattern_v1, etc. - extract from message
    if msg:
        # Strip "Value error, " prefix added by Pydantic v2
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
        return msg

    # Fallback: Build message from type and context
    error_type = error.get("type", "unknown")
    field = _get_field_path(error)

    if error_type == "value_error":
        return f"{field} is invalid"
    elif error_type == "type_error":
        expected_type = ctx.get("expected_type", "value")
        return f"{field} must be of type {expected_type}"
    else:
        return f"Validation error at {field}"
