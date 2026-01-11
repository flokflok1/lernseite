"""
Users Domain - Journeys Layer

Journeys organize routes by user type/flow:
- user: User-facing user management (CRUD, profile)
- admin: Admin user management (roles, actions, status) - TODO

Architecture: Journey-Based DDD
Pattern: Blueprints for route organization
"""

from .user.api.routes import ALL_BLUEPRINTS as user_blueprints

# All journey blueprints
ALL_JOURNEY_BLUEPRINTS = [
    *user_blueprints,
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    'user_blueprints',
]
