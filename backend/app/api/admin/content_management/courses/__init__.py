"""
Admin Course Management API

Handles all course-related admin operations.

Package Structure (Refactored 2026-01-08):
- content/: Chapter, lesson, and exam management
- management/: CRUD, files, prompts
- ai/: AI settings and authoring (bridge to standalone files)
- analytics/: Course analytics (bridge to standalone file)
- features/: System features (bridge to standalone file)

Example usage:
    >>> from app.api.admin.content_management.courses.management.crud import get_courses
    >>> from app.api.admin.content_management.courses.content.chapters import create_chapter
"""

# Import all packages and modules to register routes
from app.api.admin.content_management.courses import (
    content,
    management,
    ai_settings,
    authoring,
    analytics,
    system_features
)

__all__ = [
    'content',
    'management',
    'ai_settings',
    'authoring',
    'analytics',
    'system_features'
]
