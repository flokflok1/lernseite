"""
Organisations Domain - Admin Journey

Admin-only organisation management journeys.

Routes:
- CRUD operations (list, create, get, update)
- Member management (list users, assign user)

Architecture: Journey-Based DDD
"""

from .api.routes import ALL_BLUEPRINTS

__all__ = ['ALL_BLUEPRINTS']
