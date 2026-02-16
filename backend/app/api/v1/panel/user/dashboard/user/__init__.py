"""
Dashboard User Module

User dashboard endpoints (widgets, layouts, recommendations).

Structure:
- widgets.py: Widget registry and instance management
- layouts.py: Dashboard layout management
- recommendations.py: Dashboard recommendations

Part of: Phase 1 Dashboard Consolidation (Feature-based structure)
"""

from . import widgets, layouts, recommendations

__all__ = ['widgets', 'layouts', 'recommendations']
