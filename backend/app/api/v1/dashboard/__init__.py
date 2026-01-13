"""
Dashboard API Package

Feature-based structure (flattened from admin/core/layouts/recommendations/user/widgets structure):
- widgets.py: Widget registry and instance management (503 LOC)
  - Widget registry endpoints (get available widgets)
  - Widget instance management (add, remove, update position/settings, toggle visibility)
  - Consolidated from widgets/registry.py, widgets/instances.py, widgets/models.py

- layouts.py: Dashboard layout management (228 LOC)
  - From layouts/endpoints.py

- recommendations.py: Dashboard recommendations (213 LOC)
  - From recommendations/endpoints.py

- admin_system.py: Admin system dashboard (294 LOC)
  - From admin/system_dashboard.py

- services.py: Dashboard core services (644 LOC)
  - From core/services.py

Total: 1882 LOC across 5 feature files (down from 2010 LOC in 7 files + subdirectories)

All routes: /api/v1/dashboard/*
"""

from app.api.v1.dashboard import (
    widgets,
    layouts,
    recommendations,
    admin_system,
    services
)

__all__ = [
    'widgets',
    'layouts',
    'recommendations',
    'admin_system',
    'services'
]
