"""
Courses Admin Module

Admin course management endpoints.

Structure:
- ai_settings.py: AI configuration for courses
- analytics.py: Course analytics

Moved from: api/v1/admin/courses/ → api/v1/courses/admin/
Part of: Phase 3 Courses Consolidation

Routes are registered directly on api_v1 via @api_v1.route() decorators.
"""

# Import modules to register their routes
from . import ai_settings, analytics

__all__ = ['ai_settings', 'analytics']
