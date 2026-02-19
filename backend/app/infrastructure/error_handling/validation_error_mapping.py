"""
Validation Error Message to ErrorCode Mapping.

Maps standardized validation error messages (from Step 4) to ErrorCode values
for i18n translation support.

This module handles the bridge between:
1. Standardized error messages in Pydantic validators
2. ErrorCode enum values (mapped to i18n keys in error_code_i18n_mapping.py)
3. Frontend localization via TranslationManager

Standardized Message Patterns (from Phase 2, Step 4):
- Empty/Content: "{field} cannot be empty"
- Required: "{field} is required"
- XOR Conflict: "Cannot specify both {field1} and {field2}"
- XOR Required: "Must specify either {field1} or {field2}"
- Conditional: "{field} must be {condition}" (e.g., "duration_days must be null")
- Type/Enum: Pydantic built-in validation errors
"""

from typing import Dict, Optional, Tuple
import re


class ValidationErrorMapping:
    """
    Maps standardized validation error messages to ErrorCode values.

    Provides pattern matching for validation error messages and returns
    the corresponding ErrorCode for i18n translation.
    """

    # Pattern definitions for standardized error messages
    PATTERNS = {
        # Empty/Content validation: "{field} cannot be empty"
        "FIELD_EMPTY": {
            "pattern": r"^(.+?)\s+cannot\s+be\s+empty$",
            "error_code": "VALIDATION_FIELD_EMPTY",
            "description": "Field value is empty or whitespace-only"
        },

        # Required field: "{field} is required"
        "FIELD_REQUIRED": {
            "pattern": r"^(.+?)\s+is\s+required$",
            "error_code": "VALIDATION_REQUIRED_FIELD",
            "description": "Required field is missing or null"
        },

        # XOR Conflict: "Cannot specify both {field1} and {field2}"
        "XOR_CONFLICT": {
            "pattern": r"^Cannot\s+specify\s+both\s+(.+?)\s+and\s+(.+?)$",
            "error_code": "VALIDATION_XOR_CONFLICT",
            "description": "Mutually exclusive fields both specified"
        },

        # XOR Required: "Must specify either {field1} or {field2}"
        "XOR_REQUIRED": {
            "pattern": r"^Must\s+specify\s+either\s+(.+?)\s+or\s+(.+?)$",
            "error_code": "VALIDATION_XOR_REQUIRED",
            "description": "Must provide one of the mutually exclusive fields"
        },

        # Conditional: "{field} must be {condition}"
        "FIELD_CONDITIONAL": {
            "pattern": r"^(.+?)\s+must\s+be\s+(.+?)$",
            "error_code": "VALIDATION_CONDITIONAL_FIELD",
            "description": "Field fails conditional validation rule"
        }
    }

    @staticmethod
    def get_error_code(error_message: str) -> Tuple[str, Optional[Dict[str, str]]]:
        """
        Get ErrorCode for a standardized validation error message.

        Args:
            error_message: The validation error message from Pydantic validator

        Returns:
            Tuple of (error_code: str, details: Optional[Dict])
            Details dict contains extracted field names for i18n interpolation

        Example:
            >>> msg = "email cannot be empty"
            >>> code, details = ValidationErrorMapping.get_error_code(msg)
            >>> code
            'VALIDATION_FIELD_EMPTY'
            >>> details
            {'field': 'email'}
        """
        for pattern_key, pattern_info in ValidationErrorMapping.PATTERNS.items():
            match = re.match(pattern_info["pattern"], error_message)

            if match:
                error_code = pattern_info["error_code"]
                details = ValidationErrorMapping._extract_details(
                    pattern_key, match.groups()
                )
                return error_code, details

        # Fallback to generic validation error
        return "VALIDATION_ERROR", {"message": error_message}

    @staticmethod
    def _extract_details(
        pattern_key: str, groups: Tuple[str, ...]
    ) -> Dict[str, str]:
        """
        Extract field names and conditions from regex match groups.

        Args:
            pattern_key: The pattern type (e.g., "FIELD_EMPTY")
            groups: Regex match groups from pattern

        Returns:
            Dictionary with extracted details for i18n interpolation
        """
        if pattern_key == "FIELD_EMPTY":
            # Groups: (field_name,)
            return {"field": groups[0]}

        elif pattern_key == "FIELD_REQUIRED":
            # Groups: (field_name,)
            return {"field": groups[0]}

        elif pattern_key == "XOR_CONFLICT":
            # Groups: (field1, field2)
            return {"field1": groups[0], "field2": groups[1]}

        elif pattern_key == "XOR_REQUIRED":
            # Groups: (field1, field2)
            return {"field1": groups[0], "field2": groups[1]}

        elif pattern_key == "FIELD_CONDITIONAL":
            # Groups: (field_name, condition)
            return {"field": groups[0], "condition": groups[1]}

        return {}

    @staticmethod
    def validate_message_format(error_message: str) -> bool:
        """
        Check if an error message matches one of the standardized patterns.

        Args:
            error_message: The error message to validate

        Returns:
            True if message matches a standardized pattern, False otherwise

        Example:
            >>> ValidationErrorMapping.validate_message_format("email cannot be empty")
            True
            >>> ValidationErrorMapping.validate_message_format("some random error")
            False
        """
        for pattern_info in ValidationErrorMapping.PATTERNS.values():
            if re.match(pattern_info["pattern"], error_message):
                return True
        return False

    @staticmethod
    def list_patterns() -> Dict[str, Dict]:
        """
        List all standardized error message patterns.

        Returns:
            Dictionary of pattern definitions for documentation
        """
        return {
            key: {
                "pattern": info["pattern"],
                "error_code": info["error_code"],
                "description": info["description"]
            }
            for key, info in ValidationErrorMapping.PATTERNS.items()
        }
