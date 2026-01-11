"""
Chapters Domain (DDD + Journey-Based Architecture)

Course chapters with DDD layers and journey-based API routes.
ALL data loaded dynamically from database - NO hardcoded values.

Architecture:
- domain/ - Domain entities and value objects
- application/ - Business logic services
- infrastructure/ - Database repositories
- journeys/ - Journey-based API routes (admin)

Usage:
    from src.api.content.courses.chapters import ChapterService, admin_chapters_bp

Exports:
- Chapter - Domain entity
- ChapterService - Business logic
- ChapterRepository - Database access
- admin_chapters_bp - Admin journey routes
"""

from src.api.content.courses.chapters.domain.entities.chapter import Chapter
from src.api.content.courses.chapters.application.services.chapter_service import ChapterService
from src.api.content.courses.chapters.infrastructure.repositories.chapter_repository import ChapterRepository
from src.api.content.courses.chapters.journeys.admin.api.routes.chapters import admin_chapters_bp

__all__ = [
    # Domain
    'Chapter',
    
    # Application
    'ChapterService',
    
    # Infrastructure
    'ChapterRepository',
    
    # Journeys
    'admin_chapters_bp',
]
