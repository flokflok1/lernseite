"""
Admin System Operations Package

Feature-based structure (flattened from settings/system subdirectories).

Modules:
- settings: System settings and environment management (324 LOC)
- system_info: Version, deprecated endpoints, health (279 LOC)
- system_stats: User, course, system statistics (214 LOC)
- audit_logs: Audit log viewing (153 LOC)
- ai_providers: AI provider management (467 LOC)
- ai_models: AI model registry and defaults (402 LOC)
- ai_settings: Global AI settings (133 LOC)
- roles: Role management (359 LOC)

Total: 2331 LOC across 8 feature files (down from 2655 LOC with duplicate removed)

Cleanup:
- Removed settings/ directory (contained duplicate of system/settings.py)
- Flattened system/ subdirectory to package root
- Migration status: COMPLETED (was IN PROGRESS)

All routes: /api/v1/admin/system/*
Refactored: 2026-01-11 - Flattened to feature-based structure
"""

# CIRCULAR IMPORT FIX:
# Import api_v1 here ONCE, then submodules import from this package
from app.api import api_v1

# Import all route modules to register them with Flask
# Modules now import api_v1 from this package (admin.system_operations), not from app.api
from app.api.v1.admin.system_operations import settings
from app.api.v1.admin.system_operations import system_info
from app.api.v1.admin.system_operations import system_stats
from app.api.v1.admin.system_operations import audit_logs
from app.api.v1.admin.system_operations import ai_providers
from app.api.v1.admin.system_operations import ai_models
from app.api.v1.admin.system_operations import ai_settings
from app.api.v1.admin.system_operations import roles

__all__ = [
    'api_v1',  # Re-export for submodules
    'settings',
    'system_info',
    'system_stats',
    'audit_logs',
    'ai_providers',
    'ai_models',
    'ai_settings',
    'roles',
]
