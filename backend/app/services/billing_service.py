"""
LernsystemX Billing Service

Business logic for token and subscription management:
- AI usage access control (ensure user can use AI)
- Token charging (charge tokens for AI usage)
- Subscription plan management
- Monthly token allocation

ISO 27001:2013 compliant - Billing and payment security
"""

from typing import Dict, Any, Optional
from datetime import datetime
from psycopg.rows import dict_row

from app.extensions import db_pool
from app.repositories.token_repository import TokenRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.models.learning_method import get_required_tier, check_tier_access


class BillingService:
    """
    Billing Service for token and subscription business logic
    """

    @staticmethod
    def ensure_user_can_use_ai(user_id: str, method_id: str, estimated_tokens: int = 0) -> Dict[str, Any]:
        """
        Check if user can use AI method

        Args:
            user_id: User ID
            method_id: Learning method ID
            estimated_tokens: Estimated token cost (optional)

        Returns:
            {
                'allowed': bool,
                'reason': str (if not allowed),
                'subscription': dict,
                'wallet': dict,
                'estimated_cost': int
            }
        """
        # Get user
        user = UserRepository.find_by_id(user_id)
        if not user:
            return {
                'allowed': False,
                'reason': 'User not found'
            }

        # Get user's subscription
        subscription = SubscriptionRepository.get_subscription_for_user(user_id)

        # If no direct subscription, check organisation subscription
        if not subscription and user.get('organization_id'):
            subscription = SubscriptionRepository.get_subscription_for_organisation(
                user['organization_id']
            )

        # Default to 'free' plan if no subscription
        if not subscription:
            subscription = {
                'plan_name': 'free',
                'plan_tier': 'free',
                'status': 'active',
                'plan_features': {'ai': False}
            }

        # Check if plan allows AI access
        plan_features = subscription.get('plan_features', {})

        # Support both 'ai' and 'ai_access' keys for compatibility
        if not (plan_features.get('ai', False) or plan_features.get('ai_access', False)):
            return {
                'allowed': False,
                'reason': 'AI access not included in your plan. Upgrade to Premium or higher.',
                'subscription': subscription,
                'required_tier': 'premium',
                'user_tier': subscription.get('plan_tier', 'free')
            }

        # Check subscription status (accept both 'trial' and 'trialing' for compatibility)
        if subscription.get('status') not in ['active', 'trial', 'trialing']:
            return {
                'allowed': False,
                'reason': f'Subscription status: {subscription.get("status")}. Please update your payment method.',
                'subscription': subscription
            }

        # Get wallet (user or organisation)
        if user.get('organization_id') and subscription.get('organization_id'):
            # Use organisation wallet
            wallet = TokenRepository.get_or_create_organisation_wallet(user['organization_id'])
        else:
            # Use user wallet
            wallet = TokenRepository.get_or_create_user_wallet(user_id)

        # Check balance
        available_tokens = wallet['balance']

        if available_tokens < estimated_tokens:
            return {
                'allowed': False,
                'reason': f'Insufficient tokens. Available: {available_tokens}, Required: {estimated_tokens}',
                'subscription': subscription,
                'wallet': wallet,
                'estimated_cost': estimated_tokens,
                'shortage': estimated_tokens - available_tokens
            }

        # All checks passed
        return {
            'allowed': True,
            'subscription': subscription,
            'wallet': wallet,
            'estimated_cost': estimated_tokens,
            'available_tokens': available_tokens
        }

    @staticmethod
    def charge_ai_usage(
        user_id: str,
        organisation_id: Optional[str],
        method_id: str,
        tokens_used: int,
        provider: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Charge user for AI usage

        Args:
            user_id: User ID
            organisation_id: Organisation ID (if applicable)
            method_id: Learning method ID
            tokens_used: Tokens consumed
            provider: AI provider
            meta: Additional metadata

        Returns:
            {
                'transaction': dict,
                'new_balance': int,
                'usage_log': dict
            }
        """
        # Determine which wallet to charge
        if organisation_id:
            wallet = TokenRepository.get_or_create_organisation_wallet(organisation_id)
        else:
            wallet = TokenRepository.get_or_create_user_wallet(user_id)

        # Charge tokens
        transaction = TokenRepository.change_balance(
            wallet_id=wallet['wallet_id'],
            amount=-tokens_used,  # Negative for consumption
            reason='ai_execution',
            meta=meta,
            reference_type='learning_method',
            reference_id=method_id
        )

        # Note: AI usage logging is already done in execute_ai_method()
        # to avoid duplicate logging, we skip log_usage_from_ai here

        return {
            'transaction': transaction,
            'new_balance': transaction['balance_after'],
            'usage_log': None  # Logged in execute_ai_method
        }

    @staticmethod
    def get_effective_plan_for_user(user_id: str) -> Dict[str, Any]:
        """
        Get effective subscription plan for user

        Checks user's direct subscription first, then organisation subscription.

        Args:
            user_id: User ID

        Returns:
            Subscription plan details
        """
        # Check direct subscription
        subscription = SubscriptionRepository.get_subscription_for_user(user_id)

        if subscription:
            return {
                'source': 'user',
                'subscription': subscription,
                'plan_name': subscription.get('plan_name'),
                'tier': subscription.get('plan_tier'),
                'features': subscription.get('plan_features', {})
            }

        # Check organisation subscription
        user = UserRepository.find_by_id(user_id)

        if user and user.get('organization_id'):
            org_subscription = SubscriptionRepository.get_subscription_for_organisation(
                user['organization_id']
            )

            if org_subscription:
                return {
                    'source': 'organisation',
                    'subscription': org_subscription,
                    'plan_name': org_subscription.get('plan_name'),
                    'tier': org_subscription.get('plan_tier'),
                    'features': org_subscription.get('plan_features', {})
                }

        # Default to free plan
        return {
            'source': 'default',
            'subscription': None,
            'plan_name': 'free',
            'tier': 'free',
            'features': {
                'ai': False,
                'methods': 11,
                'course_creation': False
            }
        }

    @staticmethod
    def allocate_monthly_tokens_for_subscription(subscription_id: str) -> Dict[str, Any]:
        """
        Allocate monthly tokens for subscription

        Called by monthly billing cron job.

        Args:
            subscription_id: Subscription ID

        Returns:
            {
                'subscription_id': int,
                'tokens_granted': int,
                'transaction': dict
            }
        """
        # Get subscription
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        s.*,
                        sp.included_tokens
                    FROM subscriptions s
                    JOIN subscription_plans sp ON s.plan_id = sp.plan_id
                    WHERE s.subscription_id = %s
                """, (subscription_id,))

                subscription = cur.fetchone()

        if not subscription:
            raise ValueError(f'Subscription {subscription_id} not found')

        tokens_to_grant = subscription.get('included_tokens', 0)

        if tokens_to_grant <= 0:
            return {
                'subscription_id': subscription_id,
                'tokens_granted': 0,
                'message': 'No tokens to grant'
            }

        # Get wallet
        if subscription.get('user_id'):
            wallet = TokenRepository.get_or_create_user_wallet(subscription['user_id'])
        elif subscription.get('organization_id'):
            wallet = TokenRepository.get_or_create_organisation_wallet(subscription['organization_id'])
        else:
            raise ValueError('Subscription has no user_id or organisation_id')

        # Grant tokens
        transaction = TokenRepository.change_balance(
            wallet_id=wallet['wallet_id'],
            amount=tokens_to_grant,
            reason='subscription_monthly_grant',
            meta={'subscription_id': subscription_id},
            reference_type='subscription',
            reference_id=subscription_id
        )

        # Update last_grant_date
        with db_pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE token_wallets
                    SET last_grant_date = CURRENT_DATE,
                        monthly_grant_amount = %s
                    WHERE wallet_id = %s
                """, (tokens_to_grant, wallet['wallet_id']))
                conn.commit()

        return {
            'subscription_id': subscription_id,
            'tokens_granted': tokens_to_grant,
            'transaction': transaction,
            'new_balance': transaction['balance_after']
        }

    @staticmethod
    def check_feature_access(user_id: str, feature: str) -> Dict[str, Any]:
        """
        Check if user has access to a feature

        Args:
            user_id: User ID
            feature: Feature name (e.g., 'ai_access', 'course_creation')

        Returns:
            {
                'has_access': bool,
                'plan': str,
                'reason': str (if no access)
            }
        """
        plan_info = BillingService.get_effective_plan_for_user(user_id)

        features = plan_info.get('features', {})
        has_access = features.get(feature, False)

        if has_access:
            return {
                'has_access': True,
                'plan': plan_info.get('plan_name'),
                'tier': plan_info.get('tier')
            }
        else:
            return {
                'has_access': False,
                'plan': plan_info.get('plan_name'),
                'tier': plan_info.get('tier'),
                'reason': f'Feature "{feature}" not available in {plan_info.get("plan_name")} plan'
            }

    @staticmethod
    def estimate_ai_cost(method_name: str, complexity: str = 'medium') -> int:
        """
        Estimate AI token cost for a method

        Args:
            method_name: Learning method name
            complexity: Complexity level (simple, medium, complex)

        Returns:
            Estimated token cost
        """
        # Base costs by method type
        base_costs = {
            'KI-Tutor': 500,
            'KI-Glossar': 300,
            'Braindump': 800,
            'KI-Quiz': 1000,
            'Deep Praxis': 2000,
            'Deep Scenario': 2500,
            'Whiteboard-KI': 600,
            'PDF-Analyse': 400,  # per page
            'Übersetzung': 300,
            'MindMap': 1000
        }

        base_cost = base_costs.get(method_name, 500)

        # Complexity multiplier
        multipliers = {
            'simple': 0.5,
            'medium': 1.0,
            'complex': 2.0
        }

        multiplier = multipliers.get(complexity, 1.0)

        return int(base_cost * multiplier)

    @staticmethod
    def can_user_afford(user_id: str, estimated_cost: int) -> bool:
        """
        Quick check if user can afford estimated cost

        Args:
            user_id: User ID
            estimated_cost: Estimated token cost

        Returns:
            True if user has sufficient balance
        """
        user = UserRepository.find_by_id(user_id)

        if not user:
            return False

        # Get wallet
        if user.get('organization_id'):
            # Try organisation wallet first
            org_wallet = TokenRepository.get_wallet_for_organisation(user['organization_id'])
            if org_wallet and org_wallet['balance'] >= estimated_cost:
                return True

        # Check user wallet
        user_wallet = TokenRepository.get_wallet_for_user(user_id)

        if user_wallet and user_wallet['balance'] >= estimated_cost:
            return True

        return False
