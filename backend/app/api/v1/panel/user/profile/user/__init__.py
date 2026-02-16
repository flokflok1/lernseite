"""User Profile API — Profile core, data, preferences."""

from .core import core_bp
from .preferences import preferences_bp
from .user_data import user_data_bp
from .ui_layout_preferences import ui_layout_preferences_bp

__all__ = ['core_bp', 'preferences_bp', 'user_data_bp', 'ui_layout_preferences_bp']
