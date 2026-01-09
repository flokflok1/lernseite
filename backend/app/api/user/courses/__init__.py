"""
LernsystemX Course API Package (DDD-Compliant)

Course management following Domain-Driven Design principles.

Structure:
    - core/: Domain Layer (Factory, Services, Value Objects)
    - admin/: Admin-specific endpoints
    - user/: User-facing endpoints (crud/*, enrollment)
    - public/: Public endpoints

Modules:
    - core/factory: CourseFactory, ChapterFactory, LessonFactory
    - core/services: CourseService, EnrollmentService
    - core/value_objects: CourseStatus, Visibility, etc.
    - admin/crud: Admin course management
    - crud/courses: Course CRUD, publish/unpublish, stats
    - crud/chapters: Chapter management
    - crud/lessons: Lesson management
    - enrollment: Enrollment, progress, my-courses

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    Final URLs: /api/v1/courses/..., /api/v1/chapters/..., /api/v1/lessons/...
"""

from flask import Blueprint

# Import core layer (makes Factory & Services available)
from . import core

# Import admin module (registers admin routes)
from . import admin

# Import user-facing modules
from .crud.courses import courses_bp
from .crud.chapters import chapters_bp
from .crud.lessons import lessons_bp
from .enrollment import enrollment_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    courses_bp,
    enrollment_bp,
    chapters_bp,
    lessons_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    'core',
    'admin',
    'courses_bp',
    'enrollment_bp',
    'chapters_bp',
    'lessons_bp',
    'ALL_BLUEPRINTS',
]
