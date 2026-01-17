"""
Error Code to i18n Key Mapping

Maps backend ErrorCode enum values to frontend i18n translation keys
for consistent error message localization.

Pattern: error.{domain}.{action}.{reason}
Example: error.auth.login.invalidCredentials

This mapping ensures that:
1. Backend uses ErrorCode enums (type-safe)
2. Frontend uses i18n keys (translated)
3. All error messages are consistently localized
4. Developers know which i18n key to add for new errors

Usage:
    from app.i18n.error_code_i18n_mapping import ERROR_CODE_I18N_MAPPING

    error_code = ErrorCode.AUTH_INVALID_CREDENTIALS
    i18n_key = ERROR_CODE_I18N_MAPPING.get(error_code)  # 'error.auth.login.invalidCredentials'

Frontend Implementation:
    The frontend receives: {'error': {'code': 'AUTH_INVALID_CREDENTIALS'}}
    The frontend looks up: i18n_key = ERROR_CODE_I18N_MAPPING[code]
    The frontend displays: $t(i18n_key)
"""

from typing import Dict

# Maps ErrorCode string → i18n key path for frontend translation
ERROR_CODE_I18N_MAPPING: Dict[str, str] = {
    # =================================================================
    # GENERIC ERRORS (7 codes)
    # =================================================================
    "INTERNAL_ERROR": "error.generic.internalError",
    "NOT_FOUND": "error.generic.notFound",
    "BAD_REQUEST": "error.generic.badRequest",
    "UNAUTHORIZED": "error.auth.unauthorized",
    "FORBIDDEN": "error.generic.forbidden",
    "VALIDATION_ERROR": "error.validation.validationError",
    "BUSINESS_LOGIC_ERROR": "error.generic.businessLogicError",

    # =================================================================
    # AUTH ERRORS (9 codes)
    # =================================================================
    "AUTH_INVALID_CREDENTIALS": "error.auth.login.invalidCredentials",
    "AUTH_TOKEN_EXPIRED": "error.auth.token.expired",
    "AUTH_TOKEN_INVALID": "error.auth.token.invalid",
    "AUTH_TOKEN_MISSING": "error.auth.token.missing",
    "AUTH_INSUFFICIENT_PERMISSIONS": "error.auth.permissions.insufficient",
    "AUTH_ACCOUNT_DISABLED": "error.auth.account.disabled",
    "AUTH_EMAIL_NOT_VERIFIED": "error.auth.email.notVerified",
    "AUTH_SESSION_EXPIRED": "error.auth.session.expired",

    # =================================================================
    # USER ERRORS (6 codes)
    # =================================================================
    "USER_NOT_FOUND": "error.user.notFound",
    "USER_EMAIL_EXISTS": "error.user.email.alreadyExists",
    "USER_USERNAME_EXISTS": "error.user.username.alreadyExists",
    "USER_CREATE_FAILED": "error.user.create.failed",
    "USER_UPDATE_FAILED": "error.user.update.failed",
    "USER_DELETE_FAILED": "error.user.delete.failed",

    # =================================================================
    # COURSE ERRORS (9 codes)
    # =================================================================
    "COURSE_NOT_FOUND": "error.course.notFound",
    "COURSE_CREATE_FAILED": "error.course.create.failed",
    "COURSE_UPDATE_FAILED": "error.course.update.failed",
    "COURSE_DELETE_FAILED": "error.course.delete.failed",
    "COURSE_ACCESS_DENIED": "error.course.access.denied",
    "COURSE_ALREADY_ENROLLED": "error.course.enrollment.alreadyEnrolled",
    "COURSE_NOT_ENROLLED": "error.course.enrollment.notEnrolled",
    "COURSE_TITLE_REQUIRED": "error.course.validation.titleRequired",

    # =================================================================
    # CHAPTER ERRORS (5 codes)
    # =================================================================
    "CHAPTER_NOT_FOUND": "error.chapter.notFound",
    "CHAPTER_CREATE_FAILED": "error.chapter.create.failed",
    "CHAPTER_UPDATE_FAILED": "error.chapter.update.failed",
    "CHAPTER_DELETE_FAILED": "error.chapter.delete.failed",
    "CHAPTER_TITLE_REQUIRED": "error.chapter.validation.titleRequired",

    # =================================================================
    # LESSON ERRORS (4 codes)
    # =================================================================
    "LESSON_NOT_FOUND": "error.lesson.notFound",
    "LESSON_CREATE_FAILED": "error.lesson.create.failed",
    "LESSON_UPDATE_FAILED": "error.lesson.update.failed",
    "LESSON_DELETE_FAILED": "error.lesson.delete.failed",

    # =================================================================
    # LEARNING METHOD ERRORS (6 codes)
    # =================================================================
    "LM_NOT_FOUND": "error.learningMethod.notFound",
    "LM_CREATE_FAILED": "error.learningMethod.create.failed",
    "LM_UPDATE_FAILED": "error.learningMethod.update.failed",
    "LM_DELETE_FAILED": "error.learningMethod.delete.failed",
    "LM_INVALID_TYPE": "error.learningMethod.validation.invalidType",
    "LM_GENERATION_FAILED": "error.learningMethod.generation.failed",

    # =================================================================
    # AI/KI ERRORS (8 codes)
    # =================================================================
    "AI_GENERATION_FAILED": "error.ai.generation.failed",
    "AI_PROVIDER_ERROR": "error.ai.provider.failed",
    "AI_QUOTA_EXCEEDED": "error.ai.quota.exceeded",
    "AI_MODEL_NOT_FOUND": "error.ai.model.notFound",
    "AI_JOB_NOT_FOUND": "error.ai.job.notFound",
    "AI_JOB_FAILED": "error.ai.job.failed",
    "AI_SESSION_NOT_FOUND": "error.ai.session.notFound",
    "AI_SESSION_CREATE_FAILED": "error.ai.session.create.failed",

    # =================================================================
    # THEORY ERRORS (7 codes)
    # =================================================================
    "THEORY_NOT_FOUND": "error.theory.notFound",
    "THEORY_ALREADY_EXISTS": "error.theory.alreadyExists",
    "THEORY_GENERATION_FAILED": "error.theory.generation.failed",
    "THEORY_UPDATE_FAILED": "error.theory.update.failed",
    "THEORY_DELETE_FAILED": "error.theory.delete.failed",
    "THEORY_TITLE_REQUIRED": "error.theory.validation.titleRequired",
    "THEORY_NO_AUDIO": "error.theory.audio.notAvailable",

    # =================================================================
    # EXAM ERRORS (5 codes)
    # =================================================================
    "EXAM_NOT_FOUND": "error.exam.notFound",
    "EXAM_CREATE_FAILED": "error.exam.create.failed",
    "EXAM_GENERATION_FAILED": "error.exam.generation.failed",
    "EXAM_SUBMIT_FAILED": "error.exam.submit.failed",
    "EXAM_ALREADY_SUBMITTED": "error.exam.submission.alreadySubmitted",

    # =================================================================
    # FILE/UPLOAD ERRORS (5 codes)
    # =================================================================
    "FILE_NOT_FOUND": "error.file.notFound",
    "FILE_UPLOAD_FAILED": "error.file.upload.failed",
    "FILE_TOO_LARGE": "error.file.validation.tooLarge",
    "FILE_INVALID_FORMAT": "error.file.validation.invalidFormat",
    "FILE_NO_FILE_PROVIDED": "error.file.validation.noFileProvided",

    # =================================================================
    # AUDIO ERRORS (6 codes)
    # =================================================================
    "AUDIO_NOT_FOUND": "error.audio.notFound",
    "AUDIO_UPLOAD_FAILED": "error.audio.upload.failed",
    "AUDIO_NO_FILE_PROVIDED": "error.audio.validation.noFileProvided",
    "AUDIO_INVALID_FORMAT": "error.audio.validation.invalidFormat",
    "AUDIO_TOO_LARGE": "error.audio.validation.tooLarge",
    "AUDIO_TRANSCRIPTION_FAILED": "error.audio.transcription.failed",

    # =================================================================
    # ORGANIZATION ERRORS (5 codes)
    # =================================================================
    "ORG_NOT_FOUND": "error.organization.notFound",
    "ORG_CREATE_FAILED": "error.organization.create.failed",
    "ORG_UPDATE_FAILED": "error.organization.update.failed",
    "ORG_MEMBER_NOT_FOUND": "error.organization.member.notFound",
    "ORG_QUOTA_EXCEEDED": "error.organization.quota.exceeded",

    # =================================================================
    # CATEGORY ERRORS (4 codes)
    # =================================================================
    "CATEGORY_NOT_FOUND": "error.category.notFound",
    "CATEGORY_CREATE_FAILED": "error.category.create.failed",
    "CATEGORY_DELETE_FAILED": "error.category.delete.failed",
    "CATEGORY_HAS_COURSES": "error.category.constraint.hasCourses",

    # =================================================================
    # VALIDATION ERRORS (5 codes)
    # =================================================================
    "VALIDATION_REQUIRED_FIELD": "error.validation.requiredField",
    "VALIDATION_INVALID_FORMAT": "error.validation.invalidFormat",
    "VALIDATION_INVALID_VALUE": "error.validation.invalidValue",
    "VALIDATION_REQUEST_BODY_REQUIRED": "error.validation.requestBodyRequired",

    # =================================================================
    # MATH TOOLKIT ERRORS (7 codes)
    # =================================================================
    "MATH_PATTERN_NOT_FOUND": "error.math.pattern.notFound",
    "MATH_FORMULA_NOT_FOUND": "error.math.formula.notFound",
    "MATH_SESSION_NOT_FOUND": "error.math.session.notFound",
    "MATH_SESSION_CREATE_FAILED": "error.math.session.create.failed",
    "MATH_EXPRESSION_REQUIRED": "error.math.validation.expressionRequired",
    "MATH_PATTERN_CREATE_FAILED": "error.math.pattern.create.failed",
    "MATH_FORMULA_CREATE_FAILED": "error.math.formula.create.failed",

    # =================================================================
    # FEEDBACK ERRORS (2 codes)
    # =================================================================
    "FEEDBACK_CREATE_FAILED": "error.feedback.create.failed",
    "FEEDBACK_INVALID_TYPE": "error.feedback.validation.invalidType",

    # =================================================================
    # FILE VALIDATION ERRORS (additional)
    # =================================================================
    "FILE_INVALID_BASE64": "error.file.validation.invalidBase64",
}

# Reverse mapping for debugging: i18n_key → ErrorCode
I18N_TO_ERROR_CODE = {v: k for k, v in ERROR_CODE_I18N_MAPPING.items()}


def get_i18n_key(error_code: str) -> str:
    """
    Get i18n key for error code.

    Args:
        error_code: ErrorCode string value

    Returns:
        i18n key path (e.g., 'error.auth.login.invalidCredentials')

    Raises:
        KeyError: If error code not found in mapping

    Example:
        >>> get_i18n_key('AUTH_INVALID_CREDENTIALS')
        'error.auth.login.invalidCredentials'
    """
    if error_code not in ERROR_CODE_I18N_MAPPING:
        raise KeyError(f"No i18n mapping found for error code: {error_code}")

    return ERROR_CODE_I18N_MAPPING[error_code]


def get_error_code(i18n_key: str) -> str:
    """
    Get error code for i18n key (reverse lookup).

    Args:
        i18n_key: i18n key path

    Returns:
        ErrorCode string value

    Raises:
        KeyError: If i18n key not found in mapping

    Example:
        >>> get_error_code('error.auth.login.invalidCredentials')
        'AUTH_INVALID_CREDENTIALS'
    """
    if i18n_key not in I18N_TO_ERROR_CODE:
        raise KeyError(f"No error code found for i18n key: {i18n_key}")

    return I18N_TO_ERROR_CODE[i18n_key]
