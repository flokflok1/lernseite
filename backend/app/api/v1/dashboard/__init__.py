"""
Dashboard API Package

Feature-based structure with role separation (Phase 1 Consolidation).

Structure:
├── admin/                     # Admin dashboards
│   ├── stats/                # Quick statistics endpoints
│   │   └── __init__.py       # /dashboard/admin/stats/* (251 LOC)
│   └── system/               # Full system dashboard views
│       └── __init__.py       # /dashboard/admin/system/* (289 LOC)
│
├── user/                      # User dashboards
│   ├── widgets.py            # Widget registry/management (497 LOC)
│   ├── layouts.py            # Layout management (228 LOC)
│   └── recommendations.py    # Recommendations (213 LOC)
│
└── shared/                    # Shared services
    └── services.py           # Core dashboard services (644 LOC)

Consolidated from:
- api/v1/admin/dashboard/ → dashboard/admin/stats/
- api/v1/dashboard/admin_system.py → dashboard/admin/system/
- api/v1/dashboard/*.py → dashboard/user/*.py

Total: ~2122 LOC (down from split structure)

All routes:
- /api/v1/dashboard/admin/stats/* (admin stats)
- /api/v1/dashboard/admin/system/* (admin system views)
- /api/v1/dashboard/* (user widgets/layouts/recommendations - existing)

Part of: Phase 1 Dashboard Consolidation (Feature-based structure)
"""

from app.api.v1.dashboard import admin, user, shared

# Export user blueprints
from app.api.v1.dashboard.user.widgets import widgets_registry_bp, widgets_instances_bp
from app.api.v1.dashboard.user.layouts import layouts_bp
from app.api.v1.dashboard.user.recommendations import recommendations_bp

__all__ = [
    'admin',
    'user',
    'shared',
    'widgets_registry_bp',
    'widgets_instances_bp',
    'layouts_bp',
    'recommendations_bp'
]
