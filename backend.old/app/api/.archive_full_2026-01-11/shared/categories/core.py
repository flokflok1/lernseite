"""
LernsystemX Category API - Bridge Module

DEPRECATED: This file is a bridge module for backward compatibility.
All functionality has been moved to the categories/ package.

The actual implementation is in:
    - categories/public.py    - Public read endpoints
    - categories/hierarchy.py - Tree, breadcrumbs, descendants
    - categories/admin.py     - Admin CRUD & management

Refactored: 2026-01-07 per Developer-Guide-KI Section 10
Original: 903 lines -> 3 modules (~850 lines total, all under 500 LOC)

Import this module to register all category routes on api_v1.
"""

# Import the package to trigger blueprint registration
from app.api.shared.categories.core import (
    categories_public_bp,
    categories_hierarchy_bp,
    categories_admin_bp,
    ALL_BLUEPRINTS,
)

# Re-export for backward compatibility
__all__ = [
    'categories_public_bp',
    'categories_hierarchy_bp',
    'categories_admin_bp',
    'ALL_BLUEPRINTS',
]
