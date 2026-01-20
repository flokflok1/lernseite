"""
Admin API Package

Organized by sidebar navigation structure:
- Feature Configuration (Feature flags, rollouts, A/B tests, audit logs)
- Settings (AI, System, Permissions, Feature Flags)
- Audit Logs
- Dashboard
- Categories
- Translations
- Billing
- Analytics

All admin routes: /api/v1/admin/*

Note: Blueprints are auto-registered by importing the settings modules.
Feature Configuration uses explicit register_blueprints() function.
"""

# Import feature configuration module with blueprint registration function
# Use importlib since subpackage name contains hyphen (feature-configuration)
import importlib
feature_configuration = importlib.import_module('.feature-configuration', package=__name__)

# Import settings modules (blueprints auto-register on import)
from .settings import ai, permissions, feature_flags

__all__ = ['feature_configuration', 'ai', 'permissions', 'feature_flags']
