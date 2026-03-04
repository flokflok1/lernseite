"""
LernsystemX Celery Tasks

Background task processing for:
- Exam simulation generation
- Exam archive analysis (real IHK PDFs)
- AI content generation
- File processing
- Analytics updates
"""

from app.infrastructure.tasks.exam_tasks import generate_exam_task
from app.infrastructure.tasks.exam_archive_tasks import analyze_exam_pdf_task

__all__ = ['generate_exam_task', 'analyze_exam_pdf_task']
