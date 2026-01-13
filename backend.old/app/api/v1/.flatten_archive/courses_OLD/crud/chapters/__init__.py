"""
Chapter/Module Management Package

Split from monolithic chapters.py to comply with G04 (max 500 LOC per file).

Modules:
    - nested: Nested chapter endpoints under /courses/:id/chapters
    - direct: Direct chapter endpoints under /chapters/:id

All modules register their routes on the same blueprint for unified routing.
Barrel exports maintain backward compatibility.
"""

# Import nested first (creates blueprint), then direct registers additional routes
from .nested import chapters_bp
from . import direct  # noqa: F401 - imports for side effects (route registration)

__all__ = ['chapters_bp']
