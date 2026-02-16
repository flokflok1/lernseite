"""
Admin Settings - Permissions Module

PHASE B: Roles management removed (replaced with Groups system)

Modules:
- permission_thresholds.py: Permission threshold configuration

All routes: /api/v1/panel/settings/permissions/*
"""

# Import permission thresholds
from .permission_thresholds import permission_thresholds_bp

# Register blueprints with api_v1
from app.api.v1 import api_v1

api_v1.register_blueprint(permission_thresholds_bp)

__all__ = ['permission_thresholds_bp']
