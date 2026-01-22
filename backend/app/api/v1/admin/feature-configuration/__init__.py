"""
Feature Configuration Admin API Module

Admin endpoints for managing the Enterprise Feature Configuration System:
- Feature CRUD operations
- Progressive rollout management
- A/B testing and experimentation
- Audit logging and change tracking

This module provides REST API endpoints that consume the Phase 2 service layer:
- app.services.feature_configuration_service
- app.services.feature_configuration_cache
- app.services.feature_configuration_rollout
- app.services.feature_configuration_ab_test

Blueprint Routes:
- /api/v1/admin/feature-configuration/features - Feature CRUD
- /api/v1/admin/feature-configuration/rollout - Rollout management
- /api/v1/admin/feature-configuration/ab-tests - A/B testing
- /api/v1/admin/feature-configuration/audit - Audit logs
"""

from flask import Blueprint

# Import individual route blueprints
from .core import bp as core_bp
from .core_part2 import bp as core_part2_bp
from .rollout import bp as rollout_bp
from .ab_tests import bp as ab_tests_bp
from .audit import bp as audit_bp


def register_blueprints(app):
    """
    Register all feature configuration blueprints with Flask app.

    This function is called during app initialization to register
    all API endpoints for feature configuration management.

    Args:
        app: Flask application instance
    """
    app.register_blueprint(core_bp)
    app.register_blueprint(core_part2_bp)
    app.register_blueprint(rollout_bp)
    app.register_blueprint(ab_tests_bp)
    app.register_blueprint(audit_bp)


# Export blueprints for external registration
__all__ = [
    'core_bp',
    'core_part2_bp',
    'rollout_bp',
    'ab_tests_bp',
    'audit_bp',
    'register_blueprints'
]
