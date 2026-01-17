"""User Profile API Module"""
from app.api.v1.profile.routes import profile_bp
from app.api.v1.profile.core import core_bp
from app.api.v1.profile.preferences import preferences_bp
from app.api.v1.profile.user_data import user_data_bp
from app.api.v1.profile.ui_layout_preferences import ui_layout_preferences_bp
__all__ = ['profile_bp', 'core_bp', 'preferences_bp', 'user_data_bp', 'ui_layout_preferences_bp']
