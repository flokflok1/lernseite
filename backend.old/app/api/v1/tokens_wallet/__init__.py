"""
Tokens Wallet API Package

Feature-based structure (flattened from admin/core/stats/transactions/wallet structure):
- admin_management.py: Admin wallet management (169 LOC)
  - From admin/management.py

- factory.py: Wallet factory (392 LOC)
  - From core/factory.py

- services.py: Wallet services (428 LOC)
  - From core/services.py

- value_objects.py: Value object definitions (174 LOC)
  - From core/value_objects.py

- stats_usage.py: Token usage statistics (160 LOC)
  - From stats/usage.py

- transactions_history.py: Transaction history (95 LOC)
  - From transactions/history.py

- wallet_balance.py: Wallet balance operations (177 LOC)
  - From wallet/balance.py

Total: 1595 LOC across 7 feature files

All routes: /api/v1/tokens/*
"""

from app.api.v1.tokens_wallet import (
    admin_management,
    factory,
    services,
    value_objects,
    stats_usage,
    transactions_history,
    wallet_balance
)

__all__ = [
    'admin_management',
    'factory',
    'services',
    'value_objects',
    'stats_usage',
    'transactions_history',
    'wallet_balance'
]
