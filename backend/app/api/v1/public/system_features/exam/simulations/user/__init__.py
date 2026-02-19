"""
Exam Simulations - User Routes

User-facing exam simulation endpoints:
- core.py        # Service layer, models, blueprint definitions
- core_part2.py  # Route endpoints (create, list, get, delete)
- attempts.py    # Attempt history and review
- settings.py    # User simulation preferences
"""

from app.api.v1.public.system_features.exam.simulations.user.core import core_bp, course_bp
import app.api.v1.public.system_features.exam.simulations.user.core_part2  # noqa: F401 - registers routes on blueprints
from app.api.v1.public.system_features.exam.simulations.user.attempts import attempts_bp
from app.api.v1.public.system_features.exam.simulations.user.settings import settings_bp

__all__ = ['core_bp', 'course_bp', 'attempts_bp', 'settings_bp']
