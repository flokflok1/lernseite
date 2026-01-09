"""Auth Domain (DDD) - Authentication & Authorization

Complete DDD implementation:
- Domain: User, UserSession entities
- Application: AuthService (business logic)
- Infrastructure: AuthRepository (database access)
- Journeys: API routes (to be added)

Handles:
- User registration & authentication
- Session management (JWT)
- Password operations
- Email verification
- Two-Factor Authentication (2FA)
"""
from src.api.auth.core import *

__all__ = [
    # Entities
    'User',
    'UserSession',
    # Services
    'AuthService',
    # Repositories
    'AuthRepository'
]
