"""
LernsystemX API Package

RESTful API endpoints organized by ISO/IEC 26515 + DDD principles.

Refactored: 2026-01-11 - Flat structure matching 05_Backend-Struktur.md
All endpoints now under /api/v1/ with flat organisation.

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

ISO/IEC/IEEE 26515:2018 compliant - Functional organisation
"""

# =============================================================================
# Import v1 package which contains the api_v1 blueprint
# Refactored 2026-01-11: Flat structure under /api/v1/
# Refactored 2026-01-12: Import api_v1 from v1 package (not create duplicate!)
# =============================================================================

# Import v1 package (contains all API endpoints and api_v1 blueprint)
from app.api import v1
from app.api.v1 import api_v1  # Import the ONLY api_v1 blueprint

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

# Register Owner-Admin blueprint
if hasattr(v1, 'admin') and hasattr(v1.admin, 'owner'):
    try:
        api_v1.register_blueprint(v1.admin.owner.owner_bp)
    except Exception:
        pass  # Owner not available

# PHASE B: Roles Management removed (replaced with Groups system)
# No longer registering roles_bp - core.roles table was deleted

# Register Permission Thresholds blueprint (Admin+, RBAC 2.0)
if hasattr(v1, 'admin') and hasattr(v1.admin, 'permission_thresholds'):
    try:
        api_v1.register_blueprint(v1.admin.permission_thresholds.permission_thresholds_bp)
    except Exception:
        pass  # Permission thresholds not available

__all__ = ['api_v1', 'v1']
