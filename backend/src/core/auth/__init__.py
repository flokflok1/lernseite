"""Auth Domain (DDD) - Authentication & Authorization

Complete DDD implementation:
- Domain: User, UserSession entities
- Application: AuthService (business logic)
- Infrastructure: AuthRepository (database access)
- Journeys: API routes (public authentication flows)

Handles:
- User registration & authentication
- Session management (JWT)
- Password operations
- Email verification
- Two-Factor Authentication (2FA)

Journeys:
- Public: login, register, password reset, 2FA setup
"""
from src.api.auth.core import *
from src.api.auth.journeys import ALL_JOURNEY_BLUEPRINTS

__all__ = [
    # Entities
    'User',
    'UserSession',
    # Services
    'AuthService',
    # Repositories
    'AuthRepository',
    # Journeys (Blueprints)
    'ALL_JOURNEY_BLUEPRINTS',
]
