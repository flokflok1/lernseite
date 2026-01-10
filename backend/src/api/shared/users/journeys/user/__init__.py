"""
Users Domain - User Journey

User-facing user management journeys.

Routes:
- List/create/update/delete users
- Profile management

Architecture: Journey-Based DDD
"""

from .api.routes import ALL_BLUEPRINTS

__all__ = ['ALL_BLUEPRINTS']
