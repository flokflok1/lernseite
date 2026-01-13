"""
LernsystemX Authentication API Package

Authentication endpoints:
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/login - User login (with optional 2FA)
- POST /api/v1/auth/refresh - Refresh JWT token
- POST /api/v1/auth/logout - Logout (revoke token)
- POST /api/v1/auth/verify-email - Verify email address
- POST /api/v1/auth/forgot-password - Request password reset
- POST /api/v1/auth/reset-password - Reset password with token
- POST /api/v1/auth/2fa/setup - Setup 2FA
- POST /api/v1/auth/2fa/verify - Verify 2FA code
- POST /api/v1/auth/2fa/disable - Disable 2FA
- GET /api/v1/auth/me - Get current user info

ISO 27001:2013 compliant - Authentication and access control

Refactored from monolithic auth.py (771 lines) into focused modules.

Modules:
    - login: Login, refresh, logout, current user endpoints
    - register: User registration, email verification
    - password: Forgot/reset password endpoints
    - two_factor: 2FA setup, verify, disable endpoints

Structure (all under 500 lines):
    _helpers.py     ~65 lines   - Shared imports and utilities
    login.py       ~250 lines   - /login, /refresh, /logout, /me
    register.py    ~120 lines   - /register, /verify-email
    password.py    ~100 lines   - /forgot-password, /reset-password
    two_factor.py  ~220 lines   - /2fa/setup, /2fa/verify, /2fa/disable

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    When this package is imported, blueprints are auto-registered on api_v1.
    Final URLs: /api/v1/auth/...

Refactored: 2026-01-07 per Developer-Guide-KI Section 10
"""

from .login import auth_login_bp
from .register import auth_register_bp
from .password import auth_password_bp
from .two_factor import auth_2fa_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    auth_login_bp,
    auth_register_bp,
    auth_password_bp,
    auth_2fa_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported from app/api/__init__.py
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    'auth_login_bp',
    'auth_register_bp',
    'auth_password_bp',
    'auth_2fa_bp',
    'ALL_BLUEPRINTS',
]
