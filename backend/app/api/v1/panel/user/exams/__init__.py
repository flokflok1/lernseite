"""
User Exams Module — Exam trainer endpoints for end-users.

Provides practice mode, topic-based training, and timed exam attempts.
"""

from .trainer import trainer_bp

__all__ = ['trainer_bp']
