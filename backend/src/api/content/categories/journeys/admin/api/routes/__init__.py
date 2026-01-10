"""
Categories Domain - Admin Journey Routes

Admin-only category management endpoints.

Routes:
- crud.py: Create, Update, Delete (3 endpoints)
- operations.py: Reorder, Move, Activate, Deactivate (4 endpoints)

Total: 7 admin endpoints

Architecture: Journey-Based (Admin)
Pattern: DDD with Repository Pattern
"""

from .crud import categories_admin_crud_bp
from .operations import categories_admin_ops_bp

# All blueprints in this journey
ALL_BLUEPRINTS = [
    categories_admin_crud_bp,
    categories_admin_ops_bp,
]

__all__ = [
    'categories_admin_crud_bp',
    'categories_admin_ops_bp',
    'ALL_BLUEPRINTS',
]
