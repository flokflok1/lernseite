"""
User Exam Endpoints Package.

User-facing endpoints for exam interaction:
- Exam simulation management (CRUD)
- Exam attempts (start, submit, list)
- User exam profile settings
"""

from .simulations import exam_simulations_bp, exam_simulations_course_bp
from .attempts import exam_attempts_bp
from .user_profile import exam_user_profile_bp

__all__ = [
    'exam_simulations_bp',
    'exam_simulations_course_bp',
    'exam_attempts_bp',
    'exam_user_profile_bp',
]
