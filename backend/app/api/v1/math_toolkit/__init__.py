"""Math Toolkit API Module"""
from app.api.v1.math_toolkit.admin import admin_bp
from app.api.v1.math_toolkit.practice import practice_bp
from app.api.v1.math_toolkit.reference import reference_bp
from app.api.v1.math_toolkit.tasks import tasks_bp
__all__ = ['admin_bp', 'practice_bp', 'reference_bp', 'tasks_bp']
