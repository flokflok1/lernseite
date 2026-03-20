"""
Exams Repository Package

Exam and assessment repositories:
- ExamRepository: Exam CRUD and question management
- ExamSimulationRepository: Exam simulation and attempt management
- ExamSessionRepository: Hierarchical session grouping
- CurriculumFrameworkRepository: Curriculum framework CRUD and mappings
- PerformanceStatsRepository: Anonymized peer comparison aggregates
- ExamProgramRepository: Exam programs (Beruf/Zertifizierung) hierarchy

Example usage:
    >>> from app.infrastructure.persistence.repositories.exams.core import ExamRepository
    >>> from app.infrastructure.persistence.repositories.exams.sessions import ExamSessionRepository
    >>> from app.infrastructure.persistence.repositories.exams.curriculum import CurriculumFrameworkRepository
    >>> from app.infrastructure.persistence.repositories.exams.programs import ExamProgramRepository
"""

from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.questions import ExamQuestionRepository
from app.infrastructure.persistence.repositories.exams.simulations import ExamSimulationRepository
from app.infrastructure.persistence.repositories.exams.trainer import ExamTrainerRepository
from app.infrastructure.persistence.repositories.exams.sessions import ExamSessionRepository
from app.infrastructure.persistence.repositories.exams.curriculum import CurriculumFrameworkRepository
from app.infrastructure.persistence.repositories.exams.user_exam_goals import UserExamGoalsRepository
from app.infrastructure.persistence.repositories.exams.performance_stats import PerformanceStatsRepository
from app.infrastructure.persistence.repositories.exams.programs import ExamProgramRepository
from app.infrastructure.persistence.repositories.exams.program_types import ProgramTypeRepository
from app.infrastructure.persistence.repositories.exams.folders import ArchiveFolderRepository

__all__ = [
    'ExamRepository',
    'ExamQuestionRepository',
    'ExamSimulationRepository',
    'ExamTrainerRepository',
    'ExamSessionRepository',
    'CurriculumFrameworkRepository',
    'UserExamGoalsRepository',
    'PerformanceStatsRepository',
    'ExamProgramRepository',
    'ProgramTypeRepository',
    'ArchiveFolderRepository',
]
