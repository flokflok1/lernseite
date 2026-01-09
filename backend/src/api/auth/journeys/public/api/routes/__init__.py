"""
Auth Domain - Public Journey Routes

Authentication endpoints accessible to all users.

Routes:
- POST /auth/register - User registration
- POST /auth/login - User login (with optional 2FA)
- POST /auth/refresh - Refresh JWT token
- POST /auth/logout - Logout (revoke token)
- POST /auth/verify-email - Verify email address
- POST /auth/forgot-password - Request password reset
- POST /auth/reset-password - Reset password with token
- POST /auth/2fa/setup - Setup 2FA
- POST /auth/2fa/verify - Verify 2FA code
- POST /auth/2fa/disable - Disable 2FA
- GET /auth/me - Get current user info

Architecture: Journey-Based (Public)
Pattern: DDD with Repository Pattern
Database: PostgreSQL via psycopg3 (direct SQL)
"""

from .login import auth_login_bp
from .register import auth_register_bp
from .password import auth_password_bp
from .two_factor import auth_2fa_bp

# All blueprints in this journey
ALL_BLUEPRINTS = [
    auth_login_bp,
    auth_register_bp,
    auth_password_bp,
    auth_2fa_bp,
]

__all__ = [
    'auth_login_bp',
    'auth_register_bp',
    'auth_password_bp',
    'auth_2fa_bp',
    'ALL_BLUEPRINTS',
]
