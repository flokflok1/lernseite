"""
LernsystemX API Package

RESTful API endpoints organized by ISO/IEC 26515 + DDD principles.

Refactored: 2026-01-11 - Flat structure matching 05_Backend-Struktur.md
All endpoints now under /api/v1/ with flat organization.

Package Structure:
└── v1/                  # API Version 1 (flat structure)
    ├── auth.py          # Authentication
    ├── users.py         # User management
    ├── courses.py       # Courses
    ├── /dashboard/      # Dashboard
    ├── /admin/          # Admin API
    ├── /social/         # Social (feature-flagged)
    ├── /community/      # Community
    └── /messaging/      # Messaging (feature-flagged)

Uses:
- Flask Blueprints for modular routing
- Pydantic for request/response validation
- JWT for authentication
- RBAC for authorization
- Repository Pattern (no ORM)

ISO/IEC/IEEE 26515:2018 compliant - Functional organization
"""

from flask import Blueprint

# Create API blueprint (version 1)
api_v1 = Blueprint(
    'api_v1',
    __name__,
    url_prefix='/api/v1'
)

# =============================================================================
# Import v1 package after blueprint creation to avoid circular imports
# Refactored 2026-01-11: Flat structure under /api/v1/
# =============================================================================

# Import v1 package (contains all API endpoints)
from app.api import v1

# Register Social/Messaging/Community blueprints from v1/ (if available)
if hasattr(v1, 'social') and v1.social:
    try:
        for bp in [v1.social.posts_bp, v1.social.feed_bp, v1.social.follow_bp, v1.social.likes_bp, v1.social.comments_bp]:
            api_v1.register_blueprint(bp)
    except Exception:
        pass  # Social feature not fully implemented yet

if hasattr(v1, 'messaging') and v1.messaging:
    try:
        for bp in [v1.messaging.dm_bp, v1.messaging.group_chat_bp]:
            api_v1.register_blueprint(bp)
    except Exception:
        pass  # Messaging feature not fully implemented yet

if hasattr(v1, 'community') and v1.community:
    try:
        for bp in [v1.community.forums_bp, v1.community.groups_bp]:
            api_v1.register_blueprint(bp)
    except Exception:
        pass  # Community feature not fully implemented yet

__all__ = ['api_v1', 'v1']
