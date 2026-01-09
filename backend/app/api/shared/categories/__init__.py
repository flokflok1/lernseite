"""
LernsystemX Category API Package

Flexible hierarchical course categorization (unlimited depth).
Refactored from monolithic categories.py (903 lines) into focused modules.

Modules:
    - public: Public read endpoints (list, search, stats, roots, by-path)
    - hierarchy: Tree structure, breadcrumbs, descendants
    - admin/: Admin management endpoints
        - crud: Create, update, delete operations
        - operations: Move, reorder, activate, deactivate

Structure (all under 250 lines):
    public.py       ~270 lines  - GET /categories, /search, /stats, /roots, /by-path
    hierarchy.py    ~200 lines  - GET /tree, /:id/breadcrumb, /:id/descendants, /:id
    admin/crud.py   ~220 lines  - POST, PUT, DELETE operations
    admin/operations.py ~210 lines - Move, reorder, activate, deactivate

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    When this package is imported, blueprints are auto-registered on api_v1.

Endpoints:
    Public:
        GET    /api/v1/categories           - List all categories (flat)
        GET    /api/v1/categories/tree      - Hierarchical tree structure
        GET    /api/v1/categories/roots     - Get root categories only
        GET    /api/v1/categories/:id       - Get category details
        GET    /api/v1/categories/:id/descendants - Get all descendants
        GET    /api/v1/categories/:id/breadcrumb  - Get category breadcrumb path
        GET    /api/v1/categories/by-path   - Get category by path
        GET    /api/v1/categories/search    - Search categories
        GET    /api/v1/categories/stats     - Get category statistics

    Admin:
        POST   /api/v1/categories           - Create category
        PUT    /api/v1/categories/:id       - Update category
        DELETE /api/v1/categories/:id       - Delete category
        POST   /api/v1/categories/:id/move  - Move category to new parent
        POST   /api/v1/categories/reorder   - Reorder categories
        POST   /api/v1/categories/:id/activate   - Activate category
        POST   /api/v1/categories/:id/deactivate - Deactivate category

    Admin Aliases (for frontend consistency):
        POST   /api/v1/admin/categories           - Create category
        PUT    /api/v1/admin/categories/:id       - Update category
        DELETE /api/v1/admin/categories/:id       - Delete category

ISO 27001:2013 compliant - Category management and access control
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design

Refactored: 2026-01-07 per Developer-Guide-KI Section 10
Updated: 2026-01-08 - Split admin.py (469 LOC) into crud.py + operations.py
"""

from .public import categories_public_bp
from .hierarchy import categories_hierarchy_bp
from .admin.crud import categories_admin_crud_bp
from .admin.operations import categories_admin_ops_bp
from .admin import categories_admin_alias_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    categories_public_bp,
    categories_hierarchy_bp,
    categories_admin_crud_bp,
    categories_admin_ops_bp,
    categories_admin_alias_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported from app/api/__init__.py
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    'categories_public_bp',
    'categories_hierarchy_bp',
    'categories_admin_crud_bp',
    'categories_admin_ops_bp',
    'categories_admin_alias_bp',
    'ALL_BLUEPRINTS',
]
