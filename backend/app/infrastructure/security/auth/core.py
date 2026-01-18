"""
LernsystemX Authentication API - Bridge Module

This file has been refactored into the auth/ package.
All endpoints are now in focused modules under backend/app/api/auth/:

    - login.py: /login, /refresh, /logout, /me
    - register.py: /register, /verify-email
    - password.py: /forgot-password, /reset-password
    - two_factor.py: /2fa/setup, /2fa/verify, /2fa/disable

This bridge module imports and re-exports for backward compatibility.
Blueprints are auto-registered when the auth package is imported.

See: backend/app/api/auth/__init__.py
Refactored: 2026-01-07 per Developer-Guide-KI Section 10
"""

# Import auth package to register all blueprints on api_v1
from app.api.core.auth import (
    auth_login_bp,
    auth_register_bp,
    auth_password_bp,
    auth_2fa_bp,
    ALL_BLUEPRINTS,
)

__all__ = [
    'auth_login_bp',
    'auth_register_bp',
    'auth_password_bp',
    'auth_2fa_bp',
    'ALL_BLUEPRINTS',
]
