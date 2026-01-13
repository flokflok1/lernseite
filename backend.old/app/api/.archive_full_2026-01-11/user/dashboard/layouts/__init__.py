"""
LernsystemX Dashboard Layouts Package

Dashboard layout management (renamed from core.py).

Endpoints:
- GET    /api/v1/dashboard/layout       - Get user's dashboard layout
- PUT    /api/v1/dashboard/layout       - Save user's dashboard layout
- POST   /api/v1/dashboard/layout/reset - Reset layout to default

ISO 27001:2013 compliant - Dashboard layout management
Refactored: 2026-01-08 per Developer-Guide-KI Section 10
"""

from .endpoints import layouts_bp

__all__ = ['layouts_bp']
