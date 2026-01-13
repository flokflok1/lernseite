"""
Course Domain Layer (DDD Core)

This package contains the domain logic for the courses bounded context.
Follows Domain-Driven Design (DDD) principles.

Components:
- factory.py: CourseFactory, ChapterFactory, LessonFactory
- services.py: CourseService, EnrollmentService (business logic)
- value_objects.py: CourseStatus, Visibility, Price, etc.

Usage:
    >>> from app.api.user.courses.core import CourseFactory, CourseService
    >>> course = CourseFactory.create_draft(creator_id, title, category_id)
    >>> can_enroll, reason = CourseService.can_user_enroll(user, course)
"""

from .factory import CourseFactory, ChapterFactory, LessonFactory
from .services import CourseService, EnrollmentService
from .value_objects import (
    CourseStatus,
    Visibility,
    EnrollmentType,
    EnrollmentStatus,
    LessonType,
    CourseSettings,
    Price,
    EnrollmentWindow,
    ProgressSnapshot,
    CourseId,
    ChapterId,
    LessonId,
    UserId
)

__all__ = [
    # Factories
    'CourseFactory',
    'ChapterFactory',
    'LessonFactory',

    # Services
    'CourseService',
    'EnrollmentService',

    # Value Objects - Enums
    'CourseStatus',
    'Visibility',
    'EnrollmentType',
    'EnrollmentStatus',
    'LessonType',

    # Value Objects - Dataclasses
    'CourseSettings',
    'Price',
    'EnrollmentWindow',
    'ProgressSnapshot',

    # Type Aliases
    'CourseId',
    'ChapterId',
    'LessonId',
    'UserId'
]
