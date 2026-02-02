"""
LernsystemX Profile API - Barrel Export

Consolidated user profile management endpoints.

Endpoints (16 total across 4 modules):
- Core (4): GET /profile, PUT /profile, DELETE /profile, POST /profile/change-password
- Preferences (4): GET /profile/theme, PATCH /profile/theme, GET /profile/preferences, POST /profile/preferences/reset
- UI Layout (3): GET /profile/preferences/window-sizes, PUT /profile/preferences/window-sizes, DELETE /profile/preferences/window-sizes/<type>
- User Data (5): GET /profile/courses, /activity, /stats, /subscription, /tokens

Architecture: Feature-based splitting with semantic domains
- profile_core.py - Core CRUD operations
- profile_preferences.py - Theme & preference management
- ui_layout_preferences.py - UI layout and workspace configuration
- profile_user_data.py - User data queries

ISO 27001:2013 compliant
Refactored: 2026-01-17 - Fixed naming convention violations (windows → ui_layout_preferences)
"""

from flask import Blueprint

# Import all submodule blueprints
from app.api.v1.profile.core import core_bp as profile_core_bp
from app.api.v1.profile.preferences import preferences_bp as profile_preferences_bp
from app.api.v1.profile.ui_layout_preferences import ui_layout_preferences_bp as profile_ui_layout_bp
from app.api.v1.profile.user_data import user_data_bp as profile_user_data_bp

# Create main blueprint (barrel export)
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

# Register all submodule blueprints as child blueprints
# This ensures all routes from submodules are available under /api/v1/profile/*
profile_bp.register_blueprint(profile_core_bp)
profile_bp.register_blueprint(profile_preferences_bp)
profile_bp.register_blueprint(profile_ui_layout_bp)
profile_bp.register_blueprint(profile_user_data_bp)

# All route handlers are now in submodules:
# - profile_core_bp: Core profile CRUD operations
# - profile_preferences_bp: Theme & general preferences
# - profile_ui_layout_bp: UI layout and workspace configuration
# - profile_user_data_bp: User data queries (courses, activity, stats, subscription, tokens)

__all__ = ['profile_bp']
