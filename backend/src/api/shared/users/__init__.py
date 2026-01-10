"""Users Domain (DDD) - User Management

Complete DDD implementation:
- Domain: User entity (imported from Auth Domain - Shared Kernel)
- Application: UserService (business logic)
- Infrastructure: UserRepository (database access)
- Journeys: API routes (user journey)

Handles:
- User CRUD operations
- User search & listing
- Profile management
- User statistics

Journeys:
- User: CRUD, profile management
"""
from src.api.users.core import *
from src.api.users.journeys import ALL_JOURNEY_BLUEPRINTS

__all__ = [
    'User',  # From Auth Domain (Shared Kernel)
    'UserService',
    'UserRepository',
    # Journeys (Blueprints)
    'ALL_JOURNEY_BLUEPRINTS',
]
