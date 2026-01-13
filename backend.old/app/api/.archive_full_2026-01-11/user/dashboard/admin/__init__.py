"""
LernsystemX Dashboard Admin Package

Admin-specific dashboard endpoints for system analytics.

Endpoints:
    - System overview
    - Recent activity
    - User statistics
    - Course statistics
    - AI usage statistics

DDD Pattern - Admin Domain
ISO 27001:2013 compliant
"""

from .system_dashboard import admin_dashboard_bp

__all__ = ['admin_dashboard_bp']
