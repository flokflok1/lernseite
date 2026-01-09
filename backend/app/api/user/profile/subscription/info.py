"""
LernsystemX Profile Subscription API

Subscription and token balance endpoints:
- GET /api/v1/profile/subscription - Get subscription info
- GET /api/v1/profile/tokens - Get token balance

ISO 27001:2013 compliant - Billing and subscription data access
"""

from flask import Blueprint, jsonify

from app.repositories.token import TokenRepository
from app.repositories.subscription import SubscriptionRepository
from app.services.billing_service import BillingService
from app.middleware.auth import token_required, get_current_user


profile_subscription_bp = Blueprint('profile_subscription', __name__, url_prefix='/profile')


@profile_subscription_bp.route('/subscription', methods=['GET'])
@token_required
def get_subscription():
    """
    Get current user's subscription information

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Subscription information
        - plan: Subscription plan (free, premium, pro)
        - tier: Subscription tier
        - status: Subscription status (active, cancelled, expired)
        - features: Plan features
        - expires_at: Subscription end date
        - auto_renew: Whether subscription will auto-renew
        - source: Subscription source (user, organisation, default)
    """
    try:
        user = get_current_user()

        # Get effective plan
        plan_info = BillingService.get_effective_plan_for_user(user['user_id'])

        # Get detailed subscription if exists
        subscription_data = None

        if plan_info['source'] == 'user':
            subscription_data = SubscriptionRepository.get_subscription_for_user(user['user_id'])
        elif plan_info['source'] == 'organisation':
            subscription_data = SubscriptionRepository.get_subscription_for_organisation(
                user['organization_id']
            )

        # Build response
        response = {
            'plan': plan_info['plan_name'],
            'tier': plan_info['tier'],
            'features': plan_info['features'],
            'source': plan_info['source']
        }

        if subscription_data:
            response['status'] = subscription_data['status']
            response['expires_at'] = (
                subscription_data['expires_at'].isoformat()
                if subscription_data.get('expires_at') else None
            )
            response['auto_renew'] = subscription_data.get('auto_renew', False)
            response['billing_cycle'] = subscription_data.get('billing_cycle')
            response['started_at'] = (
                subscription_data['started_at'].isoformat()
                if subscription_data.get('started_at') else None
            )
        else:
            response['status'] = 'none'
            response['expires_at'] = None
            response['auto_renew'] = False

        return jsonify({
            'success': True,
            'subscription': response
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get subscription',
            'details': str(e)
        }), 500


@profile_subscription_bp.route('/tokens', methods=['GET'])
@token_required
def get_token_balance():
    """
    Get current user's AI token balance

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Token balance information
        - balance: Current token balance
        - total_purchased: Total tokens purchased
        - total_granted: Total tokens granted (subscriptions, promos)
        - total_consumed: Total tokens consumed
        - monthly_grant: Monthly subscription token grant
        - source: Wallet source (user, organisation)
    """
    try:
        user = get_current_user()

        # Get effective plan to determine wallet source
        plan_info = BillingService.get_effective_plan_for_user(user['user_id'])

        # Determine which wallet to return
        if plan_info['source'] == 'organisation' and user.get('organization_id'):
            # Organisation wallet
            wallet = TokenRepository.get_or_create_organisation_wallet(user['organization_id'])
            source = 'organisation'
        else:
            # User wallet
            wallet = TokenRepository.get_or_create_user_wallet(user['user_id'])
            source = 'user'

        token_balance = {
            'balance': wallet['balance'],
            'reserved': wallet.get('reserved', 0),
            'available': wallet['balance'] - wallet.get('reserved', 0),
            'total_purchased': wallet['total_purchased'],
            'total_granted': wallet['total_granted'],
            'total_consumed': wallet['total_consumed'],
            'monthly_grant': wallet.get('monthly_grant_amount'),
            'last_grant_date': (
                wallet.get('last_grant_date').isoformat()
                if wallet.get('last_grant_date') else None
            ),
            'source': source
        }

        return jsonify({
            'success': True,
            'tokens': token_balance
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get token balance',
            'details': str(e)
        }), 500
