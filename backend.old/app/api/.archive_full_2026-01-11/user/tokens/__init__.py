"""
LernsystemX Tokens API Package

Token wallet and transaction management endpoints.
Refactored from flat structure into 4 focused packages.

Packages:
    - wallet: Token balance endpoints (~171 lines)
    - transactions: Transaction history (~89 lines)
    - stats: Usage statistics and cost estimation (~154 lines)
    - admin: Admin-only token management (~163 lines)

Structure (all under 500 lines):
    wallet/balance.py        ~171 lines  - /tokens/me, /tokens/organisation/:id
    transactions/history.py  ~89 lines   - /tokens/transactions
    stats/usage.py          ~154 lines   - /tokens/usage, /tokens/estimate
    admin/management.py     ~163 lines   - /tokens/manual-topup, /tokens/stats

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    When this package is imported, blueprints are auto-registered on api_v1.

Endpoints:
    GET    /api/v1/tokens/me                     - Get current user's token balance
    GET    /api/v1/tokens/organisation/:id       - Get organisation token balance (org admin)
    GET    /api/v1/tokens/transactions           - Get token transaction history
    GET    /api/v1/tokens/usage                  - Get token usage analytics
    POST   /api/v1/tokens/estimate               - Estimate AI token cost
    POST   /api/v1/tokens/manual-topup           - Manual token top-up (admin)
    GET    /api/v1/tokens/stats                  - Get global token statistics (admin)

ISO 27001:2013 compliant - Token and billing security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
Refactored: 2026-01-08 per Developer-Guide-KI Section 10
"""

from .wallet import tokens_wallet_bp
from .transactions import tokens_transactions_bp
from .stats import tokens_stats_bp
from .admin import tokens_admin_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    tokens_wallet_bp,
    tokens_transactions_bp,
    tokens_stats_bp,
    tokens_admin_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported from app/api/__init__.py
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    'tokens_wallet_bp',
    'tokens_transactions_bp',
    'tokens_stats_bp',
    'tokens_admin_bp',
    'ALL_BLUEPRINTS',
]
