"""
Admin Course Management API

Handles all course-related admin operations.

Package Structure (Refactored 2026-01-08):
- content/: Chapter, lesson, and exam management (chapters, lessons, exams)
- management/: CRUD, files, prompts
- authoring.py: Kurs Studio (Chat-based Course Authoring)
- ai_settings.py: AI settings per course
- analytics.py: Course analytics
- system_features.py: System features per course

Example usage:
    >>> from app.api.admin.content_management.courses.management.crud import get_courses
    >>> from app.api.admin.content_management.courses.content.chapters import create_chapter
"""

# Import all packages and modules to register routes
# Only import each module ONCE to avoid duplicate blueprint registration
try:
    from app.api.admin.content_management.courses import content  # Contains chapters, lessons, exams
    from app.api.admin.content_management.courses import management  # Contains crud, files, prompts
    from app.api.admin.content_management.courses import authoring
    from app.api.admin.content_management.courses import ai_settings
    from app.api.admin.content_management.courses import analytics
    from app.api.admin.content_management.courses import system_features
except ImportError as e:
    import sys
    print(f"Warning: Failed to import courses modules: {e}", file=sys.stderr)

__all__ = [
    'content',      # Package (contains chapters, lessons, exams blueprints)
    'management',   # Package (contains crud, files, prompts blueprints)
    'authoring',    # Module (Kurs Studio endpoints)
    'ai_settings',  # Module
    'analytics',    # Module
    'system_features'  # Module
]
