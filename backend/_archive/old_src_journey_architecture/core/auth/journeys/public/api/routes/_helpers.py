"""
Auth Domain - Shared Route Helpers

Common imports and utilities shared across auth route modules.

Imports from:
- Flask (request, jsonify, Blueprint)
- Flask-JWT-Extended (JWT functions)
- Pydantic (validation)
- DDD Services/Repositories (from src.api.auth.core.*)
- Legacy imports (app.*) for compatibility until full migration
"""

# Flask imports
from flask import request, jsonify

# JWT imports
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

# Pydantic validation
from pydantic import ValidationError

# Standard library
from datetime import timedelta

# DDD Auth Domain (NEW - src structure)
from src.api.auth.core.application.services.auth_service import AuthService
from src.api.auth.core.infrastructure.repositories.auth_repository import AuthRepository

# Legacy imports (app structure) - TODO: migrate these to src/ structure
from app.models.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    EmailVerification,
    TwoFactorSetup,
    TwoFactorDisable,
    PasswordReset
)
from app.middleware.auth import token_required, get_current_user
from app.security import BruteForceProtection
from app.services.audit_service import AuditService
from setup.admin_setup import AdminSetup

# TODO: Create these in src/ structure:
# - src.api.users.core.infrastructure.repositories.user_repository (UserRepository)
# - src.shared.models.user (Pydantic models)
# - src.shared.middleware.auth (token_required, get_current_user)
# - src.shared.security.brute_force (BruteForceProtection)
# - src.shared.services.audit (AuditService)
# - src.shared.services.two_factor (2FA logic from AdminSetup)

__all__ = [
    # Flask
    'request',
    'jsonify',
    # JWT
    'create_access_token',
    'create_refresh_token',
    'jwt_required',
    'get_jwt_identity',
    'get_jwt',
    # Pydantic
    'ValidationError',
    # Datetime
    'timedelta',
    # DDD Auth Domain (NEW)
    'AuthService',
    'AuthRepository',
    # Models (Legacy)
    'UserCreate',
    'UserLogin',
    'UserResponse',
    'TokenResponse',
    'EmailVerification',
    'TwoFactorSetup',
    'TwoFactorDisable',
    'PasswordReset',
    # Middleware (Legacy)
    'token_required',
    'get_current_user',
    # Security (Legacy)
    'BruteForceProtection',
    # Services (Legacy)
    'AuditService',
    # Setup (Legacy)
    'AdminSetup',
]
