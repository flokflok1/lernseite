"""
LernsystemX Users API Package

Comprehensive user domain API following Domain-Driven Design (DDD) principles.

DDD Structure:
    core/               - Domain core (Value Objects, Factory, Services)
        value_objects.py   - UserRole, AccountStatus, UserType, PermissionScope
        factory.py         - UserFactory for aggregate creation
        services.py        - UserService for domain logic

    admin/              - Administrative user management (8 endpoints)
        crud.py            - List users, Get details (2 endpoints)
        roles.py           - Change role, Verify creator (2 endpoints)
        actions.py         - Ban, Unban, Delete, Grant tokens (4 endpoints)

    user/               - User-facing endpoints (5 endpoints)
        crud.py            - List, Create, Delete (3 endpoints)
        profile.py         - Get, Update (2 endpoints)
        status.py          - Activate, Deactivate (2 endpoints - admin)

    search/             - Search and statistics (2 endpoints)
        queries.py         - Search users, Get stats

Structure Overview:
    Total LOC: ~3500 lines
    - core/: ~450 lines (DDD patterns)
    - admin/: ~750 lines (8 endpoints)
    - user/: ~600 lines (5 endpoints)
    - search/: ~110 lines (2 endpoints)

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.

    Admin URLs: /api/v1/admin/users/...
    User URLs: /api/v1/users/...

Endpoints Summary:
    Admin (8):
        GET    /api/v1/admin/users                     - List all users
        GET    /api/v1/admin/users/{id}                - Get user details
        PUT    /api/v1/admin/users/{id}/role           - Change role
        POST   /api/v1/admin/users/{id}/ban            - Ban user
        POST   /api/v1/admin/users/{id}/unban          - Unban user
        POST   /api/v1/admin/users/{id}/tokens/grant   - Grant tokens
        DELETE /api/v1/admin/users/{id}                - Delete user
        POST   /api/v1/admin/users/{id}/verify-creator - Verify creator

    User (5):
        GET    /api/v1/users                - List users (filtered by role)
        POST   /api/v1/users                - Create user (admin)
        GET    /api/v1/users/{id}           - Get user
        PUT    /api/v1/users/{id}           - Update user
        DELETE /api/v1/users/{id}           - Delete user
        POST   /api/v1/users/{id}/activate  - Activate user (admin)
        POST   /api/v1/users/{id}/deactivate - Deactivate user (admin)

    Search (2):
        GET    /api/v1/users/search - Search users
        GET    /api/v1/users/stats  - User statistics

DDD Refactoring - 2026-01-08
Consolidated from admin/users/ + users/management/
Per ISO/IEC 26515 role-based organization + DDD patterns
Based on Developer-Guide-KI Section 1 (DDD Factory Pattern)
"""

# Core domain exports
from .core import (
    UserRole,
    AccountStatus,
    UserType,
    PermissionScope,
    UserFactory,
    UserService,
)

# Admin endpoints
from .admin import (
    admin_users_crud_bp,
    admin_users_roles_bp,
    admin_users_actions_bp,
)

# User endpoints
from .user import (
    users_crud_bp,
    users_profile_bp,
    users_status_bp,
)

# Search endpoints
from .search import (
    users_search_bp,
)

# All blueprints in this package
ALL_BLUEPRINTS = [
    # Admin endpoints (registered in admin/__init__.py)
    admin_users_crud_bp,
    admin_users_roles_bp,
    admin_users_actions_bp,
    # User endpoints
    users_crud_bp,
    users_profile_bp,
    users_status_bp,
    # Search endpoints
    users_search_bp,
]

# Register user-facing blueprints on api_v1
# Admin blueprints are already registered in admin/__init__.py
from app.api import api_v1

for bp in [users_crud_bp, users_profile_bp, users_status_bp, users_search_bp]:
    api_v1.register_blueprint(bp)


# Export all
__all__ = [
    # Core domain
    'UserRole',
    'AccountStatus',
    'UserType',
    'PermissionScope',
    'UserFactory',
    'UserService',
    # Admin blueprints
    'admin_users_crud_bp',
    'admin_users_roles_bp',
    'admin_users_actions_bp',
    # User blueprints
    'users_crud_bp',
    'users_profile_bp',
    'users_status_bp',
    # Search blueprints
    'users_search_bp',
    # Collection
    'ALL_BLUEPRINTS',
]
