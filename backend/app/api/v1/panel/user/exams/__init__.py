"""
User Exams Module — Exam trainer + community upload endpoints.

Provides practice mode, topic-based training, timed exam attempts,
community PDF upload with moderation, and the AP2-specific trainer
(Active Recall + SM-2 + IHK-Stil for FA 235 Baden-Württemberg).
"""

from .trainer import trainer_bp
from .upload import upload_bp as exam_upload_bp
from .ap2 import ap2_trainer_bp

__all__ = ['trainer_bp', 'exam_upload_bp', 'ap2_trainer_bp']
