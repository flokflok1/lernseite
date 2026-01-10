"""
Organisations Domain - Admin Journey Routes

Admin-only organisation management endpoints.

Routes:
- GET/POST /organisations - List/create organisations
- GET/PUT /organisations/:id - Organisation operations
- GET/POST /organisations/:id/users - Member operations

Architecture: Journey-Based (Admin)
Pattern: DDD with Repository Pattern
"""

from .crud import organisations_core_bp
from .members import organisations_members_bp

# All blueprints in this journey
ALL_BLUEPRINTS = [
    organisations_core_bp,
    organisations_members_bp,
]

__all__ = [
    'organisations_core_bp',
    'organisations_members_bp',
    'ALL_BLUEPRINTS',
]
