"""
Course CRUD Operations Package

Handles course, chapter, and lesson CRUD operations.
Refactored from monolithic modules into focused sub-modules.

G04 Compliance:
    - courses.py (525 LOC) → courses/ package (3 modules: read, write, stats)
    - chapters.py (520 LOC) → chapters/ package (2 modules: nested, direct)
    - lessons.py (443 LOC) → stays as single file (within limits)

Modules:
    - courses: Course CRUD operations (split into read/write/stats)
    - chapters: Chapter CRUD operations (split into nested/direct)
    - lessons: Lesson CRUD operations (single file)

Backward compatibility maintained through barrel exports.
"""

from .courses import courses_bp
from .chapters import chapters_bp
from .lessons import lessons_bp

__all__ = [
    'courses_bp',
    'chapters_bp',
    'lessons_bp',
]
