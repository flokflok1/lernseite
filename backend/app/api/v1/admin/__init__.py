"""
LernsystemX Admin API Module

Refactored: 2026-01-11 - Flat structure matching 05_Backend-Struktur.md
Migrated from deep DDD structure to flat documentation-aligned structure.

Admin Packages:
├── courses/        # Course management (9 modules)
├── ai/             # AI management (14 modules)
├── studio/         # AI Studio
├── assessment/     # Assessment management
├── i18n_sync/      # i18n Translation Synchronization (Phase 6)
├── moderation/     # Moderation panel (future)
├── feature_flags/  # Feature flags (future)
├── user_management/# User management
└── system_operations/ # System settings

Total: ~160 endpoints
"""

# Core Admin Packages (required)
from app.api.v1.admin import courses
from app.api.v1.admin import ai
from app.api.v1.admin import studio
from app.api.v1.admin import assessment
from app.api.v1.admin import i18n_sync

# User Management Package
from app.api.v1.admin import user_management

# System Operations Package
from app.api.v1.admin import system_operations

# Owner-Admin Package
from app.api.v1.admin import owner

# Roles Management Package (Owner-Admin only)
from app.api.v1.admin import roles

# Permission Thresholds Management (Admin+ only, RBAC 2.0)
from app.api.v1.admin import permission_thresholds

# Future Packages (optional, feature-flagged)
try:
    from app.api.v1.admin import moderation
except ImportError:
    moderation = None

try:
    from app.api.v1.admin import feature_flags
except ImportError:
    feature_flags = None

# =============================================================================
# Blueprint Registration for i18n_sync (single module)
# =============================================================================

from app.api.v1.admin.i18n_sync import bp as i18n_sync_bp
from app.api.v1 import api_v1

api_v1.register_blueprint(i18n_sync_bp)

__all__ = [
    # Core packages
    'courses',
    'ai',
    'studio',
    'assessment',
    'i18n_sync',  # i18n Translation Synchronization
    'user_management',
    'system_operations',
    'owner',  # Owner-Admin only
    'roles',  # Roles Management (Owner-Admin only)
    'permission_thresholds',  # Permission Thresholds (Admin+, RBAC 2.0)
    # Future packages
    'moderation',
    'feature_flags',
    # Blueprint exports
    'i18n_sync_bp',
]
