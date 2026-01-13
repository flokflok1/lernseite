"""
LernsystemX Subscriptions Plans Package

Subscription plan catalog endpoints.

Endpoints:
- GET /api/v1/subscriptions/plans - List all available subscription plans
"""

from .catalog import subscriptions_plans_bp

__all__ = ['subscriptions_plans_bp']
