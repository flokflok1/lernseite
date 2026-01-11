"""
LernsystemX Subscriptions - Factory Pattern

DDD Factory Pattern for creating subscription instances:
- SubscriptionFactory.create_subscription(): Create new subscription
- SubscriptionFactory.create_trial(): Create trial subscription
- SubscriptionFactory.upgrade(): Upgrade to higher plan
- SubscriptionFactory.downgrade(): Downgrade to lower plan
- SubscriptionFactory.cancel(): Cancel subscription

Factory Pattern ensures:
- Business rules are enforced at creation time
- Complex object initialization is encapsulated
- Validation happens in one place
- Default values are consistently applied

ISO 27001:2013 compliant - Subscription security
ISO/IEC/IEEE 26515:2018 compliant - DDD Factory Pattern
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.repositories.subscription import SubscriptionRepository
from app.repositories.user import UserRepository
from .value_objects import (
    PlanType,
    BillingCycle,
    SubscriptionStatus,
    get_tier_for_plan,
    check_tier_access,
    TIER_HIERARCHY
)


class SubscriptionFactory:
    """
    Factory for creating subscription instances

    Implements DDD Factory Pattern for complex domain object creation.
    Encapsulates business rules and validation logic.
    """

    @staticmethod
    def create_subscription(
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        plan_id: int = None,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        promo_code: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new subscription

        Business Rules:
        - Exactly one of user_id or organization_id must be set
        - Plan must exist and be active
        - User/Organisation cannot have active subscription already
        - Trial subscriptions get 7 days free trial

        Args:
            user_id: User ID (for individual subscriptions)
            organization_id: Organisation ID (for org subscriptions)
            plan_id: Subscription plan ID
            billing_cycle: Billing cycle (monthly or yearly)
            promo_code: Optional promo code
            meta: Additional metadata

        Returns:
            Subscription data dictionary ready for database insertion

        Raises:
            ValueError: If validation fails

        Example:
            >>> sub = SubscriptionFactory.create_subscription(
            ...     user_id='123',
            ...     plan_id=2,
            ...     billing_cycle=BillingCycle.MONTHLY
            ... )
        """
        # Validation: Exactly one of user_id or organization_id
        if user_id is None and organization_id is None:
            raise ValueError("Must specify either user_id or organization_id")

        if user_id is not None and organization_id is not None:
            raise ValueError("Cannot specify both user_id and organization_id")

        # Verify plan exists and is active
        plan = SubscriptionRepository.get_plan_by_id(plan_id)

        if not plan:
            raise ValueError(f"Plan with ID {plan_id} not found")

        if not plan.get('active', False):
            raise ValueError(f"Plan {plan['name']} is not active")

        # Check for existing active subscription
        if user_id:
            existing = SubscriptionRepository.get_subscription_for_user(user_id)
            if existing and existing.get('status') in ['active', 'trial']:
                raise ValueError(
                    f"User already has an active {existing.get('plan_name')} subscription"
                )

        if organization_id:
            existing = SubscriptionRepository.get_subscription_for_organisation(organization_id)
            if existing and existing.get('status') in ['active', 'trial']:
                raise ValueError(
                    f"Organisation already has an active {existing.get('plan_name')} subscription"
                )

        # Calculate dates
        now = datetime.utcnow()
        trial_days = 7 if plan.get('name') != 'free' else 0

        if trial_days > 0:
            status = SubscriptionStatus.TRIAL
            trial_ends_at = now + timedelta(days=trial_days)
        else:
            status = SubscriptionStatus.ACTIVE
            trial_ends_at = None

        # Calculate period dates based on billing cycle
        if billing_cycle == BillingCycle.MONTHLY:
            current_period_end = now + timedelta(days=30)
        else:  # YEARLY
            current_period_end = now + timedelta(days=365)

        # Calculate price (with promo code discount if applicable)
        if billing_cycle == BillingCycle.MONTHLY:
            price = plan.get('monthly_price_eur', 0)
        else:
            price = plan.get('yearly_price_eur', 0) or (plan.get('monthly_price_eur', 0) * 12)

        # TODO: Apply promo code discount
        discount = Decimal('0.00')

        # Build subscription data
        subscription_data = {
            'subscription_id': str(uuid.uuid4()),
            'user_id': user_id,
            'organization_id': organization_id,
            'plan_id': plan_id,
            'status': status.value,
            'billing_cycle': billing_cycle.value,
            'price': price,
            'current_period_start': now,
            'current_period_end': current_period_end,
            'trial_ends_at': trial_ends_at,
            'auto_renew': True,
            'cancel_at_period_end': False,
            'created_at': now,
            'updated_at': now,
            'meta': meta or {}
        }

        if promo_code:
            subscription_data['meta']['promo_code'] = promo_code
            subscription_data['meta']['discount_applied'] = float(discount)

        return subscription_data

    @staticmethod
    def create_trial(
        user_id: str,
        plan_id: int,
        trial_days: int = 7
    ) -> Dict[str, Any]:
        """
        Create a trial subscription

        Args:
            user_id: User ID
            plan_id: Plan ID
            trial_days: Trial period in days (default: 7)

        Returns:
            Trial subscription data

        Example:
            >>> trial = SubscriptionFactory.create_trial(
            ...     user_id='123',
            ...     plan_id=2,
            ...     trial_days=14
            ... )
        """
        subscription_data = SubscriptionFactory.create_subscription(
            user_id=user_id,
            plan_id=plan_id,
            billing_cycle=BillingCycle.MONTHLY,
            meta={'trial_days': trial_days}
        )

        # Override status and dates for trial
        now = datetime.utcnow()
        subscription_data['status'] = SubscriptionStatus.TRIAL.value
        subscription_data['trial_ends_at'] = now + timedelta(days=trial_days)
        subscription_data['current_period_end'] = now + timedelta(days=trial_days)

        return subscription_data

    @staticmethod
    def upgrade(
        subscription_id: str,
        new_plan_id: int,
        reason: Optional[str] = None,
        prorate: bool = True
    ) -> Dict[str, Any]:
        """
        Upgrade subscription to a higher tier plan

        Business Rules:
        - New plan must be higher tier than current
        - Subscription must be active or trial
        - Proration applies credit for unused time

        Args:
            subscription_id: Current subscription ID
            new_plan_id: New plan ID (must be higher tier)
            reason: Upgrade reason
            prorate: Apply proration credit

        Returns:
            Update data for subscription

        Raises:
            ValueError: If upgrade is not allowed

        Example:
            >>> upgrade = SubscriptionFactory.upgrade(
            ...     subscription_id='sub_123',
            ...     new_plan_id=3,
            ...     reason='Need marketplace access'
            ... )
        """
        # Get current subscription
        subscription = SubscriptionRepository.get_by_id(subscription_id)

        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")

        # Verify subscription is active
        if subscription['status'] not in ['active', 'trial']:
            raise ValueError(
                f"Cannot upgrade subscription with status: {subscription['status']}"
            )

        # Get current and new plan
        current_plan = SubscriptionRepository.get_plan_by_id(subscription['plan_id'])
        new_plan = SubscriptionRepository.get_plan_by_id(new_plan_id)

        if not new_plan or not new_plan.get('active'):
            raise ValueError(f"New plan {new_plan_id} not found or not active")

        # Verify upgrade (higher tier)
        current_tier = get_tier_for_plan(current_plan['name'])
        new_tier = get_tier_for_plan(new_plan['name'])

        if TIER_HIERARCHY.get(new_tier, 0) <= TIER_HIERARCHY.get(current_tier, 0):
            raise ValueError(
                f"Cannot upgrade from {current_tier} to {new_tier}. "
                "Use downgrade() for lower tiers."
            )

        # Calculate new price
        if subscription['billing_cycle'] == 'monthly':
            new_price = new_plan.get('monthly_price_eur', 0)
        else:
            new_price = new_plan.get('yearly_price_eur', 0) or (
                new_plan.get('monthly_price_eur', 0) * 12
            )

        # TODO: Calculate proration credit
        proration_credit = Decimal('0.00')

        update_data = {
            'plan_id': new_plan_id,
            'price': new_price,
            'updated_at': datetime.utcnow(),
            'meta': subscription.get('meta', {})
        }

        update_data['meta']['upgrade_reason'] = reason
        update_data['meta']['previous_plan'] = current_plan['name']
        update_data['meta']['upgraded_at'] = datetime.utcnow().isoformat()

        if prorate:
            update_data['meta']['proration_credit'] = float(proration_credit)

        return update_data

    @staticmethod
    def downgrade(
        subscription_id: str,
        new_plan_id: int,
        reason: Optional[str] = None,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """
        Downgrade subscription to a lower tier plan

        Business Rules:
        - New plan must be lower tier than current
        - By default, downgrade happens at period end
        - Immediate downgrade loses remaining time

        Args:
            subscription_id: Current subscription ID
            new_plan_id: New plan ID (must be lower tier)
            reason: Downgrade reason
            immediate: Apply immediately (default: False)

        Returns:
            Update data for subscription

        Raises:
            ValueError: If downgrade is not allowed

        Example:
            >>> downgrade = SubscriptionFactory.downgrade(
            ...     subscription_id='sub_123',
            ...     new_plan_id=1,
            ...     reason='Too expensive',
            ...     immediate=False
            ... )
        """
        # Get current subscription
        subscription = SubscriptionRepository.get_by_id(subscription_id)

        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")

        # Get current and new plan
        current_plan = SubscriptionRepository.get_plan_by_id(subscription['plan_id'])
        new_plan = SubscriptionRepository.get_plan_by_id(new_plan_id)

        if not new_plan or not new_plan.get('active'):
            raise ValueError(f"New plan {new_plan_id} not found or not active")

        # Verify downgrade (lower tier)
        current_tier = get_tier_for_plan(current_plan['name'])
        new_tier = get_tier_for_plan(new_plan['name'])

        if TIER_HIERARCHY.get(new_tier, 0) >= TIER_HIERARCHY.get(current_tier, 0):
            raise ValueError(
                f"Cannot downgrade from {current_tier} to {new_tier}. "
                "Use upgrade() for higher tiers."
            )

        # Calculate new price
        if subscription['billing_cycle'] == 'monthly':
            new_price = new_plan.get('monthly_price_eur', 0)
        else:
            new_price = new_plan.get('yearly_price_eur', 0) or (
                new_plan.get('monthly_price_eur', 0) * 12
            )

        update_data = {
            'updated_at': datetime.utcnow(),
            'meta': subscription.get('meta', {})
        }

        update_data['meta']['downgrade_reason'] = reason
        update_data['meta']['previous_plan'] = current_plan['name']
        update_data['meta']['downgrade_scheduled_at'] = datetime.utcnow().isoformat()

        if immediate:
            # Apply immediately
            update_data['plan_id'] = new_plan_id
            update_data['price'] = new_price
            update_data['meta']['downgrade_applied'] = 'immediate'
        else:
            # Schedule for period end
            update_data['meta']['pending_plan_id'] = new_plan_id
            update_data['meta']['pending_price'] = float(new_price)
            update_data['meta']['downgrade_at_period_end'] = True

        return update_data

    @staticmethod
    def cancel(
        subscription_id: str,
        reason: Optional[str] = None,
        immediate: bool = False,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel subscription

        Business Rules:
        - By default, cancellation happens at period end
        - Immediate cancellation loses remaining time
        - User can reactivate before period end

        Args:
            subscription_id: Subscription ID
            reason: Cancellation reason
            immediate: Cancel immediately (default: False)
            feedback: User feedback

        Returns:
            Update data for subscription

        Example:
            >>> cancel = SubscriptionFactory.cancel(
            ...     subscription_id='sub_123',
            ...     reason='Too expensive',
            ...     immediate=False,
            ...     feedback='Would reconsider if cheaper'
            ... )
        """
        # Get subscription
        subscription = SubscriptionRepository.get_by_id(subscription_id)

        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")

        now = datetime.utcnow()

        update_data = {
            'updated_at': now,
            'cancellation_reason': reason,
            'meta': subscription.get('meta', {})
        }

        if immediate:
            # Cancel immediately
            update_data['status'] = SubscriptionStatus.CANCELLED.value
            update_data['cancelled_at'] = now
            update_data['current_period_end'] = now
            update_data['auto_renew'] = False
        else:
            # Cancel at period end
            update_data['status'] = SubscriptionStatus.CANCELLED.value
            update_data['cancelled_at'] = now
            update_data['cancel_at_period_end'] = True
            update_data['auto_renew'] = False

        if feedback:
            update_data['meta']['cancellation_feedback'] = feedback

        update_data['meta']['cancelled_at'] = now.isoformat()
        update_data['meta']['cancellation_type'] = 'immediate' if immediate else 'at_period_end'

        return update_data

    @staticmethod
    def reactivate(subscription_id: str) -> Dict[str, Any]:
        """
        Reactivate cancelled subscription

        Business Rules:
        - Only works if subscription hasn't expired yet
        - Restores auto_renew and active status
        - Cannot reactivate expired subscriptions

        Args:
            subscription_id: Subscription ID

        Returns:
            Update data for subscription

        Raises:
            ValueError: If reactivation is not allowed

        Example:
            >>> reactivate = SubscriptionFactory.reactivate('sub_123')
        """
        # Get subscription
        subscription = SubscriptionRepository.get_by_id(subscription_id)

        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")

        # Verify subscription is cancelled
        if subscription['status'] != 'cancelled':
            raise ValueError(
                f"Cannot reactivate subscription with status: {subscription['status']}"
            )

        # Verify not expired
        if subscription.get('current_period_end') and subscription['current_period_end'] < datetime.utcnow():
            raise ValueError(
                "Subscription has expired and cannot be reactivated. "
                "Please create a new subscription."
            )

        update_data = {
            'status': SubscriptionStatus.ACTIVE.value,
            'auto_renew': True,
            'cancel_at_period_end': False,
            'cancelled_at': None,
            'cancellation_reason': None,
            'updated_at': datetime.utcnow(),
            'meta': subscription.get('meta', {})
        }

        update_data['meta']['reactivated_at'] = datetime.utcnow().isoformat()

        return update_data
