"""
Subscriptions API Package

Feature-based structure (flattened from admin/core/plans/user structure):
- admin_management.py: Admin subscription management (115 LOC)
  - From admin/management.py

- factory.py: Subscription factory (504 LOC)
  - From core/factory.py

- value_objects.py: Value object definitions (188 LOC)
  - From core/value_objects.py

- plans_catalog.py: Subscription plans catalog (76 LOC)
  - From plans/catalog.py

- user_billing.py: User billing operations (313 LOC)
  - From user/billing.py

- user_subscriptions.py: User subscription management (120 LOC)
  - From user/subscriptions.py

Total: 1316 LOC across 6 feature files

All routes: /api/v1/subscriptions/*
"""

from app.api.v1.subscriptions import (
    admin_management,
    factory,
    value_objects,
    plans_catalog,
    user_billing,
    user_subscriptions
)

__all__ = [
    'admin_management',
    'factory',
    'value_objects',
    'plans_catalog',
    'user_billing',
    'user_subscriptions'
]
