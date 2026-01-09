"""
LernsystemX Users API - Management Package

User management operations split for maintainability:
- crud: List, Create, Delete operations (admin-focused)
- profile: Get, Update operations (user-facing)
- status: Activate/Deactivate operations (admin-only)

Structure:
    crud.py     ~250 lines  - /users list/create/delete
    profile.py  ~214 lines  - /users/<id> get/update
    status.py   ~127 lines  - /users/<id>/activate|deactivate

Refactored from users/core.py (464 lines) - 2026-01-08
Per Developer-Guide-KI Section 10.2 (Max 500 lines per file)
"""

from .crud import users_crud_bp
from .profile import users_profile_bp
from .status import users_status_bp

__all__ = [
    'users_crud_bp',
    'users_profile_bp',
    'users_status_bp',
]
