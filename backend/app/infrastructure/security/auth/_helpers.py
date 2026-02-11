"""
LernsystemX Auth API - Shared Helpers

Common imports and utilities shared across auth modules.
"""

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from pydantic import ValidationError
from datetime import timedelta

from app.domain.models.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    EmailVerification,
    TwoFactorSetup,
    TwoFactorDisable,
    PasswordReset
)
from app.infrastructure.persistence.repositories.user import UserRepository
from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.security import BruteForceProtection
from app.application.services.system.audit.service import AuditService
from app.setup.admin_setup import AdminSetup


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
    # Models
    'UserCreate',
    'UserLogin',
    'UserResponse',
    'TokenResponse',
    'EmailVerification',
    'TwoFactorSetup',
    'TwoFactorDisable',
    'PasswordReset',
    # Repositories
    'UserRepository',
    # Middleware
    'token_required',
    'get_current_user',
    # Security
    'BruteForceProtection',
    # Services
    'AuditService',
    # Setup
    'AdminSetup',
]
