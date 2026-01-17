"""
Admin Settings - Permissions & Roles Module Orchestrator

Refactored from monolithic roles.py into modular components.

Modules:
- roles_core.py: Shared templates and formatting helpers
- roles_crud.py: CRUD operations (list, get, create, update, delete)
- roles_management.py: Feature/permission assignments and system queries
- permission_thresholds.py: Permission threshold configuration

All routes: /api/v1/admin-panel/settings/permissions/*
"""

# Import role management blueprints (split from original roles.py)
from .roles_crud import roles_bp
from .roles_management import roles_mgmt_bp

# Import permission thresholds
from .permission_thresholds import permission_thresholds_bp

# Register blueprints with api_v1
from app.api.v1 import api_v1

api_v1.register_blueprint(roles_bp)
api_v1.register_blueprint(roles_mgmt_bp)
api_v1.register_blueprint(permission_thresholds_bp)

__all__ = ['roles_bp', 'roles_mgmt_bp', 'permission_thresholds_bp']
