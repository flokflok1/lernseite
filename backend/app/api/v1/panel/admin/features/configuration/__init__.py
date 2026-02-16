"""
Feature Configuration Admin API Module

Admin endpoints for managing the Enterprise Feature Configuration System:
- Feature CRUD operations
- Progressive rollout management
- A/B testing and experimentation
- Audit logging and change tracking

Moved from: api/v1/admin/feature-configuration/ → api/v1/features/admin/configuration/
Part of: Phase 5 Admin Consolidation

Blueprint Routes:
- /api/v1/admin/feature-configuration/features - Feature CRUD
- /api/v1/admin/feature-configuration/rollout - Rollout management
- /api/v1/admin/feature-configuration/ab-tests - A/B testing
- /api/v1/admin/feature-configuration/audit - Audit logs
"""

from .core import bp as feature_config_core_bp
from .core_part2 import bp as feature_config_core_part2_bp
from .rollout import bp as feature_config_rollout_bp
from .ab_tests import bp as feature_config_ab_tests_bp
from .audit import bp as feature_config_audit_bp

__all__ = [
    'feature_config_core_bp',
    'feature_config_core_part2_bp',
    'feature_config_rollout_bp',
    'feature_config_ab_tests_bp',
    'feature_config_audit_bp',
]
