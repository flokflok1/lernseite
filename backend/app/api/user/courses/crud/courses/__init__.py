"""
Course CRUD Operations Package

Split from monolithic courses.py to comply with G04 (max 500 LOC per file).

Modules:
    - write: POST/PUT/DELETE endpoints for course management (defines blueprint)
    - read: GET endpoints for listing and retrieving courses
    - stats: Course statistics and analytics endpoints

All modules register their routes on the same blueprint for unified routing.
Barrel exports maintain backward compatibility.
"""

# Import order matters: write.py creates the blueprint, then read.py and stats.py register routes
from .write import courses_bp
from . import read  # noqa: F401 - imports for side effects (route registration)
from . import stats  # noqa: F401 - imports for side effects (route registration)

__all__ = ['courses_bp']
