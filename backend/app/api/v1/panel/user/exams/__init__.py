"""
User Exams Module — Exam trainer + community upload endpoints.

Provides practice mode, topic-based training, timed exam attempts,
and community PDF upload with moderation.
"""

from .trainer import trainer_bp
from .upload import upload_bp as exam_upload_bp

__all__ = ['trainer_bp', 'exam_upload_bp']
