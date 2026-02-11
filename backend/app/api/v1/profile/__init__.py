"""
User Profile API Package

User profile management, preferences, and UI layout settings.

Structure:
- user/ - User profile endpoints (core, preferences, user data, UI layout)

Consolidated from: profile/ root files (Batch 5, Phase 7)

Endpoints (User - @token_required):
- GET/PUT /profile - Core profile management
- GET/PUT /profile/preferences - User preferences
- GET/PUT /profile/user-data - Custom user data
- GET/PUT /profile/ui-layout-preferences - UI layout settings

All endpoints require authentication (@token_required)
"""

from flask import Blueprint

# Import blueprints from user module
from app.api.v1.profile.user.core import core_bp as profile_core_bp
from app.api.v1.profile.user.preferences import preferences_bp as profile_preferences_bp
from app.api.v1.profile.user.user_data import user_data_bp as profile_user_data_bp
from app.api.v1.profile.user.ui_layout_preferences import ui_layout_preferences_bp as profile_ui_layout_bp

# Create main blueprint (barrel export)
profile_bp = Blueprint('profile', __name__, url_prefix='')

# Register all child blueprints
profile_bp.register_blueprint(profile_core_bp)
profile_bp.register_blueprint(profile_preferences_bp)
profile_bp.register_blueprint(profile_user_data_bp)
profile_bp.register_blueprint(profile_ui_layout_bp)

__all__ = ['profile_bp']
