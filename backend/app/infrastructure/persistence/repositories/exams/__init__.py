"""
Exams Repository Package

Exam and assessment repositories:
- ExamRepository: Exam CRUD and question management
- ExamSimulationRepository: Exam simulation and attempt management

Example usage:
    >>> from app.infrastructure.persistence.repositories.exams.core import ExamRepository
    >>> from app.infrastructure.persistence.repositories.exams.simulations import ExamSimulationRepository
"""

from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.simulations import ExamSimulationRepository

__all__ = ['ExamRepository', 'ExamSimulationRepository']
