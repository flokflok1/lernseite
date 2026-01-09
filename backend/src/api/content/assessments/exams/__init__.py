"""
Exams Domain (DDD + Journey-Based Architecture)

Exams/assessments with DDD layers and journey-based API routes.
ALL data loaded dynamically from database - NO hardcoded values.

Architecture:
- domain/ - Domain entities and value objects
- application/ - Business logic services
- infrastructure/ - Database repositories
- journeys/ - Journey-based API routes (admin)

Usage:
    from src.api.content.assessments.exams import ExamService, admin_exams_bp

Exports:
- Exam - Domain entity
- ExamService - Business logic
- ExamRepository - Database access
- admin_exams_bp - Admin journey routes
"""

from src.api.content.assessments.exams.domain.entities.exam import Exam
from src.api.content.assessments.exams.application.services.exam_service import ExamService
from src.api.content.assessments.exams.infrastructure.repositories.exam_repository import ExamRepository
from src.api.content.assessments.exams.journeys.admin.api.routes.exams import admin_exams_bp

__all__ = [
    # Domain
    'Exam',
    
    # Application
    'ExamService',
    
    # Infrastructure
    'ExamRepository',
    
    # Journeys
    'admin_exams_bp',
]
