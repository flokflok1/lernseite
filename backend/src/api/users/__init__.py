"""Users Domain (DDD) - User Management

Complete DDD implementation:
- Domain: User entity (imported from Auth Domain - Shared Kernel)
- Application: UserService (business logic)
- Infrastructure: UserRepository (database access)
- Journeys: API routes (to be added)

Handles:
- User CRUD operations
- User search & listing
- Profile management
- User statistics
"""
from src.api.users.core import *

__all__ = [
    'User',  # From Auth Domain (Shared Kernel)
    'UserService',
    'UserRepository'
]
