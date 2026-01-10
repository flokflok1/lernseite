"""
LernsystemX Subscriptions - Value Objects

Domain value objects for subscription management:
- PlanType: Subscription plan types (Free, Premium, Creator, etc.)
- BillingCycle: Billing cycles (Monthly, Yearly)
- SubscriptionStatus: Subscription states

Value Objects are immutable and identified by their attributes.
Part of DDD (Domain-Driven Design) tactical patterns.

ISO 27001:2013 compliant - Subscription management
"""

from enum import Enum
from typing import Dict, Any


class PlanType(str, Enum):
    """
    Subscription plan types

    Plans are organized by tier:
    - Free: Basic access, no AI, 11 methods
    - Premium: AI access, all 21 methods, 10K tokens/month
    - Creator: Marketplace access, 20K tokens/month
    - Teacher: Class management, 30K tokens/month, LiveRoom Pro
    - School: Organisation plan, unlimited users
    - Company: Enterprise plan, compliance features
    """
    FREE = "free"
    PREMIUM = "premium"
    CREATOR = "creator"
    TEACHER = "teacher"
    SCHOOL = "school"
    COMPANY = "company"

    @property
    def tier(self) -> str:
        """Get tier for this plan type"""
        return PLAN_TYPE_TO_TIER[self]

    @property
    def is_organisation_plan(self) -> bool:
        """Check if this is an organisation plan"""
        return self in [PlanType.SCHOOL, PlanType.COMPANY]

    @property
    def default_included_tokens(self) -> int:
        """Get default token allocation for this plan"""
        token_allocation = {
            PlanType.FREE: 0,
            PlanType.PREMIUM: 10000,
            PlanType.CREATOR: 20000,
            PlanType.TEACHER: 30000,
            PlanType.SCHOOL: 0,  # Custom allocation
            PlanType.COMPANY: 0,  # Custom allocation
        }
        return token_allocation[self]


class BillingCycle(str, Enum):
    """
    Billing cycle types

    - Monthly: Billed every month
    - Yearly: Billed annually (typically with discount)
    """
    MONTHLY = "monthly"
    YEARLY = "yearly"

    @property
    def months(self) -> int:
        """Get number of months in billing cycle"""
        return 12 if self == BillingCycle.YEARLY else 1

    def calculate_price(self, monthly_price: float, yearly_price: float = None) -> float:
        """
        Calculate price for this billing cycle

        Args:
            monthly_price: Monthly price
            yearly_price: Yearly price (if None, calculated from monthly * 12)

        Returns:
            Price for this billing cycle
        """
        if self == BillingCycle.MONTHLY:
            return monthly_price
        else:
            return yearly_price if yearly_price else monthly_price * 12


class SubscriptionStatus(str, Enum):
    """
    Subscription status enumeration

    Lifecycle states:
    - Active: Subscription is active and user has full access
    - Trial: In trial period (typically 7-30 days)
    - Cancelled: User cancelled but still has access until period end
    - Past Due: Payment failed, grace period active
    - Expired: Subscription expired, no access
    - Suspended: Manually suspended (admin action)
    """
    ACTIVE = "active"
    TRIAL = "trial"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    EXPIRED = "expired"
    SUSPENDED = "suspended"

    @property
    def has_access(self) -> bool:
        """Check if subscription status allows access"""
        return self in [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIAL,
            SubscriptionStatus.CANCELLED  # Still has access until period end
        ]

    @property
    def is_renewable(self) -> bool:
        """Check if subscription can be renewed"""
        return self in [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIAL,
            SubscriptionStatus.CANCELLED,
            SubscriptionStatus.EXPIRED
        ]


# Plan type to tier mapping
PLAN_TYPE_TO_TIER: Dict[PlanType, str] = {
    PlanType.FREE: "free",
    PlanType.PREMIUM: "premium",
    PlanType.CREATOR: "pro",
    PlanType.TEACHER: "pro",
    PlanType.SCHOOL: "enterprise",
    PlanType.COMPANY: "enterprise",
}


# Tier hierarchy (higher = more access)
TIER_HIERARCHY: Dict[str, int] = {
    "free": 0,
    "premium": 1,
    "pro": 2,
    "enterprise": 3
}


def check_tier_access(user_tier: str, required_tier: str) -> bool:
    """
    Check if user tier has access to required tier

    Args:
        user_tier: User's subscription tier
        required_tier: Required tier for feature

    Returns:
        True if user has access

    Example:
        >>> check_tier_access('premium', 'free')  # True
        >>> check_tier_access('free', 'premium')  # False
    """
    user_level = TIER_HIERARCHY.get(user_tier, 0)
    required_level = TIER_HIERARCHY.get(required_tier, 0)

    return user_level >= required_level


def get_tier_for_plan(plan_type: str) -> str:
    """
    Get tier for a plan type

    Args:
        plan_type: Plan type name

    Returns:
        Tier name
    """
    try:
        plan = PlanType(plan_type)
        return plan.tier
    except ValueError:
        return "free"
