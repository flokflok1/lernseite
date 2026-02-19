"""User Profile API — Profile endpoints."""

from flask import Blueprint

from .core import core_bp
from .preferences import preferences_bp
from .user_data import user_data_bp
from .ui_layout_preferences import ui_layout_preferences_bp

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')
profile_bp.register_blueprint(core_bp)
profile_bp.register_blueprint(preferences_bp)
profile_bp.register_blueprint(user_data_bp)
profile_bp.register_blueprint(ui_layout_preferences_bp)

__all__ = ['profile_bp']
