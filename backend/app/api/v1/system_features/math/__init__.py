"""
Math Features - System Features

1 Feature:
- toolkit/                # ✅ Math Toolkit - Practice, Reference, Tasks, Admin (IMPLEMENTED)

Status: 1 implemented
"""

# Import implemented features
from app.api.v1.system_features.math.toolkit import (
    admin_bp as math_admin_bp,
    practice_bp as math_practice_bp,
    reference_bp as math_reference_bp,
    tasks_bp as math_tasks_bp
)

__all__ = ['math_admin_bp', 'math_practice_bp', 'math_reference_bp', 'math_tasks_bp']
