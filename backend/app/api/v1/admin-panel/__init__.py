"""
Admin API Package

Organized by sidebar navigation structure:
- Settings (AI, System, Permissions, Feature Flags)
- Audit Logs
- Dashboard
- Categories
- Translations
- Billing
- Analytics

All admin routes: /api/v1/admin/*

Note: Blueprints are auto-registered by importing the settings modules.
"""

# Import settings modules (blueprints auto-register on import)
# Use relative imports since package name contains hyphen (admin-panel)
from .settings import ai, permissions

__all__ = ['ai', 'permissions']
