"""
LernsystemX Exam Simulation API Package (DDD Refactored)

KI-Prüfungssimulation Endpoints refactored following Domain-Driven Design (DDD).

Structure:
    admin/          - Admin endpoints (context detection, generation)
    user/           - User endpoints (CRUD, attempts, profile)
    core/           - Domain core (value objects, factory, services, models)

Modules:
    - admin/context.py          - Exam context detection
    - admin/generation.py       - AI generation triggering
    - user/simulations.py       - CRUD operations
    - user/attempts.py          - Exam attempt lifecycle
    - user/user_profile.py      - User exam settings
    - core/value_objects.py     - Domain value objects
    - core/factory.py           - DDD Factory pattern
    - core/services.py          - Domain services
    - core/models.py            - Pydantic validation models

Endpoints:
- GET    /api/v1/courses/:id/exam-context        - Get detected exam context (Admin)
- POST   /api/v1/courses/:id/exam-simulations    - Create new exam simulation (User)
- GET    /api/v1/exam-simulations                - List user's simulations (User)
- GET    /api/v1/exam-simulations/:id            - Get simulation details (User)
- DELETE /api/v1/exam-simulations/:id            - Delete simulation (User)
- POST   /api/v1/exam-simulations/:id/generate   - Start generation (Admin)
- POST   /api/v1/exam-simulations/:id/start      - Start attempt (User)
- GET    /api/v1/exam-simulations/:id/attempts   - Get attempts (User)
- POST   /api/v1/exam-simulations/:id/submit     - Submit attempt (User)
- GET    /api/v1/user-profile/exam-settings      - Get user exam profile (User)
- PUT    /api/v1/user-profile/exam-settings      - Update user exam profile (User)

DDD Structure:
    Core Domain:
        - Value Objects: ExamType, QuestionType, ExamStatus, AttemptStatus, Difficulty, ExamMode
        - Entities: ExamConfig, ExamContext (immutable)
        - Factory: ExamFactory, QuestionFactory (object creation)
        - Services: ExamService, ExamGenerationService (business logic)

    Application Layer:
        - Admin: Context detection, generation triggering
        - User: Simulation CRUD, attempts, profile

ISO 27001:2013 compliant - Exam Simulation System
DDD Refactored: 2026-01-08 per Developer-Guide-KI Section 10
"""

from .admin import exam_context_bp, exam_generation_bp
from .user import (
    exam_simulations_bp, exam_simulations_course_bp,
    exam_attempts_bp, exam_user_profile_bp
)
from .core import (
    ExamSimulationCreate, ExamAttemptSubmit,
    ExamFactory, ExamService
)

# All blueprints in this package
ALL_BLUEPRINTS = [
    # Admin
    exam_context_bp,
    exam_generation_bp,
    # User
    exam_simulations_bp,
    exam_simulations_course_bp,
    exam_attempts_bp,
    exam_user_profile_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints and models for direct import
__all__ = [
    # Admin Blueprints
    'exam_context_bp',
    'exam_generation_bp',
    # User Blueprints
    'exam_simulations_bp',
    'exam_simulations_course_bp',
    'exam_attempts_bp',
    'exam_user_profile_bp',
    'ALL_BLUEPRINTS',
    # Core Domain
    'ExamSimulationCreate',
    'ExamAttemptSubmit',
    'ExamFactory',
    'ExamService',
]
