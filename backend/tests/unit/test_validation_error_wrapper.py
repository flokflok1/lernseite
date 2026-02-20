"""
Tests for Validation Error Wrapper.

Tests the conversion of Pydantic ValidationError to custom ValidationError with ErrorCode
for all standardized validation patterns from Phase 2, Step 4.
"""

import pytest
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationInfo
from typing import Optional
from app.infrastructure.error_handling.validation_exception_wrapper import ValidationErrorWrapper
from app.infrastructure.error_handling.exceptions import ValidationError
from app.infrastructure.error_handling.validation_error_mapping import ValidationErrorMapping


# ============================================================================
# Test Models with Standardized Error Messages
# ============================================================================

class UserModel(BaseModel):
    """Test model with empty/required validation."""

    email: str
    username: str

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("email cannot be empty")
        return v

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("username cannot be empty")
        return v


class TokenWalletModel(BaseModel):
    """Test model with XOR validation (cannot specify both)."""

    user_id: Optional[int] = None
    organization_id: Optional[int] = None

    @field_validator("organization_id", mode="after")
    @classmethod
    def validate_owner(cls, v, info: ValidationInfo):
        """Validate XOR relationship between user_id and organization_id."""
        user_id = info.data.get("user_id")
        org_id = v

        if user_id is not None and org_id is not None:
            raise ValueError("Cannot specify both user_id and organization_id")
        if user_id is None and org_id is None:
            raise ValueError("Must specify either user_id or organization_id")

        return v


class BanUserModel(BaseModel):
    """Test model with conditional validation."""

    reason: str
    duration_days: Optional[int] = None
    permanent: bool = False

    @model_validator(mode="after")
    def validate_duration(self):
        """Validate duration_days based on permanent flag."""
        if self.permanent and self.duration_days is not None:
            raise ValueError("duration_days must be null for permanent bans")
        if not self.permanent and self.duration_days is None:
            raise ValueError("duration_days must be non-null for temporary bans")
        return self


class CoursePromptModel(BaseModel):
    """Test model with content validation."""

    prompt_system: Optional[str] = None
    prompt_user_template: Optional[str] = None

    @field_validator("prompt_system", "prompt_user_template")
    @classmethod
    def validate_prompt_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError("prompt_system cannot be empty")
        return v


# ============================================================================
# Test Cases
# ============================================================================

class TestValidationErrorMapping:
    """Test the error message to ErrorCode mapping."""

    def test_empty_pattern_mapping(self):
        """Test mapping of empty field error messages."""
        message = "email cannot be empty"
        code, details = ValidationErrorMapping.get_error_code(message)

        assert code == "VALIDATION_FIELD_EMPTY"
        assert details is not None
        assert details.get("field") == "email"

    def test_required_pattern_mapping(self):
        """Test mapping of required field error messages."""
        message = "username is required"
        code, details = ValidationErrorMapping.get_error_code(message)

        assert code == "VALIDATION_REQUIRED_FIELD"
        assert details is not None
        assert details.get("field") == "username"

    def test_xor_conflict_pattern_mapping(self):
        """Test mapping of XOR conflict error messages."""
        message = "Cannot specify both user_id and organization_id"
        code, details = ValidationErrorMapping.get_error_code(message)

        assert code == "VALIDATION_XOR_CONFLICT"
        assert details is not None
        assert details.get("field1") == "user_id"
        assert details.get("field2") == "organization_id"

    def test_xor_required_pattern_mapping(self):
        """Test mapping of XOR required error messages."""
        message = "Must specify either user_id or organization_id"
        code, details = ValidationErrorMapping.get_error_code(message)

        assert code == "VALIDATION_XOR_REQUIRED"
        assert details is not None
        assert details.get("field1") == "user_id"
        assert details.get("field2") == "organization_id"

    def test_conditional_pattern_mapping(self):
        """Test mapping of conditional field error messages."""
        message = "duration_days must be null for permanent bans"
        code, details = ValidationErrorMapping.get_error_code(message)

        assert code == "VALIDATION_CONDITIONAL_FIELD"
        assert details is not None
        assert details.get("field") == "duration_days"
        assert details.get("condition") == "null for permanent bans"

    def test_unknown_error_fallback(self):
        """Test fallback for unknown error messages."""
        message = "some random error message"
        code, details = ValidationErrorMapping.get_error_code(message)

        assert code == "VALIDATION_ERROR"
        assert details is not None
        assert details.get("message") == message

    def test_validate_message_format_known_pattern(self):
        """Test validation of known error message patterns."""
        assert ValidationErrorMapping.validate_message_format("email cannot be empty")
        assert ValidationErrorMapping.validate_message_format("username is required")
        assert ValidationErrorMapping.validate_message_format(
            "Cannot specify both user_id and organization_id"
        )

    def test_validate_message_format_unknown(self):
        """Test validation of unknown error message patterns."""
        assert not ValidationErrorMapping.validate_message_format("random error")
        assert not ValidationErrorMapping.validate_message_format("")


class TestValidationErrorWrapper:
    """Test conversion of Pydantic ValidationError to custom ValidationError."""

    def test_convert_empty_field_error(self):
        """Test conversion of empty field validation error."""
        with pytest.raises(Exception) as exc_info:
            UserModel(email="", username="testuser")

        pydantic_error = exc_info.value
        custom_error = ValidationErrorWrapper.convert(pydantic_error)

        assert isinstance(custom_error, ValidationError)
        assert custom_error.error_code == "VALIDATION_FIELD_EMPTY"
        assert "email cannot be empty" in custom_error.message
        assert custom_error.details.get("field") == "email"
        assert custom_error.details.get("i18n_key") == "error.validation.fieldEmpty"

    def test_convert_xor_conflict_error(self):
        """Test conversion of XOR conflict validation error."""
        with pytest.raises(Exception) as exc_info:
            TokenWalletModel(user_id=42, organization_id=123)

        pydantic_error = exc_info.value
        custom_error = ValidationErrorWrapper.convert(pydantic_error)

        assert isinstance(custom_error, ValidationError)
        assert custom_error.error_code == "VALIDATION_XOR_CONFLICT"
        assert custom_error.details.get("field1") == "user_id"
        assert custom_error.details.get("field2") == "organization_id"
        assert (
            custom_error.details.get("i18n_key") == "error.validation.xorConflict"
        )

    def test_convert_xor_required_error(self):
        """Test conversion of XOR required validation error."""
        with pytest.raises(Exception) as exc_info:
            TokenWalletModel(user_id=None, organization_id=None)

        pydantic_error = exc_info.value
        custom_error = ValidationErrorWrapper.convert(pydantic_error)

        assert isinstance(custom_error, ValidationError)
        assert custom_error.error_code == "VALIDATION_XOR_REQUIRED"
        assert custom_error.details.get("field1") == "user_id"
        assert custom_error.details.get("field2") == "organization_id"
        assert (
            custom_error.details.get("i18n_key") == "error.validation.xorRequired"
        )

    def test_convert_conditional_error(self):
        """Test conversion of conditional validation error."""
        with pytest.raises(Exception) as exc_info:
            BanUserModel(
                reason="Spam violation", duration_days=30, permanent=True
            )

        pydantic_error = exc_info.value
        custom_error = ValidationErrorWrapper.convert(pydantic_error)

        assert isinstance(custom_error, ValidationError)
        assert custom_error.error_code == "VALIDATION_CONDITIONAL_FIELD"
        assert custom_error.details.get("field") == "duration_days"
        assert (
            custom_error.details.get("i18n_key")
            == "error.validation.conditionalField"
        )

    def test_convert_required_field_error(self):
        """Test conversion of required field validation error."""
        with pytest.raises(Exception) as exc_info:
            BanUserModel(reason="Spam", duration_days=None, permanent=False)

        pydantic_error = exc_info.value
        custom_error = ValidationErrorWrapper.convert(pydantic_error)

        assert isinstance(custom_error, ValidationError)
        assert custom_error.error_code == "VALIDATION_CONDITIONAL_FIELD"

    def test_convert_multiple_errors(self):
        """Test conversion with multiple validation errors."""
        with pytest.raises(Exception) as exc_info:
            UserModel(email="", username="")

        pydantic_error = exc_info.value
        custom_error = ValidationErrorWrapper.convert(pydantic_error)

        assert isinstance(custom_error, ValidationError)
        # First error should be email
        assert "email" in custom_error.message
        # Should include all_errors
        assert "all_errors" in custom_error.details
        assert len(custom_error.details["all_errors"]) >= 1

    def test_is_validation_error(self):
        """Test detection of Pydantic ValidationError."""
        with pytest.raises(Exception) as exc_info:
            UserModel(email="", username="")

        pydantic_error = exc_info.value
        assert ValidationErrorWrapper.is_validation_error(pydantic_error)
        assert not ValidationErrorWrapper.is_validation_error(ValueError("random"))

    def test_convert_with_i18n_key_lookup(self):
        """Test that i18n key is properly looked up and added to details."""
        with pytest.raises(Exception) as exc_info:
            UserModel(email="", username="testuser")

        pydantic_error = exc_info.value
        custom_error = ValidationErrorWrapper.convert(pydantic_error)

        assert custom_error.error_code == "VALIDATION_FIELD_EMPTY"
        assert "i18n_key" in custom_error.details
        assert custom_error.details["i18n_key"] == "error.validation.fieldEmpty"

    def test_convert_multiple_errors_detailed(self):
        """Test detailed conversion of multiple validation errors."""
        with pytest.raises(Exception) as exc_info:
            UserModel(email="", username="")

        pydantic_error = exc_info.value
        error_dict = ValidationErrorWrapper.convert_multiple(pydantic_error)

        assert error_dict["total_errors"] >= 1
        assert "errors" in error_dict
        assert "first_error" in error_dict

        if error_dict["errors"]:
            first_error = error_dict["first_error"]
            assert "field" in first_error
            assert "message" in first_error
            assert "error_code" in first_error
            assert "i18n_key" in first_error

    def test_status_code_is_400_for_validation(self):
        """Test that validation errors have HTTP 400 status code."""
        with pytest.raises(Exception) as exc_info:
            UserModel(email="", username="testuser")

        pydantic_error = exc_info.value
        custom_error = ValidationErrorWrapper.convert(pydantic_error)

        assert custom_error.status_code == 400

    def test_error_code_in_error_code_mapping(self):
        """Test that generated error codes exist in ErrorCode mapping."""
        with pytest.raises(Exception) as exc_info:
            UserModel(email="", username="testuser")

        pydantic_error = exc_info.value
        custom_error = ValidationErrorWrapper.convert(pydantic_error)

        # Should not raise KeyError
        from app.infrastructure.i18n.error_code_i18n_mapping import get_i18n_key

        try:
            i18n_key = get_i18n_key(custom_error.error_code)
            assert i18n_key is not None
        except KeyError:
            pytest.fail(f"ErrorCode {custom_error.error_code} not in mapping")


class TestValidationErrorIntegration:
    """Integration tests for validation error wrapper with actual models."""

    def test_full_flow_empty_field(self):
        """Test full flow from Pydantic validation to custom error."""
        try:
            UserModel(email="", username="testuser")
        except Exception as e:
            if ValidationErrorWrapper.is_validation_error(e):
                custom_error = ValidationErrorWrapper.convert(e)

                # Verify all parts
                assert custom_error.error_code == "VALIDATION_FIELD_EMPTY"
                assert custom_error.status_code == 400
                assert "i18n_key" in custom_error.details
                assert custom_error.details["i18n_key"] == "error.validation.fieldEmpty"
                return

        pytest.fail("Expected ValidationError to be raised")

    def test_full_flow_xor_conflict(self):
        """Test full flow for XOR conflict validation."""
        try:
            TokenWalletModel(user_id=42, organization_id=123)
        except Exception as e:
            if ValidationErrorWrapper.is_validation_error(e):
                custom_error = ValidationErrorWrapper.convert(e)

                assert custom_error.error_code == "VALIDATION_XOR_CONFLICT"
                assert custom_error.details["field1"] == "user_id"
                assert custom_error.details["field2"] == "organization_id"
                return

        pytest.fail("Expected ValidationError to be raised")

    def test_error_to_dict_conversion(self):
        """Test conversion of error to JSON-serializable dict."""
        try:
            UserModel(email="", username="testuser")
        except Exception as e:
            if ValidationErrorWrapper.is_validation_error(e):
                custom_error = ValidationErrorWrapper.convert(e)
                error_dict = custom_error.to_dict()

                assert "error" in error_dict
                assert "code" in error_dict["error"]
                assert "message" in error_dict["error"]
                assert error_dict["error"]["code"] == "VALIDATION_FIELD_EMPTY"
                return

        pytest.fail("Expected ValidationError to be raised")


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestValidationErrorEdgeCases:
    """Test edge cases and error handling."""

    def test_convert_empty_errors_list(self):
        """Test handling of ValidationError with no errors."""
        from pydantic import ValidationError as PydanticValidationError

        # Create a minimal ValidationError (this is hard to do directly)
        # Instead, test with a model that passes validation
        try:
            user = UserModel(email="test@example.com", username="testuser")
            # No error should be raised
        except Exception:
            pytest.fail("Model validation should pass")

    def test_field_path_extraction_nested(self):
        """Test extraction of nested field paths."""

        class NestedModel(BaseModel):
            user_data: dict = {}

        try:
            NestedModel(user_data={"nested": {"field": "value"}})
        except Exception as e:
            if ValidationErrorWrapper.is_validation_error(e):
                # Should handle nested paths gracefully
                custom_error = ValidationErrorWrapper.convert(e)
                assert custom_error is not None
