"""
LernsystemX Users API - Admin Package

Administrative user management endpoints moved from admin/users/.

Modules:
    - crud: List users, Get user details (2 endpoints)
    - roles: Change role, Verify creator (2 endpoints)
    - actions: Ban, Unban, Delete, Grant tokens (4 endpoints)

Structure (all under 500 lines):
    crud.py       ~200 lines  - GET /admin/users, GET /admin/users/<id>
    roles.py      ~200 lines  - PUT /admin/users/<id>/role, POST /admin/users/<id>/verify-creator
    actions.py    ~350 lines  - POST /ban, /unban, DELETE, POST /tokens/grant

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    Final URLs: /api/v1/admin/users/...

Endpoints:
    GET    /api/v1/admin/users              - List all users with filters
    GET    /api/v1/admin/users/{user_id}    - Get user details
    PUT    /api/v1/admin/users/{user_id}/role - Change user role
    POST   /api/v1/admin/users/{user_id}/ban - Ban user
    POST   /api/v1/admin/users/{user_id}/unban - Unban user
    POST   /api/v1/admin/users/{user_id}/tokens/grant - Grant tokens
    DELETE /api/v1/admin/users/{user_id}    - Delete user (soft)
    POST   /api/v1/admin/users/{user_id}/verify-creator - Verify creator

DDD Refactoring - 2026-01-08
Consolidated from admin/users/ → users/admin/ per ISO/IEC 26515
"""

from .crud import admin_users_crud_bp
from .roles import admin_users_roles_bp
from .actions import admin_users_actions_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    admin_users_crud_bp,
    admin_users_roles_bp,
    admin_users_actions_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported from app/api/users/__init__.py
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    'admin_users_crud_bp',
    'admin_users_roles_bp',
    'admin_users_actions_bp',
    'ALL_BLUEPRINTS',
]
