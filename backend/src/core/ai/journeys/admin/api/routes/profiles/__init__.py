"""
AI Profiles Admin Package (DDD)

Endpoints for AI profile management using DDD patterns:
- Uses AIProfileFactory for profile creation
- Publishes AIProfileUpdatedEvent on changes
- Uses Repository Pattern for persistence

AI Profiles define model preferences and configurations for:
- Learning method model routing
- Default models per category
- Organization-specific overrides
- User-specific preferences

Blueprint:
    - profiles_crud_bp: Profile CRUD operations
"""

from .crud import profiles_crud_bp

__all__ = [
    'profiles_crud_bp'
]
