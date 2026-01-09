"""
Courses Domain (DDD + Journey-Based Architecture)

Content courses with DDD layers and journey-based API routes.
ALL data loaded dynamically from database - NO hardcoded values.

Architecture:
- core/ - DDD layers (domain, application, infrastructure)
- journeys/ - Journey-based API routes (admin, learner)

Usage:
    from src.api.content.courses import CourseService, admin_courses_bp, learner_courses_bp

Exports:
- CourseService - Business logic for courses
- Course - Domain entity
- CourseRepository - Database access
- admin_courses_bp - Admin journey routes
- learner_courses_bp - Learner journey routes
"""

from src.api.content.courses.core.domain.entities.course import Course
from src.api.content.courses.core.application.services.course_service import CourseService
from src.api.content.courses.core.infrastructure.repositories.course_repository import CourseRepository
from src.api.content.courses.journeys.admin.api.routes.courses import admin_courses_bp
from src.api.content.courses.journeys.learner.api.routes.courses import learner_courses_bp

__all__ = [
    # Domain
    'Course',
    
    # Application
    'CourseService',
    
    # Infrastructure
    'CourseRepository',
    
    # Journeys
    'admin_courses_bp',
    'learner_courses_bp',
]
