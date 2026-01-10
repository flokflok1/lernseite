"""
Categories Domain - Public Journey Routes

Public read-only routes for category browsing and hierarchy navigation.

Routes:
- browse.py: List, roots, search, stats, by-path (5 endpoints)
- hierarchy.py: Tree, get, breadcrumb, descendants (4 endpoints)

Total: 9 public endpoints
"""

from .browse import categories_browse_bp
from .hierarchy import categories_hierarchy_bp

__all__ = [
    'categories_browse_bp',
    'categories_hierarchy_bp',
]
