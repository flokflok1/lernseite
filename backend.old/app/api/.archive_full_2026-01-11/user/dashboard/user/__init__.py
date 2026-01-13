"""
LernsystemX Dashboard User Package

User-facing dashboard endpoints:
    - layouts/: Dashboard layout management
    - widgets/: Widget registry and instances
    - recommendations/: KI-powered recommendations

Re-exports from existing sub-packages for backward compatibility.

DDD Pattern - User Domain
ISO 27001:2013 compliant
"""

# Import existing blueprints from parent directory
# These are already organized and work correctly
from ..layouts import layouts_bp
from ..widgets import widgets_registry_bp, widgets_instances_bp
from ..recommendations import recommendations_bp

# Export all user-facing blueprints
__all__ = [
    'layouts_bp',
    'widgets_registry_bp',
    'widgets_instances_bp',
    'recommendations_bp',
]
