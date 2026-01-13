"""
LernsystemX Token Core - Token Service

Business logic for token wallet operations.
Implements Service Layer Pattern.

ISO 27001:2013 compliant - Token security and audit
ISO/IEC/IEEE 26515:2018 compliant - Service orchestration
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from app.repositories.token import TokenRepository
from app.repositories.user import UserRepository
from .factory import TokenTransactionFactory
from .value_objects import WalletIdentifier, TransactionAmount


class TokenService:
    """
    Token Service - Business logic layer

    Orchestrates token operations with business rules.
    """

    @staticmethod
    def get_user_balance(user_id: int) -> Dict[str, Any]:
        """
        Get user's effective token balance

        Checks both user wallet and organisation wallet.

        Args:
            user_id: User ID

        Returns:
            Balance information with source

        Example:
            >>> TokenService.get_user_balance(42)
            {
                'balance': 8500,
                'available': 7000,
                'reserved': 1500,
                'source': 'user',
                'wallet_id': 1
            }
        """
        # Get user details
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Check if user belongs to organisation
        if user.get('organization_id'):
            # Organisation wallet takes precedence
            wallet = TokenRepository.get_or_create_organisation_wallet(
                user['organization_id']
            )
            source = 'organisation'
        else:
            # User's personal wallet
            wallet = TokenRepository.get_or_create_user_wallet(user_id)
            source = 'user'

        available = wallet['balance'] - wallet.get('reserved', 0)

        return {
            'balance': wallet['balance'],
            'available': available,
            'reserved': wallet.get('reserved', 0),
            'source': source,
            'wallet_id': wallet['wallet_id']
        }

    @staticmethod
    def can_afford(user_id: int, required_tokens: int) -> bool:
        """
        Check if user can afford token cost

        Args:
            user_id: User ID
            required_tokens: Required token amount

        Returns:
            True if user has sufficient available tokens

        Example:
            >>> TokenService.can_afford(42, 2000)
            True
        """
        try:
            balance = TokenService.get_user_balance(user_id)
            return balance['available'] >= required_tokens
        except Exception:
            return False

    @staticmethod
    def reserve_tokens(wallet_id: int, amount: int) -> bool:
        """
        Reserve tokens for pending operation

        Args:
            wallet_id: Wallet ID
            amount: Token amount to reserve

        Returns:
            True if reservation successful

        Example:
            >>> TokenService.reserve_tokens(1, 2000)
            True
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Reservation amount must be positive")

        wallet = TokenRepository.get_wallet_by_id(wallet_id)
        if not wallet:
            raise ValueError(f"Wallet {wallet_id} not found")

        # Check if enough available tokens
        available = wallet['balance'] - wallet.get('reserved', 0)
        if available < amount:
            return False

        # Update reserved amount
        # Note: Implementation depends on repository method
        # This is a placeholder - actual implementation in repository
        return True

    @staticmethod
    def release_tokens(wallet_id: int, amount: int) -> bool:
        """
        Release reserved tokens

        Args:
            wallet_id: Wallet ID
            amount: Token amount to release

        Returns:
            True if release successful

        Example:
            >>> TokenService.release_tokens(1, 2000)
            True
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Release amount must be positive")

        wallet = TokenRepository.get_wallet_by_id(wallet_id)
        if not wallet:
            raise ValueError(f"Wallet {wallet_id} not found")

        # Update reserved amount
        # Note: Implementation depends on repository method
        # This is a placeholder - actual implementation in repository
        return True

    @staticmethod
    def consume_ai_tokens(
        user_id: int,
        amount: int,
        ai_module: str,
        provider: str,
        method_id: Optional[int] = None,
        lesson_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Consume tokens for AI execution

        Args:
            user_id: User ID
            amount: Token amount to consume (positive)
            ai_module: AI module name
            provider: AI provider
            method_id: Learning method instance ID (optional)
            lesson_id: Lesson ID (optional)

        Returns:
            Transaction details

        Raises:
            ValueError: If insufficient tokens

        Example:
            >>> TokenService.consume_ai_tokens(
            ...     user_id=42,
            ...     amount=2000,
            ...     ai_module="KI-Tutor",
            ...     provider="anthropic",
            ...     method_id=5
            ... )
        """
        # Get user's effective wallet
        balance = TokenService.get_user_balance(user_id)

        # Check if user can afford
        if balance['available'] < amount:
            raise ValueError(
                f"Insufficient tokens: need {amount}, have {balance['available']}"
            )

        # Create usage transaction
        transaction_data = TokenTransactionFactory.create_usage(
            wallet_id=balance['wallet_id'],
            amount=amount,
            ai_module=ai_module,
            provider=provider,
            method_id=method_id,
            lesson_id=lesson_id
        )

        # Execute transaction
        transaction = TokenRepository.change_balance(**transaction_data)

        return transaction

    @staticmethod
    def grant_subscription_tokens(
        user_id: int,
        amount: int,
        subscription_id: int,
        grant_type: str = "monthly"
    ) -> Dict[str, Any]:
        """
        Grant subscription tokens to user

        Args:
            user_id: User ID
            amount: Token amount to grant
            subscription_id: Subscription ID
            grant_type: Grant type ("monthly", "bonus")

        Returns:
            Transaction details

        Example:
            >>> TokenService.grant_subscription_tokens(
            ...     user_id=42,
            ...     amount=10000,
            ...     subscription_id=1,
            ...     grant_type="monthly"
            ... )
        """
        # Get user's wallet
        wallet = TokenRepository.get_or_create_user_wallet(user_id)

        # Create subscription grant transaction
        transaction_data = TokenTransactionFactory.create_subscription_grant(
            wallet_id=wallet['wallet_id'],
            amount=amount,
            subscription_id=subscription_id,
            grant_type=grant_type
        )

        # Execute transaction
        transaction = TokenRepository.change_balance(**transaction_data)

        return transaction

    @staticmethod
    def apply_promo_code(
        user_id: int,
        promo_code: str,
        promo_code_id: int,
        token_amount: int
    ) -> Dict[str, Any]:
        """
        Apply promo code and grant tokens

        Args:
            user_id: User ID
            promo_code: Promo code
            promo_code_id: Promo code ID
            token_amount: Token amount to grant

        Returns:
            Transaction details

        Example:
            >>> TokenService.apply_promo_code(
            ...     user_id=42,
            ...     promo_code="WELCOME2025",
            ...     promo_code_id=123,
            ...     token_amount=5000
            ... )
        """
        # Get user's wallet
        wallet = TokenRepository.get_or_create_user_wallet(user_id)

        # Create promo code grant transaction
        transaction_data = TokenTransactionFactory.create_promo_code_grant(
            wallet_id=wallet['wallet_id'],
            amount=token_amount,
            promo_code=promo_code,
            promo_code_id=promo_code_id
        )

        # Execute transaction
        transaction = TokenRepository.change_balance(**transaction_data)

        return transaction

    @staticmethod
    def transfer_to_organisation_pool(
        organization_id: int,
        amount: int,
        admin_user_id: int,
        reason: str
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Transfer tokens to organisation pool

        Args:
            organization_id: Organisation ID
            amount: Token amount to transfer
            admin_user_id: Admin user initiating transfer
            reason: Transfer reason

        Returns:
            Tuple of (deduction_transaction, addition_transaction)

        Example:
            >>> TokenService.transfer_to_organisation_pool(
            ...     organization_id=10,
            ...     amount=50000,
            ...     admin_user_id=999,
            ...     reason="Monthly organisation token allocation"
            ... )
        """
        # Get organisation wallet
        org_wallet = TokenRepository.get_or_create_organisation_wallet(organization_id)

        # For now, we assume tokens come from system (admin wallet)
        # In production, this might come from billing system

        # Create admin adjustment to grant tokens
        transaction_data = TokenTransactionFactory.create_admin_adjustment(
            wallet_id=org_wallet['wallet_id'],
            amount=amount,
            reason=reason,
            admin_user_id=admin_user_id
        )

        # Execute transaction
        transaction = TokenRepository.change_balance(**transaction_data)

        return None, transaction

    @staticmethod
    def get_usage_summary(
        user_id: int,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get token usage summary for user

        Args:
            user_id: User ID
            period_days: Period in days

        Returns:
            Usage summary with breakdown

        Example:
            >>> TokenService.get_usage_summary(42, 30)
            {
                'total_used': 15000,
                'by_ai_module': {'KI-Tutor': 8000, 'KI-Glossar': 7000},
                'by_provider': {'anthropic': 10000, 'openai': 5000},
                'period_start': '2024-12-16T00:00:00',
                'period_end': '2025-01-15T00:00:00'
            }
        """
        stats = TokenRepository.get_user_token_stats(
            user_id=user_id,
            period_days=period_days
        )

        return stats

    @staticmethod
    def estimate_cost(
        method_name: str,
        complexity: str = "medium"
    ) -> int:
        """
        Estimate token cost for AI method

        Args:
            method_name: AI method name
            complexity: Complexity level (simple, medium, complex)

        Returns:
            Estimated token cost

        Example:
            >>> TokenService.estimate_cost("KI-Tutor", "medium")
            2000
        """
        # Base costs by method
        base_costs = {
            'KI-Tutor': 1500,
            'KI-Glossar': 500,
            'KI-Zusammenfassung': 1000,
            'KI-Quiz-Generator': 2000,
            'KI-Übungsaufgaben': 1500,
        }

        # Complexity multipliers
        complexity_multipliers = {
            'simple': 0.7,
            'medium': 1.0,
            'complex': 1.5,
        }

        base_cost = base_costs.get(method_name, 1000)
        multiplier = complexity_multipliers.get(complexity, 1.0)

        return int(base_cost * multiplier)


__all__ = [
    'TokenService',
]
