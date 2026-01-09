"""
LernsystemX API Package

RESTful API endpoints organized by ISO/IEC 26515 + DDD principles.

Refactored: 2026-01-08 - Complete API restructuring
Structure parallel to Frontend (components/)

Package Structure:
├── admin/           # Admin-only endpoints (roles, courses, AI, analytics)
├── user/            # User-facing endpoints (courses, lessons, dashboard, exams)
├── shared/          # Role-independent (categories, feedback, organisations, media)
├── core/            # Framework-core (auth, health, i18n, deprecation)
└── system_features/ # System-Features (AI, agents, math, tutor)

Uses:
- Flask Blueprints for modular routing
- Pydantic for request/response validation
- JWT for authentication (core/auth/)
- RBAC for authorization
- Repository Pattern (no ORM)

ISO/IEC/IEEE 26515:2018 compliant - Functional organization
Domain-Driven Design (DDD) - Bounded contexts
"""

from flask import Blueprint

# Create API blueprint (version 1)
api_v1 = Blueprint(
    'api_v1',
    __name__,
    url_prefix='/api/v1'
)

# =============================================================================
# Import packages after blueprint creation to avoid circular imports
# Refactored 2026-01-08: ISO + DDD compliant parallel structure
# =============================================================================

# Core Framework (Health, Auth, i18n)
try:
    from app.api import core
    from app.api.core import health, deprecation
except ImportError as e:
    print(f"Warning: Core package import failed: {e}")
    core = None

# Admin Package
try:
    from app.api import admin
except ImportError as e:
    print(f"Warning: Admin package import failed: {e}")
    admin = None

# User Package
try:
    from app.api import user
except ImportError as e:
    print(f"Warning: User package import failed: {e}")
    user = None

# Shared Package
try:
    from app.api import shared
except ImportError as e:
    print(f"Warning: Shared package import failed: {e}")
    shared = None

# System Features Package
try:
    from app.api import system_features
except ImportError as e:
    print(f"Warning: System Features package import failed: {e}")
    system_features = None

__all__ = ['api_v1', 'core', 'admin', 'user', 'shared', 'system_features']
