"""
LernsystemX Subscriptions Admin Package

Admin-only subscription management endpoints.

Endpoints:
- GET /api/v1/subscriptions/admin/all - List all subscriptions
- POST /api/v1/subscriptions/admin/cancel/:id - Cancel subscription (admin)
"""

from .management import subscriptions_admin_bp

__all__ = ['subscriptions_admin_bp']
