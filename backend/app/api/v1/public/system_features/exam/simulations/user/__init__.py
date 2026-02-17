"""
Exam Simulations - User Routes

User-facing exam simulation endpoints:
- core.py       # Core simulation execution (start, submit, results)
- attempts.py   # Attempt history and review
- settings.py   # User simulation preferences
"""

from app.api.v1.public.system_features.exam.simulations.user.core import core_bp, course_bp
from app.api.v1.public.system_features.exam.simulations.user.attempts import attempts_bp
from app.api.v1.public.system_features.exam.simulations.user.settings import settings_bp

__all__ = ['core_bp', 'course_bp', 'attempts_bp', 'settings_bp']
