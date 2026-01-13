"""
Feedback API Package

Feature-based structure (flattened from admin/core/user structure):
- submit.py: User feedback submission
- admin_management.py: Admin feedback management

All routes: /api/v1/feedback/*
"""

from app.api.v1.feedback import submit, admin_management

__all__ = ['submit', 'admin_management']
