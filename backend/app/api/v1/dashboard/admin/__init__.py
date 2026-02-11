"""
Dashboard Admin Module

Admin dashboard endpoints (stats + system views).

Structure:
- stats/: Quick statistics endpoints (/dashboard/admin/stats/*)
- system/: Full system dashboard views (/dashboard/admin/system/*)

Part of: Phase 1 Dashboard Consolidation (Feature-based structure)
"""

from app.api.v1.dashboard.admin import stats, system

__all__ = ['stats', 'system']
