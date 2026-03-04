"""
Exams Repository Package

Exam and assessment repositories:
- ExamRepository: Exam CRUD and question management
- ExamSimulationRepository: Exam simulation and attempt management
- ExamSessionRepository: Hierarchical session grouping

Example usage:
    >>> from app.infrastructure.persistence.repositories.exams.core import ExamRepository
    >>> from app.infrastructure.persistence.repositories.exams.sessions import ExamSessionRepository
"""

from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.simulations import ExamSimulationRepository
from app.infrastructure.persistence.repositories.exams.trainer import ExamTrainerRepository
from app.infrastructure.persistence.repositories.exams.sessions import ExamSessionRepository

__all__ = [
    'ExamRepository',
    'ExamSimulationRepository',
    'ExamTrainerRepository',
    'ExamSessionRepository',
]
