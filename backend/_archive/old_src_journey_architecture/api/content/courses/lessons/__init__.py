"""
Lessons Domain (DDD + Journey-Based Architecture)

Course lessons with DDD layers and journey-based API routes.
ALL data loaded dynamically from database - NO hardcoded values.

Architecture:
- domain/ - Domain entities and value objects
- application/ - Business logic services
- infrastructure/ - Database repositories
- journeys/ - Journey-based API routes (admin)

Usage:
    from src.api.content.courses.lessons import LessonService, admin_lessons_bp

Exports:
- Lesson - Domain entity
- LessonService - Business logic
- LessonRepository - Database access
- admin_lessons_bp - Admin journey routes
"""

from src.api.content.courses.lessons.domain.entities.lesson import Lesson
from src.api.content.courses.lessons.application.services.lesson_service import LessonService
from src.api.content.courses.lessons.infrastructure.repositories.lesson_repository import LessonRepository
from src.api.content.courses.lessons.journeys.admin.api.routes.lessons import admin_lessons_bp

__all__ = [
    # Domain
    'Lesson',
    
    # Application
    'LessonService',
    
    # Infrastructure
    'LessonRepository',
    
    # Journeys
    'admin_lessons_bp',
]
