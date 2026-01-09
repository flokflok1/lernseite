"""
Admin Course Chapters API - Bridge Module

DEPRECATED: This file is a bridge module for backward compatibility.
All functionality has been moved into the admin/courses/content/ package.

Original: 200 LOC
Refactored: admin/courses/content/chapters.py (200 LOC)

Endpoints:
- GET    /api/v1/admin/courses/<course_id>/chapters  - List chapters
- POST   /api/v1/admin/courses/<course_id>/chapters  - Create chapter
- PUT    /api/v1/admin/courses/chapters/<chapter_id> - Update chapter
- DELETE /api/v1/admin/courses/chapters/<chapter_id> - Delete chapter
- PUT    /api/v1/admin/courses/chapters/<chapter_id>/reorder - Reorder
"""

# Re-export from the refactored package
from app.api.admin.content_management.courses.content.chapters import *

__all__ = ['chapters']
