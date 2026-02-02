"""
Token Repository Package

Provides access to token wallet, transaction, and usage data.

Sub-modules:
- wallet: Token wallet CRUD operations
- transactions: Transaction management and balance updates
- analytics: Token usage statistics and reporting
- admin: Admin token management operations
"""

from .wallet import TokenWalletRepository
from .transactions import TokenTransactionRepository
from .analytics import TokenAnalyticsRepository
from .admin import TokenAdminRepository

# Backward compatibility: Export all as TokenRepository for existing code
class TokenRepository:
    """
    Token Repository - Main interface (backward compatible)

    Routes calls to specialized sub-repositories.
    """

    # Wallet methods
    get_or_create_user_wallet = TokenWalletRepository.get_or_create_user_wallet
    get_or_create_organisation_wallet = TokenWalletRepository.get_or_create_organisation_wallet
    get_wallet_by_id = TokenWalletRepository.get_wallet_by_id
    get_wallet_for_user = TokenWalletRepository.get_wallet_for_user
    get_wallet_for_organisation = TokenWalletRepository.get_wallet_for_organisation

    # Transaction methods
    change_balance = TokenTransactionRepository.change_balance
    log_usage_from_ai = TokenTransactionRepository.log_usage_from_ai
    get_transactions = TokenTransactionRepository.get_transactions

    # Analytics methods
    get_user_token_stats = TokenAnalyticsRepository.get_user_token_stats
    get_org_token_stats = TokenAnalyticsRepository.get_org_token_stats
    get_global_token_stats = TokenAnalyticsRepository.get_global_token_stats

    # Admin methods
    admin_grant_tokens = TokenAdminRepository.admin_grant_tokens




class TokenRepository(
    TokenWalletRepository,
    TokenTransactionRepository,
    TokenAdminRepository,
    TokenAnalyticsRepository
):
    """
    Unified TokenRepository combining all functionality
    This class uses multiple inheritance to aggregate methods from specialized modules.
    """
    pass


__all__ = [
    'TokenRepository',
    'TokenWalletRepository',
    'TokenTransactionRepository',
    'TokenAnalyticsRepository',
    'TokenAdminRepository',
]
