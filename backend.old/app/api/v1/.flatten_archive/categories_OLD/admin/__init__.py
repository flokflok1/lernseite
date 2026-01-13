"""
Category Admin Module

Provides admin-only category management endpoints:
- CRUD operations (create, update, delete)
- Advanced operations (reorder, move, activate, deactivate)
- Admin aliases under /admin/categories for frontend consistency

All endpoints require admin_required authentication.
"""

from flask import Blueprint
from .crud import categories_admin_crud_bp
from .operations import categories_admin_ops_bp

# Create main admin blueprint
categories_admin_bp = Blueprint(
    'categories_admin',
    __name__
)

# Import and re-export route functions for backward compatibility
from .crud import (
    create_category,
    update_category,
    delete_category
)

from .operations import (
    reorder_categories,
    move_category,
    activate_category,
    deactivate_category
)


# ============================================================================
# ADMIN CATEGORY MANAGEMENT ROUTES - ALIASES
# Aliased routes under /admin/categories for consistency with frontend
# ============================================================================

# Create a separate blueprint for admin aliases
categories_admin_alias_bp = Blueprint(
    'categories_admin_alias',
    __name__,
    url_prefix='/admin/categories'
)


@categories_admin_alias_bp.route('', methods=['POST'])
def admin_create_category():
    """Admin: Create category (alias to /categories POST)"""
    return create_category()


@categories_admin_alias_bp.route('/<int:category_id>', methods=['PATCH', 'PUT'])
def admin_update_category(category_id: int):
    """Admin: Update category (alias to /categories/:id PUT)"""
    return update_category(category_id)


@categories_admin_alias_bp.route('/<int:category_id>', methods=['DELETE'])
def admin_delete_category(category_id: int):
    """Admin: Delete category (alias to /categories/:id DELETE)"""
    return delete_category(category_id)


# Import admin_required for aliases
from app.middleware.auth import admin_required

# Apply decorators to alias routes
admin_create_category = admin_required(admin_create_category)
admin_update_category = admin_required(admin_update_category)
admin_delete_category = admin_required(admin_delete_category)


__all__ = [
    'categories_admin_bp',
    'categories_admin_crud_bp',
    'categories_admin_ops_bp',
    'categories_admin_alias_bp',
    'create_category',
    'update_category',
    'delete_category',
    'reorder_categories',
    'move_category',
    'activate_category',
    'deactivate_category'
]
