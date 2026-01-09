"""
Admin Course Lessons API - Bridge Module

DEPRECATED: This file is a bridge module for backward compatibility.
All functionality has been moved into the admin/courses/content/ package.

Original: 228 LOC
Refactored: admin/courses/content/lessons.py (228 LOC)

Endpoints:
- GET    /api/v1/admin/courses/chapters/<chapter_id>/lessons - List lessons
- POST   /api/v1/admin/courses/chapters/<chapter_id>/lessons - Create lesson
- PUT    /api/v1/admin/courses/lessons/<lesson_id> - Update lesson
- DELETE /api/v1/admin/courses/lessons/<lesson_id> - Delete lesson
- PUT    /api/v1/admin/courses/lessons/<lesson_id>/reorder - Reorder
"""

# Re-export from the refactored package
from app.api.admin.content_management.courses.content.lessons import *

__all__ = ['lessons']
