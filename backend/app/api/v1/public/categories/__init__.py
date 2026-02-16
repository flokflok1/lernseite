"""
Categories Public Module

Provides public category access and hierarchy functionality.
"""

# Category hierarchy
from .hierarchy import (
    get_category_tree,
    get_category,
    get_category_breadcrumb,
    get_category_descendants,
    hierarchy_bp
)

# Public routes
from .routes import (
    list_categories,
    get_root_categories,
    search_categories,
    get_category_stats,
    get_category_by_path,
    public_bp
)

__all__ = [
    # Hierarchy
    'get_category_tree',
    'get_category',
    'get_category_breadcrumb',
    'get_category_descendants',
    'hierarchy_bp',

    # Public routes
    'list_categories',
    'get_root_categories',
    'search_categories',
    'get_category_stats',
    'get_category_by_path',
    'public_bp'
]
