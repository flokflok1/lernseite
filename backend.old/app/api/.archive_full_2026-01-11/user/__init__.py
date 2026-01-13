"""
LernsystemX User API Package

User-facing endpoints for courses, lessons, dashboard, exams, etc.

Refactored: 2026-01-08 - ISO/IEC 26515 + DDD compliant
Struktur parallel zu Frontend (components/user/)

Package Structure:
├── courses/         # Course enrollment, access, progress
├── chapters/        # Chapter theory (former chapter_theory/)
├── lessons/         # Lesson player, explanations, videos
├── dashboard/       # User dashboard, widgets, layouts
├── exams/           # Exam simulations, attempts, results
├── profile/         # User profile management
├── subscriptions/   # Subscription management (Premium)
├── tokens/          # Token wallet, transactions
└── learning_methods/ (TBD)

Example usage:
    >>> from app.api.user.courses import enrollment
    >>> from app.api.user.dashboard import widgets
"""

# Import user packages to trigger blueprint registration
from app.api.user import profile
from app.api.user import subscriptions
from app.api.user import tokens
from app.api.user import courses
from app.api.user import gamification

__all__ = [
    'courses',
    'chapters',
    'lessons',
    'dashboard',
    'exams',
    'profile',
    'subscriptions',
    'tokens'
]
