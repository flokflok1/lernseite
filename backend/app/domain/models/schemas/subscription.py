"""
LernsystemX Subscription Models

Pydantic models for subscription and plan operations:
- Subscription plans (Free, Premium, Creator, Teacher, School, Company)
- Subscription management (create, update, cancel)
- Tier-based access control
- Billing cycle management

ISO 9001:2015 compliant - Subscription management
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal

from app.domain.models.enums import SubscriptionTier, SubscriptionStatus, BillingCycle


class SubscriptionPlanBase(BaseModel):
    """
    Base subscription plan model

    Example:
        >>> plan = SubscriptionPlanBase(
        ...     name="premium",
        ...     tier="premium",
        ...     monthly_price_eur=14.99,
        ...     included_tokens=10000,
        ...     features={"ai_access": True, "all_methods": True}
        ... )
    """
    name: str = Field(..., min_length=2, max_length=50, description="Plan name (e.g., free, premium, creator)")
    tier: SubscriptionTier = Field(..., description="Subscription tier")
    monthly_price_eur: Decimal = Field(..., ge=0, description="Monthly price in EUR")
    yearly_price_eur: Optional[Decimal] = Field(None, ge=0, description="Yearly price in EUR (if applicable)")
    included_tokens: int = Field(default=0, ge=0, description="Monthly token grant")
    max_users: Optional[int] = Field(None, ge=1, description="Max users (for organisation plans)")
    max_courses: Optional[int] = Field(None, ge=1, description="Max courses user can create")
    features: Dict[str, Any] = Field(default_factory=dict, description="Plan features (JSON)")

    model_config = ConfigDict(from_attributes=True)


class SubscriptionPlanResponse(SubscriptionPlanBase):
    """
    Subscription plan response model

    Example:
        >>> plan = SubscriptionPlanResponse(
        ...     plan_id=1,
        ...     name="premium",
        ...     tier="premium",
        ...     monthly_price_eur=14.99,
        ...     included_tokens=10000,
        ...     active=True,
        ...     created_at=datetime.now()
        ... )
    """
    plan_id: int = Field(..., description="Plan ID")
    active: bool = Field(default=True, description="Plan is active and available")
    sort_order: int = Field(default=0, description="Display sort order")
    is_default: bool = Field(default=False, description="Is default plan")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Computed fields
    yearly_discount_percent: Optional[int] = Field(None, description="Yearly discount percentage")
    price_per_1k_tokens: Optional[Decimal] = Field(None, description="Price per 1000 tokens")

    model_config = ConfigDict(from_attributes=True)


class SubscriptionBase(BaseModel):
    """
    Base subscription model

    Example:
        >>> subscription = SubscriptionBase(
        ...     user_id=42,
        ...     plan_id=2,
        ...     status="active",
        ...     billing_cycle="monthly"
        ... )
    """
    user_id: Optional[int] = Field(None, description="User ID (for individual subscriptions)")
    organisation_id: Optional[int] = Field(None, description="Organisation ID (for org subscriptions)")
    plan_id: int = Field(..., description="Subscription plan ID")
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE, description="Subscription status")
    billing_cycle: BillingCycle = Field(default=BillingCycle.MONTHLY, description="Billing cycle")
    auto_renew: bool = Field(default=True, description="Auto-renewal enabled")

    @field_validator('user_id', 'organisation_id')
    @classmethod
    def validate_owner(cls, v, info):
        """Ensure exactly one of user_id or organisation_id is set"""
        data = info.data
        if info.field_name == 'organisation_id':
            user_id = data.get('user_id')
            org_id = v
            if user_id is None and org_id is None:
                raise ValueError('Must specify either user_id or organisation_id')
            if user_id is not None and org_id is not None:
                raise ValueError('Cannot specify both user_id and organisation_id')
        return v

    model_config = ConfigDict(from_attributes=True)


class SubscriptionCreate(SubscriptionBase):
    """
    Subscription creation model

    Example:
        >>> subscription = SubscriptionCreate(
        ...     user_id=42,
        ...     plan_id=2,
        ...     billing_cycle="monthly",
        ...     promo_code="EARLYBIRD2024"
        ... )
    """
    promo_code: Optional[str] = Field(None, max_length=50, description="Promo code (if applicable)")
    trial_days: Optional[int] = Field(None, ge=0, le=30, description="Trial period in days")

    model_config = ConfigDict(from_attributes=True)


class SubscriptionResponse(SubscriptionBase):
    """
    Subscription response model

    Example:
        >>> subscription = SubscriptionResponse(
        ...     subscription_id=123,
        ...     user_id=42,
        ...     plan_id=2,
        ...     plan=plan_response,
        ...     status="active",
        ...     started_at=datetime.now(),
        ...     expires_at=datetime.now() + timedelta(days=30)
        ... )
    """
    subscription_id: int = Field(..., description="Subscription ID")
    plan: Optional[SubscriptionPlanResponse] = Field(None, description="Subscription plan details")
    started_at: datetime = Field(..., description="Subscription start date")
    expires_at: Optional[datetime] = Field(None, description="Subscription expiry date")
    trial_ends_at: Optional[datetime] = Field(None, description="Trial end date")
    cancelled_at: Optional[datetime] = Field(None, description="Cancellation date")
    cancellation_reason: Optional[str] = Field(None, description="Cancellation reason")
    next_billing_at: Optional[datetime] = Field(None, description="Next billing date")
    stripe_subscription_id: Optional[str] = Field(None, max_length=255, description="Stripe subscription ID")
    stripe_customer_id: Optional[str] = Field(None, max_length=255, description="Stripe customer ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Computed fields
    is_trial: bool = Field(default=False, description="Currently in trial period")
    days_remaining: Optional[int] = Field(None, description="Days until expiry")
    can_cancel: bool = Field(default=True, description="Can be cancelled")

    model_config = ConfigDict(from_attributes=True)


class SubscriptionUpdate(BaseModel):
    """
    Subscription update model (partial updates)

    Example:
        >>> update = SubscriptionUpdate(
        ...     auto_renew=False,
        ...     billing_cycle="yearly"
        ... )
    """
    plan_id: Optional[int] = Field(None, description="New plan ID")
    status: Optional[SubscriptionStatus] = Field(None, description="New status")
    billing_cycle: Optional[BillingCycle] = Field(None, description="New billing cycle")
    auto_renew: Optional[bool] = Field(None, description="Auto-renewal setting")

    model_config = ConfigDict(from_attributes=True)


class SubscriptionChangeRequest(BaseModel):
    """
    Subscription plan change request

    Example:
        >>> change = SubscriptionChangeRequest(
        ...     new_plan_id=3,
        ...     reason="Upgrade to Creator"
        ... )
    """
    new_plan_id: int = Field(..., description="New plan ID")
    reason: Optional[str] = Field(None, max_length=255, description="Change reason")
    prorate: bool = Field(default=True, description="Prorate the plan change")

    model_config = ConfigDict(from_attributes=True)


class SubscriptionCancelRequest(BaseModel):
    """
    Subscription cancellation request

    Example:
        >>> cancel = SubscriptionCancelRequest(
        ...     reason="Too expensive",
        ...     immediate=False
        ... )
    """
    reason: Optional[str] = Field(None, max_length=500, description="Cancellation reason")
    immediate: bool = Field(default=False, description="Cancel immediately vs. end of billing period")
    feedback: Optional[str] = Field(None, max_length=1000, description="User feedback")

    model_config = ConfigDict(from_attributes=True)


class SubscriptionStats(BaseModel):
    """
    Subscription statistics

    Example:
        >>> stats = SubscriptionStats(
        ...     total_subscribers=1523,
        ...     active_subscribers=1342,
        ...     by_plan={"free": 500, "premium": 800, "creator": 42},
        ...     by_status={"active": 1342, "cancelled": 181},
        ...     mrr=18950.58,
        ...     arr=227406.96
        ... )
    """
    total_subscribers: int = Field(..., ge=0, description="Total number of subscribers")
    active_subscribers: int = Field(..., ge=0, description="Active subscribers")
    trial_subscribers: int = Field(default=0, ge=0, description="Trial subscribers")
    cancelled_subscribers: int = Field(default=0, ge=0, description="Cancelled subscribers")
    by_plan: Dict[str, int] = Field(..., description="Subscribers by plan")
    by_status: Dict[str, int] = Field(..., description="Subscribers by status")
    by_tier: Optional[Dict[str, int]] = Field(None, description="Subscribers by tier")
    mrr: Decimal = Field(..., ge=0, description="Monthly Recurring Revenue (EUR)")
    arr: Decimal = Field(..., ge=0, description="Annual Recurring Revenue (EUR)")
    churn_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Churn rate percentage")
    period_start: Optional[datetime] = Field(None, description="Statistics period start")
    period_end: Optional[datetime] = Field(None, description="Statistics period end")

    model_config = ConfigDict(from_attributes=True)


class SubscriptionUpgrade(BaseModel):
    """
    Subscription upgrade record

    Example:
        >>> upgrade = SubscriptionUpgrade(
        ...     upgrade_id=123,
        ...     user_id=42,
        ...     from_plan="free",
        ...     to_plan="premium",
        ...     reason="Need AI features",
        ...     upgraded_at=datetime.now()
        ... )
    """
    upgrade_id: int = Field(..., description="Upgrade ID")
    user_id: int = Field(..., description="User ID")
    from_plan: str = Field(..., max_length=50, description="Previous plan name")
    to_plan: str = Field(..., max_length=50, description="New plan name")
    reason: Optional[str] = Field(None, description="Upgrade reason")
    promo_code: Optional[str] = Field(None, max_length=50, description="Promo code used")
    discount_amount: Optional[Decimal] = Field(None, ge=0, description="Discount amount in EUR")
    upgraded_at: datetime = Field(..., description="Upgrade timestamp")

    model_config = ConfigDict(from_attributes=True)


# Predefined subscription plans
SUBSCRIPTION_PLANS = {
    'free': {
        'tier': 'free',
        'monthly_price_eur': 0.00,
        'yearly_price_eur': 0.00,
        'included_tokens': 0,
        'max_courses': 0,
        'features': {
            'learning_methods': 11,  # Basic methods only
            'ai_access': False,
            'course_creation': False,
            'community_publishing': False,
            'private_groups': False,
            'liveroom': False,
            'dashboard_customizing': False
        }
    },
    'premium': {
        'tier': 'premium',
        'monthly_price_eur': 14.99,
        'yearly_price_eur': 129.99,  # ~10.83/month, 2 months free
        'included_tokens': 10000,
        'max_courses': 50,  # Private courses
        'features': {
            'learning_methods': 21,  # All methods
            'ai_access': True,
            'course_creation': True,
            'community_publishing': True,
            'private_groups': True,
            'liveroom': 'basic',  # 4 participants
            'dashboard_customizing': True,
            'max_group_members': 10
        }
    },
    'creator': {
        'tier': 'pro',
        'monthly_price_eur': 29.99,
        'yearly_price_eur': 299.99,
        'included_tokens': 20000,
        'max_courses': None,  # Unlimited
        'features': {
            'learning_methods': 21,
            'ai_access': True,
            'course_creation': True,
            'community_publishing': True,
            'marketplace': True,  # Can sell courses
            'revenue_share': 75,  # 75% revenue
            'global_publishing': True,  # 20 languages
            'pro_methods_create': True,
            'creator_analytics': True,
            'private_groups': True,
            'liveroom': 'basic',
            'dashboard_customizing': True
        }
    },
    'teacher': {
        'tier': 'pro',
        'monthly_price_eur': 39.99,
        'yearly_price_eur': 399.99,
        'included_tokens': 30000,
        'max_users': None,  # Can manage unlimited students
        'features': {
            'learning_methods': 21,
            'ai_access': True,
            'course_creation': True,
            'class_management': True,
            'liveroom': 'pro',  # Unlimited participants
            'whiteboard_pro': True,
            'screen_sharing': True,
            'recording': True,
            'breakout_rooms': True,
            'exam_management': True,
            'student_tracking': True
        }
    },
    'school': {
        'tier': 'enterprise',
        'monthly_price_eur': None,  # Custom pricing
        'yearly_price_eur': None,
        'included_tokens': None,  # Shared pool
        'max_users': None,
        'features': {
            'learning_methods': 21,
            'ai_access': True,
            'organisation_management': True,
            'teacher_accounts': True,
            'student_accounts': True,
            'custom_domain': True,
            'sso': True,
            'api_access': True,
            'priority_support': True,
            'dedicated_account_manager': True,
            'custom_branding': True
        }
    },
    'company': {
        'tier': 'enterprise',
        'monthly_price_eur': None,  # Custom pricing
        'yearly_price_eur': None,
        'included_tokens': None,  # Shared pool
        'max_users': None,
        'features': {
            'learning_methods': 21,
            'ai_access': True,
            'organisation_management': True,
            'employee_accounts': True,
            'team_management': True,
            'custom_domain': True,
            'sso': True,
            'scorm_support': True,
            'api_access': True,
            'priority_support': True,
            'dedicated_account_manager': True,
            'custom_branding': True,
            'compliance_reporting': True
        }
    }
}


def get_plan_features(plan_name: str) -> Dict[str, Any]:
    """
    Get plan features by name

    Args:
        plan_name: Plan name (free, premium, creator, teacher, school, company)

    Returns:
        Plan features dictionary

    Example:
        >>> features = get_plan_features('premium')
        >>> print(features['ai_access'])  # True
    """
    plan = SUBSCRIPTION_PLANS.get(plan_name, SUBSCRIPTION_PLANS['free'])
    return plan.get('features', {})


def can_access_feature(plan_name: str, feature: str) -> bool:
    """
    Check if plan has access to a feature

    Args:
        plan_name: Plan name
        feature: Feature name

    Returns:
        True if plan has access to feature

    Example:
        >>> can_access_feature('premium', 'ai_access')  # True
        >>> can_access_feature('free', 'ai_access')  # False
    """
    features = get_plan_features(plan_name)
    return features.get(feature, False) == True or features.get(feature, False) != False


def get_tier_hierarchy() -> Dict[str, int]:
    """
    Get tier hierarchy for access control

    Returns:
        Tier hierarchy (higher = more access)

    Example:
        >>> hierarchy = get_tier_hierarchy()
        >>> print(hierarchy['premium'] > hierarchy['free'])  # True
    """
    return {
        'free': 0,
        'premium': 1,
        'pro': 2,
        'enterprise': 3
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
    hierarchy = get_tier_hierarchy()
    user_level = hierarchy.get(user_tier, 0)
    required_level = hierarchy.get(required_tier, 0)

    return user_level >= required_level
