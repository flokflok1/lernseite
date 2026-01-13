"""
LernsystemX Users API - User Package

User-facing endpoints for profile and account management.
Renamed from management/ to user/ per ISO/IEC 26515 role-based organization.

Modules:
    - crud: List, Create, Delete operations (250 lines)
    - profile: Get, Update operations (214 lines)
    - status: Activate/Deactivate operations (127 lines)

Structure (all under 300 lines):
    crud.py     ~250 lines  - /users list/create/delete
    profile.py  ~214 lines  - /users/<id> get/update
    status.py   ~127 lines  - /users/<id>/activate|deactivate

Route Registration:
    All routes are registered on api_v1 blueprint.
    Final URLs: /api/v1/users/...

DDD Refactoring - 2026-01-08
Renamed from management/ to user/ for clarity
"""

from .crud import users_crud_bp
from .profile import users_profile_bp
from .status import users_status_bp

__all__ = [
    'users_crud_bp',
    'users_profile_bp',
    'users_status_bp',
]
