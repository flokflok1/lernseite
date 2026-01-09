"""
LernsystemX Shared API Package

Role-independent endpoints for categories, feedback, media, organisations, users.

Refactored: 2026-01-08 - ISO/IEC 26515 + DDD compliant

Package Structure:
├── categories/      # Course categories (hierarchical)
├── feedback/        # User feedback system
├── media/           # Media files (TTS, audio, video)
├── organisations/   # Organisation management
└── users/           # User CRUD (admin + self-management)

Example usage:
    >>> from app.api.shared.categories import hierarchy
    >>> from app.api.shared.media import tts
"""

__all__ = [
    'categories',
    'feedback',
    'media',
    'organisations',
    'users'
]
