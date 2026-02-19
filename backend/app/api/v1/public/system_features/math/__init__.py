"""
Math Features - System Features

1 Feature:
- toolkit/                # ✅ Math Toolkit - Practice, Reference, Tasks, Admin (IMPLEMENTED)

Status: 1 implemented
"""

# Import implemented features
from app.api.v1.public.system_features.math.toolkit import (
    practice_bp as math_practice_bp,
    reference_bp as math_reference_bp,
    tasks_bp as math_tasks_bp
)

# NOTE: math_admin_bp moved to app.api.v1.panel.admin.math_toolkit (Phase 1 Task 2)

__all__ = ['math_practice_bp', 'math_reference_bp', 'math_tasks_bp']
