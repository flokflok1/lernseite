"""
LernsystemX Admin System API Package

Refactored from admin_system.py (1565 LOC) for better maintainability.
All routes remain at /api/v1/admin/...

Modules:
- settings: System settings and environment management (6 endpoints)
- system_info: Version, deprecated endpoints, health (3 endpoints)
- system_stats: User, course, system statistics (3 endpoints)
- audit_logs: Audit log viewing (1 endpoint)
- ai_providers: AI provider management (6 endpoints)
- ai_models: AI model registry and defaults (4 endpoints)
- ai_settings: Global AI settings (2 endpoints)
- roles: Role management (migrated from system package)

Total: 25+ endpoints
Refactored: 2026-01-07 per Developer-Guide-KI Section 10
"""

# CIRCULAR IMPORT FIX (Phase 8g):
# Problem: app.api → admin → admin.system → settings → app.api (CIRCULAR!)
# Solution: Import api_v1 here ONCE, then submodules import from this package
# Submodules changed from: from app.api import api_v1
# To: from app.api.admin.system import api_v1

# Import parent blueprint BEFORE importing submodules
# Import from app.api.BLUEPRINT directly (defined at app/api/__init__.py:25-29)
# This works because api_v1 is defined BEFORE any other imports in app/api/__init__.py
from app.api import api_v1

# Import all route modules to register them with Flask
# Each module imports api_v1 from this package (admin.system), not from app.api
from app.api.admin.system import settings
from app.api.admin.system import system_info
from app.api.admin.system import system_stats
from app.api.admin.system import audit_logs
from app.api.admin.system import ai_providers
from app.api.admin.system import ai_models
from app.api.admin.system import ai_settings
from app.api.admin.system import roles

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
