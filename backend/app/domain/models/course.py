"""
LernsystemX Course Models

Pydantic models for course-related operations:
- Course creation and management
- Module creation and ordering
- Course enrollment
- Course publishing

ISO 9001:2015 compliant - Course quality standards
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class CourseBase(BaseModel):
    """
    Base course model with common fields

    Example:
        >>> course = CourseBase(
        ...     title="Introduction to Python",
        ...     description="Learn Python from scratch"
        ... )
    """
    title: str = Field(..., min_length=3, max_length=255, description="Course title")
    description: Optional[str] = Field(None, description="Course description")
    language: str = Field(default="de", max_length=2, description="Course language (ISO 639-1)")
    difficulty: Optional[str] = Field(None, description="Course difficulty level")

    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code"""
        valid_languages = ['de', 'en', 'fr', 'es', 'it']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> Optional[str]:
        """Validate difficulty level"""
        if v is None:
            return v
        valid_difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
        if v not in valid_difficulties:
            raise ValueError(f'Difficulty must be one of: {", ".join(valid_difficulties)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class CourseCreate(CourseBase):
    """
    Course creation model

    Example:
        >>> course_data = CourseCreate(
        ...     title="Advanced Python",
        ...     description="Master advanced Python concepts",
        ...     category_id=1,
        ...     difficulty="advanced",
        ...     language="en"
        ... )
    """
    category_id: Optional[int] = Field(None, description="Course category ID")
    organisation_id: Optional[int] = Field(None, description="Organisation ID (for school/company courses)")

    model_config = ConfigDict(from_attributes=True)


class CourseUpdate(BaseModel):
    """
    Course update model

    All fields are optional for partial updates.

    Example:
        >>> update = CourseUpdate(title="Updated Title", difficulty="advanced")
    """
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    language: Optional[str] = Field(None, max_length=2)
    difficulty: Optional[str] = None
    is_published: Optional[bool] = None

    @field_validator('language')
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language code"""
        if v is None:
            return v
        valid_languages = ['de', 'en', 'fr', 'es', 'it']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> Optional[str]:
        """Validate difficulty level"""
        if v is None:
            return v
        valid_difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
        if v not in valid_difficulties:
            raise ValueError(f'Difficulty must be one of: {", ".join(valid_difficulties)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class CourseResponse(CourseBase):
    """
    Course response model

    Example:
        >>> course = CourseResponse(
        ...     course_id=1,
        ...     title="Python Basics",
        ...     description="Learn Python",
        ...     creator_id=1,
        ...     is_published=True,
        ...     created_at=datetime.now()
        ... )
    """
    course_id: int = Field(..., description="Course ID")
    creator_id: int = Field(..., description="Course creator user ID")
    organisation_id: Optional[int] = Field(None, description="Organisation ID")
    category_id: Optional[int] = Field(None, description="Category ID")
    is_published: bool = Field(default=False, description="Course published status")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    created_at: datetime = Field(..., description="Course creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Additional computed fields
    module_count: Optional[int] = Field(None, description="Number of modules")
    enrollment_count: Optional[int] = Field(None, description="Number of enrolled students")
    creator_name: Optional[str] = Field(None, description="Creator full name")

    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(CourseResponse):
    """
    Detailed course response with modules

    Example:
        >>> course = CourseDetailResponse(
        ...     course_id=1,
        ...     title="Python Basics",
        ...     modules=[module1, module2]
        ... )
    """
    modules: List['ModuleResponse'] = Field(default=[], description="Course modules")
    total_duration: Optional[int] = Field(None, description="Total course duration in minutes")

    model_config = ConfigDict(from_attributes=True)


class CourseListResponse(BaseModel):
    """
    Paginated course list response

    Example:
        >>> course_list = CourseListResponse(
        ...     items=[course1, course2],
        ...     total=50,
        ...     page=1,
        ...     per_page=10
        ... )
    """
    items: List[CourseResponse] = Field(..., description="List of courses")
    total: int = Field(..., description="Total number of courses")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_prev: bool = Field(..., description="Has previous page")
    has_next: bool = Field(..., description="Has next page")

    model_config = ConfigDict(from_attributes=True)


class ModuleBase(BaseModel):
    """
    Base module model

    Example:
        >>> module = ModuleBase(
        ...     title="Introduction",
        ...     description="Course introduction",
        ...     order_index=1
        ... )
    """
    title: str = Field(..., min_length=3, max_length=255, description="Module title")
    description: Optional[str] = Field(None, description="Module description")
    order_index: int = Field(..., ge=0, description="Module order in course (0-based)")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Estimated duration in minutes")

    model_config = ConfigDict(from_attributes=True)


class ModuleCreate(ModuleBase):
    """
    Module creation model

    Example:
        >>> module_data = ModuleCreate(
        ...     course_id=1,
        ...     title="Lesson 1",
        ...     order_index=0,
        ...     content={"type": "text", "data": "..."}
        ... )
    """
    course_id: int = Field(..., description="Course ID")
    content: Optional[Dict[str, Any]] = Field(None, description="Module content (JSONB)")

    model_config = ConfigDict(from_attributes=True)


class ModuleUpdate(BaseModel):
    """
    Module update model

    All fields are optional for partial updates.

    Example:
        >>> update = ModuleUpdate(title="Updated Title", order_index=2)
    """
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    order_index: Optional[int] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(None, ge=0)

    model_config = ConfigDict(from_attributes=True)


class ModuleResponse(ModuleBase):
    """
    Module response model

    Example:
        >>> module = ModuleResponse(
        ...     module_id=1,
        ...     course_id=1,
        ...     title="Introduction",
        ...     order_index=0,
        ...     created_at=datetime.now()
        ... )
    """
    module_id: int = Field(..., description="Module ID")
    course_id: int = Field(..., description="Course ID")
    content: Optional[Dict[str, Any]] = Field(None, description="Module content")
    created_at: datetime = Field(..., description="Module creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class EnrollmentCreate(BaseModel):
    """
    Course enrollment model

    Example:
        >>> enrollment = EnrollmentCreate(course_id=1)
    """
    course_id: int = Field(..., description="Course ID to enroll in")

    model_config = ConfigDict(from_attributes=True)


class EnrollmentResponse(BaseModel):
    """
    Enrollment response model

    Example:
        >>> enrollment = EnrollmentResponse(
        ...     enrollment_id=1,
        ...     user_id=5,
        ...     course_id=10,
        ...     progress=45.5,
        ...     enrolled_at=datetime.now()
        ... )
    """
    enrollment_id: int = Field(..., description="Enrollment ID")
    user_id: int = Field(..., description="User ID")
    course_id: int = Field(..., description="Course ID")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Course progress percentage")
    completed: bool = Field(default=False, description="Course completed")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    enrolled_at: datetime = Field(..., description="Enrollment timestamp")

    model_config = ConfigDict(from_attributes=True)


class CoursePublish(BaseModel):
    """
    Course publish/unpublish model

    Example:
        >>> publish = CoursePublish(is_published=True)
    """
    is_published: bool = Field(..., description="Publish status")

    model_config = ConfigDict(from_attributes=True)


class CourseStats(BaseModel):
    """
    Course statistics model

    Example:
        >>> stats = CourseStats(
        ...     total_enrollments=150,
        ...     active_students=120,
        ...     completion_rate=75.5,
        ...     average_progress=62.3
        ... )
    """
    total_enrollments: int = Field(..., description="Total number of enrollments")
    active_students: int = Field(..., description="Number of active students")
    completed_students: int = Field(..., description="Number of students who completed")
    completion_rate: float = Field(..., ge=0.0, le=100.0, description="Completion rate percentage")
    average_progress: float = Field(..., ge=0.0, le=100.0, description="Average progress percentage")
    total_modules: int = Field(..., description="Total number of modules")
    total_duration: int = Field(..., description="Total course duration in minutes")

    model_config = ConfigDict(from_attributes=True)


class LessonBase(BaseModel):
    """
    Base lesson model

    Example:
        >>> lesson = LessonBase(
        ...     title="Python Variables",
        ...     content_type="video",
        ...     order_index=1
        ... )
    """
    title: str = Field(..., min_length=3, max_length=255, description="Lesson title")
    content_type: str = Field(..., description="Content type (video, text, quiz, assignment, file)")
    order_index: int = Field(..., ge=0, description="Lesson order in module (0-based)")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Estimated duration in minutes")

    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """Validate content type"""
        valid_types = ['video', 'text', 'quiz', 'assignment', 'file']
        if v not in valid_types:
            raise ValueError(f'Content type must be one of: {", ".join(valid_types)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class LessonCreate(LessonBase):
    """
    Lesson creation model

    Example:
        >>> lesson_data = LessonCreate(
        ...     module_id=1,
        ...     title="Variables in Python",
        ...     content_type="video",
        ...     content_url="https://vimeo.com/123",
        ...     order_index=0
        ... )
    """
    module_id: int = Field(..., description="Module ID")
    content_url: Optional[str] = Field(None, max_length=1000, description="Content URL (video/file)")
    content_text: Optional[str] = Field(None, description="Text content")
    quiz_data: Optional[Dict[str, Any]] = Field(None, description="Quiz data (JSON)")
    is_preview: bool = Field(default=False, description="Is free preview lesson")

    model_config = ConfigDict(from_attributes=True)


class LessonUpdate(BaseModel):
    """
    Lesson update model

    All fields are optional for partial updates.

    Example:
        >>> update = LessonUpdate(title="Updated Title", duration_minutes=20)
    """
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    content_type: Optional[str] = None
    content_url: Optional[str] = Field(None, max_length=1000)
    content_text: Optional[str] = None
    quiz_data: Optional[Dict[str, Any]] = None
    order_index: Optional[int] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(None, ge=0)
    is_preview: Optional[bool] = None

    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate content type"""
        if v is None:
            return v
        valid_types = ['video', 'text', 'quiz', 'assignment', 'file']
        if v not in valid_types:
            raise ValueError(f'Content type must be one of: {", ".join(valid_types)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class LessonResponse(LessonBase):
    """
    Lesson response model

    Example:
        >>> lesson = LessonResponse(
        ...     lesson_id=1,
        ...     module_id=1,
        ...     title="Variables",
        ...     content_type="video",
        ...     order_index=0,
        ...     created_at=datetime.now()
        ... )
    """
    lesson_id: int = Field(..., description="Lesson ID")
    module_id: int = Field(..., description="Module ID")
    content_url: Optional[str] = Field(None, description="Content URL")
    content_text: Optional[str] = Field(None, description="Text content")
    quiz_data: Optional[Dict[str, Any]] = Field(None, description="Quiz data")
    is_preview: bool = Field(default=False, description="Is free preview")
    created_at: datetime = Field(..., description="Lesson creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


# Update forward references
CourseDetailResponse.model_rebuild()
