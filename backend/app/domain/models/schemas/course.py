"""
LernsystemX Admin Course Models

Pydantic models for admin course management operations:
- Admin course list response
- Admin course detail response
- Admin course create request
- Admin course update request
- Admin course status update request

Phase B24-02 - ISO 9001:2015 compliant
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal


class AdminCourseListItem(BaseModel):
    """
    Admin course list item model

    Example:
        >>> course = AdminCourseListItem(
        ...     course_id=1,
        ...     title="Python Basics",
        ...     creator_id=5,
        ...     status="published",
        ...     enrollment_count=150
        ... )
    """
    course_id: int = Field(..., description="Course ID")
    title: str = Field(..., description="Course title")
    description: Optional[str] = Field(None, description="Course description")
    creator_id: int = Field(..., description="Creator user ID")
    creator_name: Optional[str] = Field(None, description="Creator full name")
    organisation_id: Optional[int] = Field(None, description="Organisation ID")
    organisation_name: Optional[str] = Field(None, description="Organisation name")
    category: Optional[str] = Field(None, description="Course category")
    level: Optional[str] = Field(None, description="Difficulty level")
    language: str = Field(default="de", description="Course language")
    price: Optional[Decimal] = Field(None, description="Course price")
    is_public: bool = Field(default=False, description="Is public course")
    status: str = Field(..., description="Course status (draft, published, archived)")
    module_count: int = Field(default=0, description="Number of modules")
    enrollment_count: int = Field(default=0, description="Number of enrollments")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")

    model_config = ConfigDict(from_attributes=True)


class AdminCourseDetail(BaseModel):
    """
    Admin detailed course model (C1.1 extended)

    Example:
        >>> course = AdminCourseDetail(
        ...     course_id=1,
        ...     title="Python Basics",
        ...     creator_id=5,
        ...     status="published",
        ...     created_at=datetime.now()
        ... )
    """
    course_id: int = Field(..., description="Course ID")
    title: str = Field(..., description="Course title")
    description: Optional[str] = Field(None, description="Short course description")
    long_description: Optional[str] = Field(None, description="Long course description")
    creator_id: int = Field(..., description="Creator user ID (creator_user_id)")
    creator_name: Optional[str] = Field(None, description="Creator full name")
    creator_email: Optional[str] = Field(None, description="Creator email")
    organisation_id: Optional[int] = Field(None, description="Organisation ID")
    organisation_name: Optional[str] = Field(None, description="Organisation name")
    category: Optional[str] = Field(None, description="Course category")
    level: Optional[str] = Field(None, description="Difficulty level")
    language: str = Field(default="de", description="Course language")
    price: Optional[Decimal] = Field(None, description="Course price")
    is_public: bool = Field(default=False, description="Is public course")
    is_published: bool = Field(default=False, description="Is published (raw DB field)")
    status: str = Field(..., description="Virtual status (draft, published, archived)")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL (cover)")
    preview_video_url: Optional[str] = Field(None, description="Preview video URL")
    tags: List[str] = Field(default=[], description="Course tags")
    module_count: int = Field(default=0, description="Number of modules")
    enrollment_count: int = Field(default=0, description="Number of enrollments")

    # C1.1 New fields
    ad_enabled: bool = Field(default=True, description="Shows ads (for free courses)")
    learning_goals: List[str] = Field(default=[], description="Learning objectives")
    target_audience: Optional[str] = Field(None, description="Target audience description")

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    archived_at: Optional[datetime] = Field(None, description="Archive timestamp")

    model_config = ConfigDict(from_attributes=True)


class AdminCourseCreateRequest(BaseModel):
    """
    Admin course creation request model

    Example:
        >>> request = AdminCourseCreateRequest(
        ...     title="Python Basics",
        ...     creator_id="e4ac9965-e3d2-42b9-9703-3f1c0f4adedc",
        ...     level="beginner",
        ...     language="de"
        ... )
    """
    title: str = Field(..., min_length=3, max_length=255, description="Course title")
    description: Optional[str] = Field(None, description="Course description")
    creator_id: str = Field(..., description="Creator user ID (UUID)")
    organisation_id: Optional[str] = Field(None, description="Organisation ID (UUID, for school/company courses)")
    category: Optional[str] = Field(None, description="Course category (string)")
    level: str = Field(default="beginner", description="Difficulty level")
    language: str = Field(default="de", max_length=2, description="Course language (ISO 639-1)")
    price: Optional[Decimal] = Field(default=0.00, ge=0, description="Course price")
    is_public: bool = Field(default=False, description="Is public course")
    thumbnail_url: Optional[str] = Field(None, max_length=1000, description="Thumbnail URL")
    preview_video_url: Optional[str] = Field(None, max_length=1000, description="Preview video URL")
    tags: List[str] = Field(default=[], description="Course tags")

    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code"""
        valid_languages = ['de', 'en', 'fr', 'es', 'it', 'nl', 'pl', 'pt', 'ru', 'tr', 'zh', 'ja', 'ko', 'ar', 'hi', 'sv', 'no', 'da', 'fi', 'el']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages[:5])}...')
        return v

    @field_validator('level')
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate difficulty level"""
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if v not in valid_levels:
            raise ValueError(f'Level must be one of: {", ".join(valid_levels)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class AdminCourseUpdateRequest(BaseModel):
    """
    Admin course update request model

    All fields are optional for partial updates.

    Example:
        >>> update = AdminCourseUpdateRequest(
        ...     title="Updated Title",
        ...     price=59.99
        ... )
    """
    title: Optional[str] = Field(None, min_length=3, max_length=255, description="Course title")
    description: Optional[str] = Field(None, description="Course description")
    category: Optional[str] = Field(None, description="Course category (legacy, use category_id)")
    category_id: Optional[int] = Field(None, description="Course category ID (references course_categories)")
    level: Optional[str] = Field(None, description="Difficulty level")
    language: Optional[str] = Field(None, max_length=2, description="Course language")
    price: Optional[Decimal] = Field(None, ge=0, description="Course price")
    is_public: Optional[bool] = Field(None, description="Is public course")
    thumbnail_url: Optional[str] = Field(None, max_length=1000, description="Thumbnail URL")
    preview_video_url: Optional[str] = Field(None, max_length=1000, description="Preview video URL")
    tags: Optional[List[str]] = Field(None, description="Course tags")

    @field_validator('language')
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language code"""
        if v is None:
            return v
        valid_languages = ['de', 'en', 'fr', 'es', 'it', 'nl', 'pl', 'pt', 'ru', 'tr', 'zh', 'ja', 'ko', 'ar', 'hi', 'sv', 'no', 'da', 'fi', 'el']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages[:5])}...')
        return v

    @field_validator('level')
    @classmethod
    def validate_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate difficulty level"""
        if v is None:
            return v
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if v not in valid_levels:
            raise ValueError(f'Level must be one of: {", ".join(valid_levels)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class AdminCourseStatusUpdateRequest(BaseModel):
    """
    Admin course status update request model

    Example:
        >>> request = AdminCourseStatusUpdateRequest(
        ...     action="publish",
        ...     reason="Quality approved by admin"
        ... )
    """
    action: str = Field(..., description="Action to perform (publish, unpublish, archive, unarchive)")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")

    @field_validator('action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Validate action"""
        valid_actions = ['publish', 'unpublish', 'archive', 'unarchive', 'restore', 'purge']
        if v not in valid_actions:
            raise ValueError(f'Action must be one of: {", ".join(valid_actions)}')
        return v

    model_config = ConfigDict(from_attributes=True)
