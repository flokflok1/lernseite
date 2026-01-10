"""Dashboard Domain - User Journey Routes"""
from .layouts import dashboard_layouts_bp
from .widgets import dashboard_widgets_bp
from .recommendations import dashboard_recommendations_bp
__all__ = ['dashboard_layouts_bp', 'dashboard_widgets_bp', 'dashboard_recommendations_bp']
