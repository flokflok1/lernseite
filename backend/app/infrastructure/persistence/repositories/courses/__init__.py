"""
LernsystemX Course Repository Package

Data access layer for course management:
- CRUD operations for courses
- Course search and filtering
- Course publishing and archiving
- Admin course management
- Statistics and analytics
- Chapter and lesson management
- AI settings and file attachments
- Multi-tenancy support (LSX Academy, Schools, Companies)
- Creator and organisation-based access control

ISO 27001:2013 compliant - Secure course data management

This package provides backward-compatible bridge for existing imports:
    from app.infrastructure.persistence.repositories.courses import CourseRepository
    # Maps to: from app.infrastructure.persistence.repositories.courses import CourseRepository
"""

from app.infrastructure.persistence.repositories.courses.crud import CourseRepositoryCRUD
from app.infrastructure.persistence.repositories.courses.search import CourseRepositorySearch
from app.infrastructure.persistence.repositories.courses.admin import CourseRepositoryAdmin
from app.infrastructure.persistence.repositories.courses.lifecycle import CourseRepositoryLifecycle
from app.infrastructure.persistence.repositories.courses.statistics import CourseRepositoryStatistics
from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository
from app.infrastructure.persistence.repositories.courses.ai_settings import CourseAiSettingsRepository
from app.infrastructure.persistence.repositories.courses.files import CourseFileRepository
from app.infrastructure.persistence.repositories.courses.analytics import CourseAnalyticsRepository

# Alias for backward compatibility (AI vs Ai naming)
CourseAISettingsRepository = CourseAiSettingsRepository


class CourseRepository(
    CourseRepositoryCRUD,
    CourseRepositorySearch,
    CourseRepositoryAdmin,
    CourseRepositoryLifecycle,
    CourseRepositoryStatistics
):
    """
    Unified CourseRepository combining all functionality

    This class uses multiple inheritance to aggregate methods from specialized
    module classes. All methods are organized by domain:
    - CRUD: Create, find, update operations
    - Search: Public course search and filtering
    - Admin: Admin-only operations
    - Lifecycle: Publishing, archiving workflows
    - Statistics: Course metrics and analytics

    Example:
        >>> course = CourseRepository.find_by_id(123)
        >>> stats = CourseRepository.get_statistics(123)
        >>> results = CourseRepository.search_public_courses(level='beginner')
    """
    pass


__all__ = [
    'CourseRepository',
    'CourseRepositoryCRUD',
    'CourseRepositorySearch',
    'CourseRepositoryAdmin',
    'CourseRepositoryLifecycle',
    'CourseRepositoryStatistics',
    'ChapterRepository',
    'LessonRepository',
    'CourseAiSettingsRepository',
    'CourseAISettingsRepository',  # Alias
    'CourseFileRepository',
    'CourseAnalyticsRepository',
]
