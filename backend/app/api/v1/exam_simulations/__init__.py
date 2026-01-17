"""Exam Simulations API Module"""
from app.api.v1.exam_simulations.routes import exams_bp
from app.api.v1.exam_simulations.core import core_bp
from app.api.v1.exam_simulations.attempts import attempts_bp
from app.api.v1.exam_simulations.settings import settings_bp
__all__ = ['exams_bp', 'core_bp', 'attempts_bp', 'settings_bp']
