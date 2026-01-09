"""
Auth Domain - Public Journey

Public authentication journeys accessible to all users (unauthenticated).

Routes:
- User registration
- User login
- Password reset
- Email verification
- 2FA management

Architecture: Journey-Based DDD
"""

from .api.routes import ALL_BLUEPRINTS

__all__ = ['ALL_BLUEPRINTS']
