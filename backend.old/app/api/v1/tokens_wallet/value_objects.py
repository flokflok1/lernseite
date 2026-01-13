"""
LernsystemX Token Core - Value Objects

Domain value objects for token transactions.
Implements Domain-Driven Design (DDD) Value Object Pattern.

ISO 27001:2013 compliant - Immutable transaction types
ISO/IEC/IEEE 26515:2018 compliant - Type safety
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass


class TransactionType(str, Enum):
    """
    Token transaction types (immutable)

    Categories:
    - INCOME: Tokens added to wallet
    - EXPENSE: Tokens deducted from wallet
    - ADMIN: Administrative adjustments
    """

    # Income types
    PURCHASE = "purchase"
    MANUAL_TOPUP = "manual_topup"
    SUBSCRIPTION_BONUS = "subscription_bonus"
    SUBSCRIPTION_MONTHLY_GRANT = "subscription_monthly_grant"
    PROMO_CODE = "promo_code"
    REWARD = "reward"
    REFUND = "refund"

    # Expense types
    AI_EXECUTION = "ai_execution"

    # Admin types
    ADMIN_ADJUSTMENT = "admin_adjustment"

    @classmethod
    def is_income(cls, transaction_type: str) -> bool:
        """Check if transaction type is income"""
        income_types = {
            cls.PURCHASE,
            cls.MANUAL_TOPUP,
            cls.SUBSCRIPTION_BONUS,
            cls.SUBSCRIPTION_MONTHLY_GRANT,
            cls.PROMO_CODE,
            cls.REWARD,
            cls.REFUND,
        }
        return transaction_type in income_types

    @classmethod
    def is_expense(cls, transaction_type: str) -> bool:
        """Check if transaction type is expense"""
        return transaction_type == cls.AI_EXECUTION

    @classmethod
    def is_admin(cls, transaction_type: str) -> bool:
        """Check if transaction type is admin adjustment"""
        return transaction_type == cls.ADMIN_ADJUSTMENT


class ReferenceType(str, Enum):
    """
    Transaction reference types

    Links transactions to their originating entities.
    """
    AI_EXECUTION = "ai_execution"
    PAYMENT = "payment"
    ADMIN_TOPUP = "admin_topup"
    SUBSCRIPTION = "subscription"
    PROMO_CODE = "promo_code"
    GAMIFICATION_REWARD = "gamification_reward"


@dataclass(frozen=True)
class TransactionAmount:
    """
    Value object for transaction amounts

    Ensures:
    - Positive amounts for income
    - Negative amounts for expenses
    - Non-zero amounts
    """
    value: int

    def __post_init__(self):
        """Validate amount"""
        if self.value == 0:
            raise ValueError("Transaction amount cannot be zero")

        # Store absolute value for comparison
        object.__setattr__(self, '_abs_value', abs(self.value))

    @classmethod
    def income(cls, amount: int) -> 'TransactionAmount':
        """Create income amount (positive)"""
        if amount <= 0:
            raise ValueError(f"Income amount must be positive, got {amount}")
        return cls(value=amount)

    @classmethod
    def expense(cls, amount: int) -> 'TransactionAmount':
        """Create expense amount (negative)"""
        if amount >= 0:
            raise ValueError(f"Expense amount must be negative, got {amount}")
        return cls(value=amount)

    @property
    def is_income(self) -> bool:
        """Check if amount is income"""
        return self.value > 0

    @property
    def is_expense(self) -> bool:
        """Check if amount is expense"""
        return self.value < 0

    @property
    def absolute(self) -> int:
        """Get absolute value"""
        return self._abs_value


@dataclass(frozen=True)
class WalletIdentifier:
    """
    Value object for wallet identification

    Ensures either user_id OR organization_id is set, but not both.
    """
    user_id: Optional[int] = None
    organization_id: Optional[int] = None

    def __post_init__(self):
        """Validate wallet identifier"""
        if self.user_id and self.organization_id:
            raise ValueError("Wallet cannot belong to both user and organisation")

        if not self.user_id and not self.organization_id:
            raise ValueError("Wallet must belong to either user or organisation")

    @classmethod
    def for_user(cls, user_id: int) -> 'WalletIdentifier':
        """Create wallet identifier for user"""
        return cls(user_id=user_id, organization_id=None)

    @classmethod
    def for_organization(cls, organization_id: int) -> 'WalletIdentifier':
        """Create wallet identifier for organisation"""
        return cls(user_id=None, organization_id=organization_id)

    @property
    def owner_type(self) -> str:
        """Get owner type (user or organisation)"""
        return "user" if self.user_id else "organisation"

    @property
    def owner_id(self) -> int:
        """Get owner ID"""
        return self.user_id if self.user_id else self.organization_id


__all__ = [
    'TransactionType',
    'ReferenceType',
    'TransactionAmount',
    'WalletIdentifier',
]
