"""
LernsystemX Panel API v1

Configuration endpoints for system administration.
Panel API - Configuration ONLY, NO execution logic.

Blueprints:
- runner_modes: Runner mode CRUD and feature mappings
- lm_type_compatibility: Learning method type to runner mode compatibility
- system_features: System features read + minimal edit
"""

from flask import Blueprint

# Create parent blueprint for panel routes
panel_bp = Blueprint('panel', __name__, url_prefix='/panel')

# Import child blueprints
from app.api.v1.panel.runner_modes import bp as runner_modes_bp
from app.api.v1.panel.lm_type_compatibility import bp as lm_type_compatibility_bp
from app.api.v1.panel.system_features import bp as system_features_bp

__all__ = [
    'panel_bp',
    'runner_modes_bp',
    'lm_type_compatibility_bp',
    'system_features_bp'
]
