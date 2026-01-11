"""
Learning Methods Domain (DDD + Journey-Based Architecture)

Learning methods (12 Content-Lernmethoden: LM00-LM11) with DDD layers and journey-based API routes.
ALL data loaded dynamically from database - NO hardcoded values.

Architecture:
- domain/ - Domain entities (LearningMethodType, LearningMethodInstance)
- application/ - Business logic services
- infrastructure/ - Database repositories
- journeys/ - Journey-based API routes (admin)

12 Content-Lernmethoden in 3 Groups:
- Group A (Erklärend): LM00-LM04 (5 methods)
- Group B (Praxis): LM05-LM08 (4 methods)
- Group C (Prüfung): LM09-LM11 (3 methods)

Usage:
    from src.api.content.learning_methods import LearningMethodService, admin_learning_methods_bp

Exports:
- LearningMethodType - Domain entity for LM type
- LearningMethodInstance - Domain entity for LM instance
- LearningMethodService - Business logic
- LearningMethodRepository - Database access
- admin_learning_methods_bp - Admin journey routes
"""

from src.api.content.learning_methods.domain.entities.learning_method_type import LearningMethodType
from src.api.content.learning_methods.domain.entities.learning_method_instance import LearningMethodInstance
from src.api.content.learning_methods.application.services.learning_method_service import LearningMethodService
from src.api.content.learning_methods.infrastructure.repositories.learning_method_repository import LearningMethodRepository
from src.api.content.learning_methods.journeys.admin.api.routes.learning_methods import admin_learning_methods_bp

__all__ = [
    # Domain
    'LearningMethodType',
    'LearningMethodInstance',

    # Application
    'LearningMethodService',

    # Infrastructure
    'LearningMethodRepository',

    # Journeys
    'admin_learning_methods_bp',
]
