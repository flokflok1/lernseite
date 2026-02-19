"""
Subscription domain enumerations
"""

from enum import Enum


class SubscriptionTier(str, Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class BillingCycle(str, Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    YEARLY = "yearly"
