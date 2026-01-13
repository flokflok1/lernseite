"""
LernsystemX Celery Tasks

Background task processing for:
- Exam simulation generation
- AI content generation
- File processing
- Analytics updates
"""

from app.tasks.exam_tasks import generate_exam_task

__all__ = ['generate_exam_task']
