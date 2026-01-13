"""
Admin Exam Endpoints Package.

Admin-only endpoints for exam management:
- Exam context detection
- Exam generation triggering
"""

from .context import exam_context_bp
from .generation import exam_generation_bp

__all__ = [
    'exam_context_bp',
    'exam_generation_bp',
]
