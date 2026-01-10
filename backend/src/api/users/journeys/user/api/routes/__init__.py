"""
Users Domain - User Journey Routes

User-facing user management endpoints.

Routes:
- GET/POST /users - List/create users
- GET/PUT/DELETE /users/:id - User operations

Architecture: Journey-Based (User)
Pattern: DDD with Repository Pattern
"""

from .crud import users_crud_bp
from .profile import users_profile_bp

# All blueprints in this journey
ALL_BLUEPRINTS = [
    users_crud_bp,
    users_profile_bp,
]

__all__ = [
    'users_crud_bp',
    'users_profile_bp',
    'ALL_BLUEPRINTS',
]
