"""Exam Systems Domain - All Journeys"""

from .admin import (
    ihk_exams_bp,
    practical_exams_bp,
    chapter_completion_exams_bp,
)

from .user import (
    ihk_exams_user_bp,
    practical_exams_user_bp,
    chapter_completion_exams_user_bp,
)

ALL_JOURNEY_BLUEPRINTS = [
    # Admin Journey (7 endpoints)
    ihk_exams_bp,  # 3 endpoints
    practical_exams_bp,  # 2 endpoints
    chapter_completion_exams_bp,  # 2 endpoints

    # User Journey (9 endpoints)
    ihk_exams_user_bp,  # 3 endpoints
    practical_exams_user_bp,  # 3 endpoints
    chapter_completion_exams_user_bp,  # 3 endpoints
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    # Admin
    'ihk_exams_bp',
    'practical_exams_bp',
    'chapter_completion_exams_bp',
    # User
    'ihk_exams_user_bp',
    'practical_exams_user_bp',
    'chapter_completion_exams_user_bp',
]
