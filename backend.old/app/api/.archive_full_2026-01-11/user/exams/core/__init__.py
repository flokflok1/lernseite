"""
Exam Domain Core Package.

Core domain logic following DDD principles:
- Value Objects: Immutable domain concepts
- Factory: Object creation with business rules
- Services: Domain logic and orchestration
- Models: Pydantic validation models
"""

from .value_objects import (
    ExamType, QuestionType, ExamStatus, AttemptStatus,
    Difficulty, ExamMode, ExamConfig, ExamContext
)
from .factory import ExamFactory, QuestionFactory
from .services import ExamService, ExamGenerationService
from .models import (
    ExamSimulationCreate, ExamAttemptSubmit, UserExamProfileUpdate,
    ExamSimulationResponse, ExamAttemptResponse, ExamResultResponse,
    ExamContextResponse
)

__all__ = [
    # Value Objects
    'ExamType',
    'QuestionType',
    'ExamStatus',
    'AttemptStatus',
    'Difficulty',
    'ExamMode',
    'ExamConfig',
    'ExamContext',
    # Factories
    'ExamFactory',
    'QuestionFactory',
    # Services
    'ExamService',
    'ExamGenerationService',
    # Pydantic Models
    'ExamSimulationCreate',
    'ExamAttemptSubmit',
    'UserExamProfileUpdate',
    'ExamSimulationResponse',
    'ExamAttemptResponse',
    'ExamResultResponse',
    'ExamContextResponse',
]
