"""Exam Systems Domain - User Journey API Routes"""
from .ihk_exams import ihk_exams_user_bp
from .practical_exams import practical_exams_user_bp
from .chapter_completion_exams import chapter_completion_exams_user_bp

__all__ = [
    'ihk_exams_user_bp',
    'practical_exams_user_bp',
    'chapter_completion_exams_user_bp',
]
