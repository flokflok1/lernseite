"""
Courses API Package

Feature-based structure (flattened from admin/core/crud structure):
- crud_read.py: Course read operations
- crud_write.py: Course write operations
- crud_stats.py: Course statistics
- chapters_direct.py: Direct chapter operations
- chapters_nested.py: Nested chapter operations
- lessons.py: Lesson operations
- enrollment.py: Course enrollment

Note: Admin course operations (admin/) moved to /admin/courses/

All routes: /api/v1/courses/*
"""

from app.api.v1.courses import (
    crud_read,
    crud_write,
    crud_stats,
    chapters_direct,
    chapters_nested,
    lessons,
    enrollment
)

__all__ = [
    'crud_read',
    'crud_write',
    'crud_stats',
    'chapters_direct',
    'chapters_nested',
    'lessons',
    'enrollment'
]
