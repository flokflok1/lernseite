"""
Exams Service Package

Application services for exam management:
- ExamArchiveService: Import exam PDFs and images into the archive
- ExamCourseGeneratorService: Generate courses from exam content
- CurriculumService: AI PDF import, question mapping, user profiles
- TaxonomyBootstrapService: AI-powered taxonomy bootstrapping
"""

from app.application.services.exams.archive_service import ExamArchiveService
from app.application.services.exams.course_generator_service import ExamCourseGeneratorService
from app.application.services.exams.curriculum_service import CurriculumService
from app.application.services.exams.taxonomy_bootstrap_service import TaxonomyBootstrapService
from app.application.services.exams.question_generator_service import QuestionGeneratorService
from app.application.services.exams.gap_content_service import GapContentService

__all__ = [
    'ExamArchiveService',
    'ExamCourseGeneratorService',
    'CurriculumService',
    'TaxonomyBootstrapService',
    'QuestionGeneratorService',
    'GapContentService',
]
