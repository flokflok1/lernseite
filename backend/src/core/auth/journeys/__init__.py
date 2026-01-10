"""
Auth Domain - Journeys Layer

Journeys organize routes by user type/flow:
- public: Unauthenticated user journeys (login, register, password reset)

Architecture: Journey-Based DDD
Pattern: Blueprints for route organization
"""

from .public.api.routes import ALL_BLUEPRINTS as public_blueprints

# All journey blueprints
ALL_JOURNEY_BLUEPRINTS = [
    *public_blueprints,
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    'public_blueprints',
]
