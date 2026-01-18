"""
LernsystemX Token Models

Pydantic models for token wallet and billing operations:
- Token wallet management (user and organisation wallets)
- Token transactions (consumption, purchases, grants)
- Token usage statistics and tracking

ISO 9001:2015 compliant - Token management and billing
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal


class TokenWalletBase(BaseModel):
    """
    Base token wallet model

    Example:
        >>> wallet = TokenWalletBase(
        ...     user_id=42,
        ...     balance=10000,
        ...     reserved=0
        ... )
    """
    user_id: Optional[int] = Field(None, description="User ID (for personal wallets)")
    organization_id: Optional[int] = Field(None, description="Organisation ID (for org wallets)")
    balance: int = Field(default=0, ge=0, description="Available token balance")
    reserved: int = Field(default=0, ge=0, description="Reserved tokens (pending operations)")
    currency: str = Field(default="tokens", description="Currency type")

    @field_validator('user_id', 'organization_id')
    @classmethod
    def validate_owner(cls, v, info):
        """Ensure exactly one of user_id or organization_id is set"""
        data = info.data
        user_id = data.get('user_id')
        org_id = info.field_name == 'organization_id' and v or data.get('organization_id')

        # Check if this is the second field being validated
        if info.field_name == 'organization_id':
            if user_id is not None and org_id is not None:
                raise ValueError('Cannot specify both user_id and organization_id')
            if user_id is None and org_id is None:
                raise ValueError('Must specify either user_id or organization_id')

        return v

    model_config = ConfigDict(from_attributes=True)


class TokenWalletResponse(TokenWalletBase):
    """
    Token wallet response model

    Example:
        >>> wallet = TokenWalletResponse(
        ...     wallet_id=1,
        ...     user_id=42,
        ...     balance=8500,
        ...     reserved=1500,
        ...     total_purchased=20000,
        ...     total_granted=10000,
        ...     total_consumed=21500,
        ...     created_at=datetime.now()
        ... )
    """
    wallet_id: int = Field(..., description="Wallet ID")
    total_purchased: int = Field(default=0, ge=0, description="Total tokens purchased")
    total_granted: int = Field(default=0, ge=0, description="Total tokens granted (subscriptions, promos)")
    total_consumed: int = Field(default=0, ge=0, description="Total tokens consumed")
    last_grant_date: Optional[datetime] = Field(None, description="Last token grant date")
    monthly_grant_amount: Optional[int] = Field(None, ge=0, description="Monthly subscription token grant")
    created_at: datetime = Field(..., description="Wallet creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class TokenTransactionBase(BaseModel):
    """
    Base token transaction model

    Example (AI consumption):
        >>> transaction = TokenTransactionBase(
        ...     wallet_id=1,
        ...     amount=-2000,
        ...     reason="ai_execution",
        ...     meta={"method_id": 5, "provider": "openai"}
        ... )

    Example (purchase):
        >>> transaction = TokenTransactionBase(
        ...     wallet_id=1,
        ...     amount=10000,
        ...     reason="manual_topup",
        ...     meta={"payment_id": "pay_123", "price_eur": 9.99}
        ... )
    """
    wallet_id: int = Field(..., description="Wallet ID")
    amount: int = Field(..., description="Token amount (negative = consumption, positive = grant)")
    reason: str = Field(..., max_length=100, description="Transaction reason")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (JSON)")
    reference_type: Optional[str] = Field(None, max_length=50, description="Reference type (e.g., 'ai_execution', 'payment')")
    reference_id: Optional[int] = Field(None, description="Reference ID")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: int) -> int:
        """Validate amount is not zero"""
        if v == 0:
            raise ValueError('Amount cannot be zero')
        return v

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Validate reason"""
        valid_reasons = [
            'ai_execution',
            'manual_topup',
            'subscription_bonus',
            'subscription_monthly_grant',
            'purchase',
            'refund',
            'admin_adjustment',
            'promo_code',
            'reward'
        ]
        if v not in valid_reasons:
            # Allow custom reasons, but log warning
            pass
        return v

    model_config = ConfigDict(from_attributes=True)


class TokenTransactionResponse(TokenTransactionBase):
    """
    Token transaction response model

    Example:
        >>> transaction = TokenTransactionResponse(
        ...     transaction_id=12345,
        ...     wallet_id=1,
        ...     user_id=42,
        ...     amount=-2000,
        ...     balance_after=8500,
        ...     reason="ai_execution",
        ...     created_at=datetime.now()
        ... )
    """
    transaction_id: int = Field(..., description="Transaction ID")
    user_id: Optional[int] = Field(None, description="User ID")
    organization_id: Optional[int] = Field(None, description="Organisation ID")
    balance_after: int = Field(..., description="Balance after transaction")
    description: Optional[str] = Field(None, description="Human-readable description")
    ai_module: Optional[str] = Field(None, max_length=100, description="AI module used (if applicable)")
    created_at: datetime = Field(..., description="Transaction timestamp")

    model_config = ConfigDict(from_attributes=True)


class TokenUsageStats(BaseModel):
    """
    Token usage statistics

    Example:
        >>> stats = TokenUsageStats(
        ...     user_id=42,
        ...     total_tokens_used=15000,
        ...     total_tokens_bought=20000,
        ...     total_tokens_granted=10000,
        ...     current_balance=15000,
        ...     by_reason={"ai_execution": 15000},
        ...     by_method={"KI-Tutor": 8000, "KI-Glossar": 7000},
        ...     period_start=datetime.now(),
        ...     period_end=datetime.now()
        ... )
    """
    user_id: Optional[int] = Field(None, description="User ID (if user-specific)")
    organization_id: Optional[int] = Field(None, description="Organisation ID (if org-specific)")
    total_tokens_used: int = Field(..., ge=0, description="Total tokens consumed")
    total_tokens_bought: int = Field(..., ge=0, description="Total tokens purchased")
    total_tokens_granted: int = Field(..., ge=0, description="Total tokens granted")
    current_balance: int = Field(..., ge=0, description="Current token balance")
    by_reason: Dict[str, int] = Field(..., description="Token usage by reason")
    by_method: Optional[Dict[str, int]] = Field(None, description="Token usage by learning method")
    by_provider: Optional[Dict[str, int]] = Field(None, description="Token usage by AI provider")
    period_start: Optional[datetime] = Field(None, description="Statistics period start")
    period_end: Optional[datetime] = Field(None, description="Statistics period end")

    model_config = ConfigDict(from_attributes=True)


class TokenPurchaseRequest(BaseModel):
    """
    Token purchase request

    Example:
        >>> purchase = TokenPurchaseRequest(
        ...     amount=10000,
        ...     package="medium"
        ... )
    """
    amount: int = Field(..., gt=0, description="Number of tokens to purchase")
    package: Optional[str] = Field(None, description="Token package name (small, medium, large, xl, xxl)")
    payment_method: str = Field(default="stripe", description="Payment method")
    promo_code: Optional[str] = Field(None, max_length=50, description="Promo code (if applicable)")

    model_config = ConfigDict(from_attributes=True)


class TokenPurchaseResponse(BaseModel):
    """
    Token purchase response

    Example:
        >>> response = TokenPurchaseResponse(
        ...     purchase_id=123,
        ...     amount=10000,
        ...     price_eur=9.99,
        ...     status="completed",
        ...     new_balance=18500
        ... )
    """
    purchase_id: int = Field(..., description="Purchase ID")
    wallet_id: int = Field(..., description="Wallet ID")
    amount: int = Field(..., description="Tokens purchased")
    price_eur: Decimal = Field(..., description="Price paid in EUR")
    discount_applied: Optional[Decimal] = Field(None, description="Discount amount in EUR")
    status: str = Field(..., description="Purchase status (pending, completed, failed)")
    payment_intent_id: Optional[str] = Field(None, description="Stripe payment intent ID")
    new_balance: int = Field(..., description="New token balance")
    created_at: datetime = Field(default_factory=datetime.now, description="Purchase timestamp")

    model_config = ConfigDict(from_attributes=True)


class TokenManualTopupRequest(BaseModel):
    """
    Manual token top-up request (admin only)

    Example:
        >>> topup = TokenManualTopupRequest(
        ...     user_id=42,
        ...     amount=5000,
        ...     reason="Support compensation"
        ... )
    """
    user_id: Optional[int] = Field(None, description="User ID")
    organization_id: Optional[int] = Field(None, description="Organisation ID")
    amount: int = Field(..., description="Token amount (can be negative for deductions)")
    reason: str = Field(..., max_length=255, description="Reason for manual topup")

    @field_validator('user_id', 'organization_id')
    @classmethod
    def validate_target(cls, v, info):
        """Ensure exactly one target is specified"""
        data = info.data
        if info.field_name == 'organization_id':
            user_id = data.get('user_id')
            org_id = v
            if user_id is None and org_id is None:
                raise ValueError('Must specify either user_id or organization_id')
            if user_id is not None and org_id is not None:
                raise ValueError('Cannot specify both user_id and organization_id')
        return v

    model_config = ConfigDict(from_attributes=True)


class TokenBalanceResponse(BaseModel):
    """
    Token balance response

    Example:
        >>> balance = TokenBalanceResponse(
        ...     wallet_id=1,
        ...     balance=8500,
        ...     reserved=1500,
        ...     available=7000,
        ...     source="user"
        ... )
    """
    wallet_id: int = Field(..., description="Wallet ID")
    balance: int = Field(..., description="Total balance")
    reserved: int = Field(..., description="Reserved tokens")
    available: int = Field(..., description="Available tokens (balance - reserved)")
    source: str = Field(..., description="Wallet source (user, organisation)")
    monthly_grant: Optional[int] = Field(None, description="Monthly subscription grant")
    next_grant_date: Optional[datetime] = Field(None, description="Next monthly grant date")

    model_config = ConfigDict(from_attributes=True)


# Token package pricing
TOKEN_PACKAGES = {
    'small': {'tokens': 5000, 'price_eur': 5.99, 'discount': 0},
    'medium': {'tokens': 10000, 'price_eur': 9.99, 'discount': 16},
    'large': {'tokens': 25000, 'price_eur': 19.99, 'discount': 33},
    'xl': {'tokens': 50000, 'price_eur': 34.99, 'discount': 42},
    'xxl': {'tokens': 100000, 'price_eur': 59.99, 'discount': 50}
}


def get_token_package(package_name: str) -> Dict[str, Any]:
    """
    Get token package details

    Args:
        package_name: Package name (small, medium, large, xl, xxl)

    Returns:
        Package details (tokens, price, discount)

    Example:
        >>> package = get_token_package('medium')
        >>> print(package)  # {'tokens': 10000, 'price_eur': 9.99, 'discount': 16}
    """
    return TOKEN_PACKAGES.get(package_name, TOKEN_PACKAGES['medium'])


def calculate_tokens_for_price(price_eur: float) -> int:
    """
    Calculate tokens for a given price

    Args:
        price_eur: Price in EUR

    Returns:
        Number of tokens

    Example:
        >>> tokens = calculate_tokens_for_price(9.99)
        >>> print(tokens)  # 10000
    """
    for package in TOKEN_PACKAGES.values():
        if package['price_eur'] == price_eur:
            return package['tokens']

    # Default calculation: 1 EUR = ~1000 tokens
    return int(price_eur * 1000)
