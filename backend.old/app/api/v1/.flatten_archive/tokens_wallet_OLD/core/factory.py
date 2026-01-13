"""
LernsystemX Token Core - Transaction Factory

Factory for creating token transactions with business rules.
Implements Domain-Driven Design (DDD) Factory Pattern.

ISO 27001:2013 compliant - Secure transaction creation
ISO/IEC/IEEE 26515:2018 compliant - Standardized creation interface
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .value_objects import (
    TransactionType,
    ReferenceType,
    TransactionAmount,
    WalletIdentifier
)


class TokenTransactionFactory:
    """
    Factory for creating token transactions with business rules.

    Ensures:
    - Correct amount signs (positive for income, negative for expenses)
    - Required metadata is present
    - Transaction types are valid
    - Audit trail information
    """

    @staticmethod
    def create_purchase(
        wallet_id: int,
        amount: int,
        payment_id: str,
        price: float,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """
        Create token purchase transaction

        Args:
            wallet_id: Wallet ID
            amount: Number of tokens purchased (must be positive)
            payment_id: Payment provider transaction ID
            price: Price paid in currency
            currency: Currency code (default: EUR)

        Returns:
            Transaction data dictionary

        Example:
            >>> TokenTransactionFactory.create_purchase(
            ...     wallet_id=1,
            ...     amount=10000,
            ...     payment_id="pay_123xyz",
            ...     price=9.99
            ... )
        """
        # Validate amount is positive
        amount_obj = TransactionAmount.income(amount)

        return {
            'wallet_id': wallet_id,
            'amount': amount_obj.value,
            'reason': TransactionType.PURCHASE.value,
            'reference_type': ReferenceType.PAYMENT.value,
            'reference_id': None,  # External payment ID in meta
            'meta': {
                'payment_id': payment_id,
                'price': price,
                'currency': currency,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    def create_usage(
        wallet_id: int,
        amount: int,
        ai_module: str,
        provider: str,
        method_id: Optional[int] = None,
        lesson_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create AI token usage transaction

        Args:
            wallet_id: Wallet ID
            amount: Number of tokens consumed (will be made negative)
            ai_module: AI module name (e.g., "KI-Tutor", "KI-Glossar")
            provider: AI provider (e.g., "openai", "anthropic")
            method_id: Learning method instance ID (optional)
            lesson_id: Lesson ID (optional)

        Returns:
            Transaction data dictionary

        Example:
            >>> TokenTransactionFactory.create_usage(
            ...     wallet_id=1,
            ...     amount=2000,
            ...     ai_module="KI-Tutor",
            ...     provider="anthropic",
            ...     method_id=5
            ... )
        """
        # Ensure amount is negative for expense
        if amount > 0:
            amount = -amount

        amount_obj = TransactionAmount.expense(amount)

        meta = {
            'ai_module': ai_module,
            'provider': provider,
            'timestamp': datetime.utcnow().isoformat()
        }

        if method_id:
            meta['method_id'] = method_id

        if lesson_id:
            meta['lesson_id'] = lesson_id

        return {
            'wallet_id': wallet_id,
            'amount': amount_obj.value,
            'reason': TransactionType.AI_EXECUTION.value,
            'reference_type': ReferenceType.AI_EXECUTION.value,
            'reference_id': method_id,
            'meta': meta
        }

    @staticmethod
    def create_transfer(
        from_wallet_id: int,
        to_wallet_id: int,
        amount: int,
        reason: str,
        admin_user_id: Optional[int] = None
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Create token transfer between wallets (two transactions)

        Args:
            from_wallet_id: Source wallet ID
            to_wallet_id: Target wallet ID
            amount: Number of tokens to transfer (must be positive)
            reason: Transfer reason
            admin_user_id: Admin user initiating transfer (optional)

        Returns:
            Tuple of (deduction_transaction, addition_transaction)

        Example:
            >>> deduction, addition = TokenTransactionFactory.create_transfer(
            ...     from_wallet_id=1,
            ...     to_wallet_id=2,
            ...     amount=5000,
            ...     reason="Organisation token pool distribution"
            ... )
        """
        # Validate amount is positive
        amount_obj = TransactionAmount.income(amount)

        transfer_meta = {
            'transfer_from': from_wallet_id,
            'transfer_to': to_wallet_id,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }

        if admin_user_id:
            transfer_meta['admin_user_id'] = admin_user_id

        # Deduction from source wallet
        deduction = {
            'wallet_id': from_wallet_id,
            'amount': -amount_obj.value,
            'reason': TransactionType.ADMIN_ADJUSTMENT.value,
            'reference_type': 'token_transfer',
            'reference_id': to_wallet_id,
            'meta': {**transfer_meta, 'transfer_type': 'deduction'}
        }

        # Addition to target wallet
        addition = {
            'wallet_id': to_wallet_id,
            'amount': amount_obj.value,
            'reason': TransactionType.ADMIN_ADJUSTMENT.value,
            'reference_type': 'token_transfer',
            'reference_id': from_wallet_id,
            'meta': {**transfer_meta, 'transfer_type': 'addition'}
        }

        return deduction, addition

    @staticmethod
    def create_admin_adjustment(
        wallet_id: int,
        amount: int,
        reason: str,
        admin_user_id: int,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create admin token adjustment transaction

        Args:
            wallet_id: Wallet ID
            amount: Token amount (positive = grant, negative = deduct)
            reason: Adjustment reason
            admin_user_id: Admin user ID making adjustment
            notes: Optional notes explaining adjustment

        Returns:
            Transaction data dictionary

        Example:
            >>> TokenTransactionFactory.create_admin_adjustment(
            ...     wallet_id=1,
            ...     amount=5000,
            ...     reason="Support compensation for service outage",
            ...     admin_user_id=999
            ... )
        """
        # Validate amount is not zero
        amount_obj = TransactionAmount(value=amount)

        meta = {
            'admin_user_id': admin_user_id,
            'admin_reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }

        if notes:
            meta['notes'] = notes

        return {
            'wallet_id': wallet_id,
            'amount': amount_obj.value,
            'reason': TransactionType.ADMIN_ADJUSTMENT.value,
            'reference_type': ReferenceType.ADMIN_TOPUP.value,
            'reference_id': None,
            'meta': meta
        }

    @staticmethod
    def create_subscription_grant(
        wallet_id: int,
        amount: int,
        subscription_id: int,
        grant_type: str = "monthly"
    ) -> Dict[str, Any]:
        """
        Create subscription token grant transaction

        Args:
            wallet_id: Wallet ID
            amount: Number of tokens granted (must be positive)
            subscription_id: Subscription ID
            grant_type: Grant type ("monthly", "bonus")

        Returns:
            Transaction data dictionary

        Example:
            >>> TokenTransactionFactory.create_subscription_grant(
            ...     wallet_id=1,
            ...     amount=10000,
            ...     subscription_id=42,
            ...     grant_type="monthly"
            ... )
        """
        # Validate amount is positive
        amount_obj = TransactionAmount.income(amount)

        # Determine transaction type based on grant_type
        if grant_type == "monthly":
            transaction_type = TransactionType.SUBSCRIPTION_MONTHLY_GRANT
        elif grant_type == "bonus":
            transaction_type = TransactionType.SUBSCRIPTION_BONUS
        else:
            raise ValueError(f"Invalid grant_type: {grant_type}")

        return {
            'wallet_id': wallet_id,
            'amount': amount_obj.value,
            'reason': transaction_type.value,
            'reference_type': ReferenceType.SUBSCRIPTION.value,
            'reference_id': subscription_id,
            'meta': {
                'subscription_id': subscription_id,
                'grant_type': grant_type,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    def create_promo_code_grant(
        wallet_id: int,
        amount: int,
        promo_code: str,
        promo_code_id: int
    ) -> Dict[str, Any]:
        """
        Create promo code token grant transaction

        Args:
            wallet_id: Wallet ID
            amount: Number of tokens granted (must be positive)
            promo_code: Promo code used
            promo_code_id: Promo code ID

        Returns:
            Transaction data dictionary

        Example:
            >>> TokenTransactionFactory.create_promo_code_grant(
            ...     wallet_id=1,
            ...     amount=5000,
            ...     promo_code="WELCOME2025",
            ...     promo_code_id=123
            ... )
        """
        # Validate amount is positive
        amount_obj = TransactionAmount.income(amount)

        return {
            'wallet_id': wallet_id,
            'amount': amount_obj.value,
            'reason': TransactionType.PROMO_CODE.value,
            'reference_type': ReferenceType.PROMO_CODE.value,
            'reference_id': promo_code_id,
            'meta': {
                'promo_code': promo_code,
                'promo_code_id': promo_code_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    def create_reward(
        wallet_id: int,
        amount: int,
        reward_type: str,
        reward_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create gamification reward transaction

        Args:
            wallet_id: Wallet ID
            amount: Number of tokens rewarded (must be positive)
            reward_type: Reward type (e.g., "quest_complete", "achievement")
            reward_data: Additional reward data

        Returns:
            Transaction data dictionary

        Example:
            >>> TokenTransactionFactory.create_reward(
            ...     wallet_id=1,
            ...     amount=500,
            ...     reward_type="quest_complete",
            ...     reward_data={'quest_id': 42, 'quest_name': 'Daily Login'}
            ... )
        """
        # Validate amount is positive
        amount_obj = TransactionAmount.income(amount)

        return {
            'wallet_id': wallet_id,
            'amount': amount_obj.value,
            'reason': TransactionType.REWARD.value,
            'reference_type': ReferenceType.GAMIFICATION_REWARD.value,
            'reference_id': reward_data.get('quest_id') or reward_data.get('achievement_id'),
            'meta': {
                'reward_type': reward_type,
                **reward_data,
                'timestamp': datetime.utcnow().isoformat()
            }
        }


__all__ = [
    'TokenTransactionFactory',
]
