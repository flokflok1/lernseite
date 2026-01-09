"""
LernsystemX Profile Subscription Package

User subscription information endpoints.

Endpoints:
- GET /api/v1/profile/subscription - Get subscription details
"""

from .info import profile_subscription_bp

__all__ = ['profile_subscription_bp']
