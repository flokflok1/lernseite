"""
Categories API Package

Feature-based structure (flattened from admin/core structure):
- admin_crud.py: Admin CRUD operations
- admin_operations.py: Admin operations (activate, deactivate, reorder)
- hierarchy.py: Category hierarchy navigation
- public.py: Public category listing

All routes: /api/v1/categories/*
"""

from app.api.v1.categories import admin_crud, admin_operations, hierarchy, public

__all__ = ['admin_crud', 'admin_operations', 'hierarchy', 'public']
