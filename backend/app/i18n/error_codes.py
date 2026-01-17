"""
Error Codes Catalog
Frontend uses these codes for i18n translation

Pattern: DOMAIN_ACTION_REASON
Example: AUTH_LOGIN_INVALID_CREDENTIALS

Domains:
- AUTH: Authentication & Authorization
- USER: User management
- COURSE: Course operations
- CHAPTER: Chapter operations
- LESSON: Lesson operations
- LM: Learning Methods
- AI: AI/KI operations
- EXAM: Exam operations
- ORG: Organization operations
- FILE: File operations
- SYSTEM: System operations
- VALIDATION: Input validation
"""
from enum import Enum
from typing import Any, Dict, Optional, Tuple
from flask import jsonify


class ErrorCode(str, Enum):
    """Error codes for API responses - Frontend translates these"""

    # ========================================================================
    # GENERIC ERRORS
    # ========================================================================
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"

    # ========================================================================
    # AUTH ERRORS
    # ========================================================================
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_TOKEN_MISSING = "AUTH_TOKEN_MISSING"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_INSUFFICIENT_PERMISSIONS"
    AUTH_ACCOUNT_DISABLED = "AUTH_ACCOUNT_DISABLED"
    AUTH_EMAIL_NOT_VERIFIED = "AUTH_EMAIL_NOT_VERIFIED"
    AUTH_SESSION_EXPIRED = "AUTH_SESSION_EXPIRED"

    # ========================================================================
    # USER ERRORS
    # ========================================================================
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_EMAIL_EXISTS = "USER_EMAIL_EXISTS"
    USER_USERNAME_EXISTS = "USER_USERNAME_EXISTS"
    USER_CREATE_FAILED = "USER_CREATE_FAILED"
    USER_UPDATE_FAILED = "USER_UPDATE_FAILED"
    USER_DELETE_FAILED = "USER_DELETE_FAILED"

    # ========================================================================
    # COURSE ERRORS
    # ========================================================================
    COURSE_NOT_FOUND = "COURSE_NOT_FOUND"
    COURSE_CREATE_FAILED = "COURSE_CREATE_FAILED"
    COURSE_UPDATE_FAILED = "COURSE_UPDATE_FAILED"
    COURSE_DELETE_FAILED = "COURSE_DELETE_FAILED"
    COURSE_ACCESS_DENIED = "COURSE_ACCESS_DENIED"
    COURSE_ALREADY_ENROLLED = "COURSE_ALREADY_ENROLLED"
    COURSE_NOT_ENROLLED = "COURSE_NOT_ENROLLED"
    COURSE_TITLE_REQUIRED = "COURSE_TITLE_REQUIRED"

    # ========================================================================
    # CHAPTER ERRORS
    # ========================================================================
    CHAPTER_NOT_FOUND = "CHAPTER_NOT_FOUND"
    CHAPTER_CREATE_FAILED = "CHAPTER_CREATE_FAILED"
    CHAPTER_UPDATE_FAILED = "CHAPTER_UPDATE_FAILED"
    CHAPTER_DELETE_FAILED = "CHAPTER_DELETE_FAILED"
    CHAPTER_TITLE_REQUIRED = "CHAPTER_TITLE_REQUIRED"

    # ========================================================================
    # LESSON ERRORS
    # ========================================================================
    LESSON_NOT_FOUND = "LESSON_NOT_FOUND"
    LESSON_CREATE_FAILED = "LESSON_CREATE_FAILED"
    LESSON_UPDATE_FAILED = "LESSON_UPDATE_FAILED"
    LESSON_DELETE_FAILED = "LESSON_DELETE_FAILED"

    # ========================================================================
    # LEARNING METHOD ERRORS
    # ========================================================================
    LM_NOT_FOUND = "LM_NOT_FOUND"
    LM_CREATE_FAILED = "LM_CREATE_FAILED"
    LM_UPDATE_FAILED = "LM_UPDATE_FAILED"
    LM_DELETE_FAILED = "LM_DELETE_FAILED"
    LM_INVALID_TYPE = "LM_INVALID_TYPE"
    LM_GENERATION_FAILED = "LM_GENERATION_FAILED"

    # ========================================================================
    # AI/KI ERRORS
    # ========================================================================
    AI_GENERATION_FAILED = "AI_GENERATION_FAILED"
    AI_PROVIDER_ERROR = "AI_PROVIDER_ERROR"
    AI_QUOTA_EXCEEDED = "AI_QUOTA_EXCEEDED"
    AI_MODEL_NOT_FOUND = "AI_MODEL_NOT_FOUND"
    AI_JOB_NOT_FOUND = "AI_JOB_NOT_FOUND"
    AI_JOB_FAILED = "AI_JOB_FAILED"
    AI_SESSION_NOT_FOUND = "AI_SESSION_NOT_FOUND"
    AI_SESSION_CREATE_FAILED = "AI_SESSION_CREATE_FAILED"

    # ========================================================================
    # THEORY ERRORS
    # ========================================================================
    THEORY_NOT_FOUND = "THEORY_NOT_FOUND"
    THEORY_ALREADY_EXISTS = "THEORY_ALREADY_EXISTS"
    THEORY_GENERATION_FAILED = "THEORY_GENERATION_FAILED"
    THEORY_UPDATE_FAILED = "THEORY_UPDATE_FAILED"
    THEORY_DELETE_FAILED = "THEORY_DELETE_FAILED"
    THEORY_TITLE_REQUIRED = "THEORY_TITLE_REQUIRED"
    THEORY_NO_AUDIO = "THEORY_NO_AUDIO"

    # ========================================================================
    # EXAM ERRORS
    # ========================================================================
    EXAM_NOT_FOUND = "EXAM_NOT_FOUND"
    EXAM_CREATE_FAILED = "EXAM_CREATE_FAILED"
    EXAM_GENERATION_FAILED = "EXAM_GENERATION_FAILED"
    EXAM_SUBMIT_FAILED = "EXAM_SUBMIT_FAILED"
    EXAM_ALREADY_SUBMITTED = "EXAM_ALREADY_SUBMITTED"

    # ========================================================================
    # FILE/UPLOAD ERRORS
    # ========================================================================
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_INVALID_FORMAT = "FILE_INVALID_FORMAT"
    FILE_NO_FILE_PROVIDED = "FILE_NO_FILE_PROVIDED"
    FILE_INVALID_BASE64 = "FILE_INVALID_BASE64"

    # ========================================================================
    # AUDIO ERRORS
    # ========================================================================
    AUDIO_NOT_FOUND = "AUDIO_NOT_FOUND"
    AUDIO_UPLOAD_FAILED = "AUDIO_UPLOAD_FAILED"
    AUDIO_NO_FILE_PROVIDED = "AUDIO_NO_FILE_PROVIDED"
    AUDIO_INVALID_FORMAT = "AUDIO_INVALID_FORMAT"
    AUDIO_TOO_LARGE = "AUDIO_TOO_LARGE"
    AUDIO_TRANSCRIPTION_FAILED = "AUDIO_TRANSCRIPTION_FAILED"

    # ========================================================================
    # ORGANIZATION ERRORS
    # ========================================================================
    ORG_NOT_FOUND = "ORG_NOT_FOUND"
    ORG_CREATE_FAILED = "ORG_CREATE_FAILED"
    ORG_UPDATE_FAILED = "ORG_UPDATE_FAILED"
    ORG_MEMBER_NOT_FOUND = "ORG_MEMBER_NOT_FOUND"
    ORG_QUOTA_EXCEEDED = "ORG_QUOTA_EXCEEDED"

    # ========================================================================
    # CATEGORY ERRORS
    # ========================================================================
    CATEGORY_NOT_FOUND = "CATEGORY_NOT_FOUND"
    CATEGORY_CREATE_FAILED = "CATEGORY_CREATE_FAILED"
    CATEGORY_DELETE_FAILED = "CATEGORY_DELETE_FAILED"
    CATEGORY_HAS_COURSES = "CATEGORY_HAS_COURSES"

    # ========================================================================
    # VALIDATION ERRORS
    # ========================================================================
    VALIDATION_REQUIRED_FIELD = "VALIDATION_REQUIRED_FIELD"
    VALIDATION_INVALID_FORMAT = "VALIDATION_INVALID_FORMAT"
    VALIDATION_INVALID_VALUE = "VALIDATION_INVALID_VALUE"
    VALIDATION_REQUEST_BODY_REQUIRED = "VALIDATION_REQUEST_BODY_REQUIRED"

    # ========================================================================
    # MATH TOOLKIT ERRORS
    # ========================================================================
    MATH_PATTERN_NOT_FOUND = "MATH_PATTERN_NOT_FOUND"
    MATH_FORMULA_NOT_FOUND = "MATH_FORMULA_NOT_FOUND"
    MATH_SESSION_NOT_FOUND = "MATH_SESSION_NOT_FOUND"
    MATH_SESSION_CREATE_FAILED = "MATH_SESSION_CREATE_FAILED"
    MATH_EXPRESSION_REQUIRED = "MATH_EXPRESSION_REQUIRED"
    MATH_PATTERN_CREATE_FAILED = "MATH_PATTERN_CREATE_FAILED"
    MATH_FORMULA_CREATE_FAILED = "MATH_FORMULA_CREATE_FAILED"

    # ========================================================================
    # FEEDBACK ERRORS
    # ========================================================================
    FEEDBACK_CREATE_FAILED = "FEEDBACK_CREATE_FAILED"
    FEEDBACK_INVALID_TYPE = "FEEDBACK_INVALID_TYPE"


def error_response(
    code: ErrorCode,
    status: int = 400,
    details: Optional[Dict[str, Any]] = None,
    field: Optional[str] = None
) -> Tuple[Dict[str, Any], int]:
    """
    Create standardized error response with error code

    Args:
        code: ErrorCode enum value
        status: HTTP status code (default 400)
        details: Additional error details (optional)
        field: Field name for validation errors (optional)

    Returns:
        Tuple of (response dict, status code)

    Example:
        return error_response(ErrorCode.USER_NOT_FOUND, 404)
        return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, field='email')
    """
    response = {
        'success': False,
        'error': {
            'code': code.value,
        }
    }

    if field:
        response['error']['field'] = field

    if details:
        response['error']['details'] = details

    return jsonify(response), status


def success_response(
    data: Optional[Any] = None,
    message_code: Optional[str] = None,
    status: int = 200
) -> Tuple[Dict[str, Any], int]:
    """
    Create standardized success response

    Args:
        data: Response data (optional)
        message_code: Success message code for frontend translation (optional)
        status: HTTP status code (default 200)

    Returns:
        Tuple of (response dict, status code)

    Example:
        return success_response({'user': user_data})
        return success_response(message_code='USER_CREATED')
    """
    response = {'success': True}

    if data is not None:
        response['data'] = data

    if message_code:
        response['message_code'] = message_code

    return jsonify(response), status
