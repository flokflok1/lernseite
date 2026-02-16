"""
Courses Public Module

Public course endpoints (core, CRUD, enrollment, publishing).

Structure:
- core.py: Core course operations
- crud.py: Course CRUD
- enrollment.py: Course enrollment
- publishing.py: Course publishing

Part of: Phase 3 Courses Consolidation
"""

from app.api.v1.public.courses import core, crud, enrollment, publishing

__all__ = ['core', 'crud', 'enrollment', 'publishing']
