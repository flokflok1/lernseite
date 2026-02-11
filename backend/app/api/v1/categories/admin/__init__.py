"""
Categories Admin Module

Provides admin category management functionality (CRUD operations).
"""

from app.api.v1.categories.admin.routes import (
    create_category,
    update_category,
    delete_category,
    reorder_categories,
    move_category,
    activate_category,
    deactivate_category,
    admin_bp
)

__all__ = [
    'create_category',
    'update_category',
    'delete_category',
    'reorder_categories',
    'move_category',
    'activate_category',
    'deactivate_category',
    'admin_bp'
]
