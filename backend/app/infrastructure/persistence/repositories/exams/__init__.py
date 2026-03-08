"""
Exams Repository Package

Exam and assessment repositories:
- ExamRepository: Exam CRUD and question management
- ExamSimulationRepository: Exam simulation and attempt management
- ExamSessionRepository: Hierarchical session grouping
- CurriculumFrameworkRepository: Curriculum framework CRUD and mappings

Example usage:
    >>> from app.infrastructure.persistence.repositories.exams.core import ExamRepository
    >>> from app.infrastructure.persistence.repositories.exams.sessions import ExamSessionRepository
    >>> from app.infrastructure.persistence.repositories.exams.curriculum import CurriculumFrameworkRepository
"""

from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.questions import ExamQuestionRepository
from app.infrastructure.persistence.repositories.exams.simulations import ExamSimulationRepository
from app.infrastructure.persistence.repositories.exams.trainer import ExamTrainerRepository
from app.infrastructure.persistence.repositories.exams.sessions import ExamSessionRepository
from app.infrastructure.persistence.repositories.exams.curriculum import CurriculumFrameworkRepository
from app.infrastructure.persistence.repositories.exams.user_exam_goals import UserExamGoalsRepository

__all__ = [
    'ExamRepository',
    'ExamQuestionRepository',
    'ExamSimulationRepository',
    'ExamTrainerRepository',
    'ExamSessionRepository',
    'CurriculumFrameworkRepository',
    'UserExamGoalsRepository',
]
