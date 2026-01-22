"""Features Module - Feature Flags and Feature Management

Exports:
- features_bp: Main feature flags and management endpoints
- features_catalog_bp: System Features catalog (25 features with ui_schemas)
"""

from app.api.v1.features.core import features_bp
from app.api.v1.features.catalog import catalog_bp as features_catalog_bp

__all__ = ['features_bp', 'features_catalog_bp']
