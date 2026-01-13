"""
Organisations API Package

Feature-based structure (flattened role-based admin/core/user, kept analytics feature):

**Flat files (from role-based structure):**
- admin_crud.py: Admin organisation CRUD (331 LOC)
  - From admin/crud.py

- admin_members.py: Admin organisation members (201 LOC)
  - From admin/members.py

- factory.py: Organisation factory (390 LOC)
  - From core/factory.py

- services.py: Organisation services (503 LOC)
  - From core/services.py

- value_objects.py: Value object definitions (317 LOC)
  - From core/value_objects.py

**Feature subdirectory (TRUE FEATURE - kept separate):**
- analytics/: Organisation analytics and reporting (629 LOC)
  - stats.py (103 LOC)
  - reports.py (253 LOC)
  - time_series.py (273 LOC)

**Helpers:**
- _helpers.py: Shared helper functions

Total: 2371 LOC (flat files: 1742 LOC, feature subdir: 629 LOC)

Architecture Pattern:
- Role-based subdirectories (admin/, core/, user/) → Flattened
- Feature subdirectory (analytics/) → Kept (multi-file feature)

All routes: /api/v1/organisations/*
"""

from app.api.v1.organisations import (
    admin_crud,
    admin_members,
    factory,
    services,
    value_objects,
    analytics
)

__all__ = [
    'admin_crud',
    'admin_members',
    'factory',
    'services',
    'value_objects',
    'analytics'
]
