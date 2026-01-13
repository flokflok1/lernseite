"""
Message Codes for Success Responses
Frontend uses these codes for i18n translation
"""
from enum import Enum


class MessageCode(str, Enum):
    """Success message codes for API responses - Frontend translates these"""

    # ========================================================================
    # GENERIC SUCCESS
    # ========================================================================
    SUCCESS = "SUCCESS"
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"

    # ========================================================================
    # AUTH SUCCESS
    # ========================================================================
    AUTH_LOGIN_SUCCESS = "AUTH_LOGIN_SUCCESS"
    AUTH_LOGOUT_SUCCESS = "AUTH_LOGOUT_SUCCESS"
    AUTH_PASSWORD_CHANGED = "AUTH_PASSWORD_CHANGED"
    AUTH_EMAIL_VERIFIED = "AUTH_EMAIL_VERIFIED"

    # ========================================================================
    # USER SUCCESS
    # ========================================================================
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_PROFILE_UPDATED = "USER_PROFILE_UPDATED"

    # ========================================================================
    # COURSE SUCCESS
    # ========================================================================
    COURSE_CREATED = "COURSE_CREATED"
    COURSE_UPDATED = "COURSE_UPDATED"
    COURSE_DELETED = "COURSE_DELETED"
    COURSE_ENROLLED = "COURSE_ENROLLED"
    COURSE_UNENROLLED = "COURSE_UNENROLLED"
    COURSE_PUBLISHED = "COURSE_PUBLISHED"

    # ========================================================================
    # CHAPTER SUCCESS
    # ========================================================================
    CHAPTER_CREATED = "CHAPTER_CREATED"
    CHAPTER_UPDATED = "CHAPTER_UPDATED"
    CHAPTER_DELETED = "CHAPTER_DELETED"

    # ========================================================================
    # LESSON SUCCESS
    # ========================================================================
    LESSON_CREATED = "LESSON_CREATED"
    LESSON_UPDATED = "LESSON_UPDATED"
    LESSON_DELETED = "LESSON_DELETED"
    LESSON_COMPLETED = "LESSON_COMPLETED"

    # ========================================================================
    # LEARNING METHOD SUCCESS
    # ========================================================================
    LM_CREATED = "LM_CREATED"
    LM_UPDATED = "LM_UPDATED"
    LM_DELETED = "LM_DELETED"
    LM_GENERATED = "LM_GENERATED"

    # ========================================================================
    # AI SUCCESS
    # ========================================================================
    AI_GENERATION_STARTED = "AI_GENERATION_STARTED"
    AI_GENERATION_COMPLETED = "AI_GENERATION_COMPLETED"
    AI_JOB_STARTED = "AI_JOB_STARTED"
    AI_JOB_COMPLETED = "AI_JOB_COMPLETED"
    AI_SESSION_CREATED = "AI_SESSION_CREATED"

    # ========================================================================
    # THEORY SUCCESS
    # ========================================================================
    THEORY_CREATED = "THEORY_CREATED"
    THEORY_UPDATED = "THEORY_UPDATED"
    THEORY_DELETED = "THEORY_DELETED"
    THEORY_GENERATED = "THEORY_GENERATED"

    # ========================================================================
    # EXAM SUCCESS
    # ========================================================================
    EXAM_CREATED = "EXAM_CREATED"
    EXAM_SUBMITTED = "EXAM_SUBMITTED"
    EXAM_GRADED = "EXAM_GRADED"

    # ========================================================================
    # FILE SUCCESS
    # ========================================================================
    FILE_UPLOADED = "FILE_UPLOADED"
    FILE_DELETED = "FILE_DELETED"

    # ========================================================================
    # CATEGORY SUCCESS
    # ========================================================================
    CATEGORY_CREATED = "CATEGORY_CREATED"
    CATEGORY_UPDATED = "CATEGORY_UPDATED"
    CATEGORY_DELETED = "CATEGORY_DELETED"

    # ========================================================================
    # FEEDBACK SUCCESS
    # ========================================================================
    FEEDBACK_SENT = "FEEDBACK_SENT"

    # ========================================================================
    # ORGANIZATION SUCCESS
    # ========================================================================
    ORG_CREATED = "ORG_CREATED"
    ORG_UPDATED = "ORG_UPDATED"
    ORG_MEMBER_ADDED = "ORG_MEMBER_ADDED"
    ORG_MEMBER_REMOVED = "ORG_MEMBER_REMOVED"
