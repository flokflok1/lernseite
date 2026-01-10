"""Exam Systems Domain - Admin Journey API Routes"""
from .ihk_exams import ihk_exams_bp
from .practical_exams import practical_exams_bp
from .chapter_completion_exams import chapter_completion_exams_bp

__all__ = [
    'ihk_exams_bp',
    'practical_exams_bp',
    'chapter_completion_exams_bp',
]
