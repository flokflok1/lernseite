"""Tokens Domain - All Journeys"""

from .user import tokens_balance_bp, tokens_history_bp, tokens_usage_bp
from .admin import tokens_admin_bp

ALL_JOURNEY_BLUEPRINTS = [
    # User Journey (7 endpoints)
    tokens_balance_bp,
    tokens_history_bp,
    tokens_usage_bp,
    # Admin Journey (2 endpoints)
    tokens_admin_bp,
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    'tokens_balance_bp',
    'tokens_history_bp',
    'tokens_usage_bp',
    'tokens_admin_bp',
]
