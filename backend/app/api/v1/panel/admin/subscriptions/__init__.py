"""Subscriptions Module - Subscription and Billing Management"""

from app.api.v1.panel.admin.subscriptions.core import subscriptions_bp
import app.api.v1.panel.admin.subscriptions.core_part2  # noqa: F401 - registers routes on subscriptions_bp

__all__ = ['subscriptions_bp']
