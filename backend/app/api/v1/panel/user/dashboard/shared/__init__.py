"""
Dashboard Shared Module

Shared services used by both admin and user dashboards.

Structure:
- services.py: Layout and widget services
- services_part2.py: Recommendation service

Part of: Phase 1 Dashboard Consolidation (Feature-based structure)
"""

from app.api.v1.panel.user.dashboard.shared import services
from app.api.v1.panel.user.dashboard.shared import services_part2

__all__ = ['services', 'services_part2']
