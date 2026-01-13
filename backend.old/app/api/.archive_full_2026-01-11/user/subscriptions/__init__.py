"""
LernsystemX Subscriptions API Package

Subscription and plan management endpoints.
Refactored from flat structure into 3 focused packages, with user.py split into two files.

Packages:
    - plans: Public subscription plan listing (~76 lines)
    - user: User subscription info and billing (~128 + 314 = 442 lines split into 2 files)
    - admin: Admin statistics and reporting (~115 lines)

Structure (all under 500 lines per file):
    plans/catalog.py         ~76 lines   - /subscriptions/plans (public)
    user/subscriptions.py   ~128 lines   - /subscriptions/me
    user/billing.py         ~314 lines   - /subscriptions/change, /cancel, /reactivate
    admin/management.py     ~115 lines   - /subscriptions/stats, /expiring (admin only)

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    When this package is imported, blueprints are auto-registered on api_v1.
    Final URLs: /api/v1/subscriptions/...

Refactored: 2026-01-08 per Developer-Guide-KI Section 10
"""

from .plans import subscriptions_plans_bp
from .user import subscriptions_info_bp, subscriptions_billing_bp
from .admin import subscriptions_admin_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    subscriptions_plans_bp,
    subscriptions_info_bp,
    subscriptions_billing_bp,
    subscriptions_admin_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported from app/__init__.py
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    'subscriptions_plans_bp',
    'subscriptions_info_bp',
    'subscriptions_billing_bp',
    'subscriptions_admin_bp',
    'ALL_BLUEPRINTS',
]
