"""
i18n API - Unified Internationalization Endpoints (Barrel Export)

This module re-exports all i18n API blueprints from their specialized modules
for backward compatibility and convenient registration.

Split modules:
- i18n_public.py - Public and authenticated user endpoints
- i18n_admin.py - Admin-only endpoints
"""

from app.api.v1.i18n_public import bp as i18n_public_bp
from app.api.v1.i18n_admin import bp as i18n_admin_bp

# For backward compatibility, export both blueprints
__all__ = ['i18n_public_bp', 'i18n_admin_bp']
