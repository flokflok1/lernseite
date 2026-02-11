"""
Categories API Module

Provides category management for both admin and public access.

Subdirectories:
- admin/: Admin-only category management (CRUD operations)
- public/: Public category access and hierarchy functionality

All routes: /api/v1/categories/*
"""

# Admin functionality (7 functions + 1 blueprint)
from app.api.v1.categories.admin import (
    create_category,
    update_category,
    delete_category,
    reorder_categories,
    move_category,
    activate_category,
    deactivate_category,
    admin_bp
)

# Public functionality (9 functions + 2 blueprints)
from app.api.v1.categories.public import (
    # Hierarchy
    get_category_tree,
    get_category,
    get_category_breadcrumb,
    get_category_descendants,
    hierarchy_bp,
    # Public routes
    list_categories,
    get_root_categories,
    search_categories,
    get_category_stats,
    get_category_by_path,
    public_bp
)

__all__ = [
    # Admin functions
    'create_category',
    'update_category',
    'delete_category',
    'reorder_categories',
    'move_category',
    'activate_category',
    'deactivate_category',

    # Public hierarchy functions
    'get_category_tree',
    'get_category',
    'get_category_breadcrumb',
    'get_category_descendants',

    # Public route functions
    'list_categories',
    'get_root_categories',
    'search_categories',
    'get_category_stats',
    'get_category_by_path',

    # Blueprints (3 total)
    'admin_bp',
    'hierarchy_bp',
    'public_bp'
]
