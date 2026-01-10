"""
Users Domain - Shared Route Helpers (User Journey)

Common imports and utilities shared across user route modules.
"""

# Flask imports
from flask import request, jsonify, g

# Pydantic validation
from pydantic import ValidationError

# DDD Users Domain (Shared Kernel - imports from Auth)
from src.api.auth.core.domain.entities.user import User

# DDD Users Domain (NEW - src structure)
from src.api.users.core.infrastructure.repositories.user_repository import UserRepository
from src.api.users.core.application.services.user_service import UserService

# Legacy imports (app structure) - TODO: migrate these to src/ structure
from app.models.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)
from app.middleware.auth import (
    token_required,
    admin_required,
    role_required,
    can_manage_user,
    get_accessible_roles
)

__all__ = [
    # Flask
    'request',
    'jsonify',
    'g',
    # Pydantic
    'ValidationError',
    # DDD Entities
    'User',
    # DDD Services/Repos
    'UserRepository',
    'UserService',
    # Models (Legacy)
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    'UserListResponse',
    # Middleware (Legacy)
    'token_required',
    'admin_required',
    'role_required',
    'can_manage_user',
    'get_accessible_roles',
]
