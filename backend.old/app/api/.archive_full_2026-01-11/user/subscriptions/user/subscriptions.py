"""
LernsystemX Subscriptions API - User Subscriptions

User subscription information endpoint:
- GET  /api/v1/subscriptions/me - Get current user's subscription

ISO 27001:2013 compliant - Subscription and billing security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, jsonify
from pydantic import ValidationError

from app.models.subscription import SubscriptionResponse
from app.repositories.subscription import SubscriptionRepository
from app.services.billing_service import BillingService
from app.middleware.auth import token_required, get_current_user


subscriptions_info_bp = Blueprint(
    'subscriptions_info',
    __name__,
    url_prefix='/subscriptions'
)


@subscriptions_info_bp.route('/me', methods=['GET'])
@token_required
def get_my_subscription():
    """
    Get current user's subscription

    Checks user's direct subscription first, then organisation subscription.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Subscription information
        {
            "success": true,
            "subscription": {
                "subscription_id": 123,
                "plan_name": "premium",
                "tier": "premium",
                "status": "active",
                "billing_cycle": "monthly",
                "started_at": "2025-01-01T00:00:00",
                "expires_at": "2025-02-01T00:00:00",
                "auto_renew": true,
                "features": {
                    "ai_access": true,
                    "learning_methods": 21
                }
            },
            "source": "user"  // or "organisation" or "default"
        }

        404: No subscription found (returns free plan as default)
    """
    try:
        user = get_current_user()

        # Get effective plan for user
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
            'success': True,
            'plan': plan_info['plan_name'],
            'tier': plan_info['tier'],
            'features': plan_info['features'],
            'source': plan_info['source']
        }

        if subscription_data:
            # Format subscription data for response (handle UUID and column name differences)
            response['subscription'] = {
                'subscription_id': str(subscription_data.get('subscription_id', '')),
                'user_id': str(subscription_data.get('user_id', '')) if subscription_data.get('user_id') else None,
                'organization_id': str(subscription_data.get('organization_id', '')) if subscription_data.get('organization_id') else None,
                'plan_id': str(subscription_data.get('plan_id', '')) if subscription_data.get('plan_id') else None,
                'plan_type': subscription_data.get('plan_type'),
                'plan_name': subscription_data.get('plan_name'),
                'status': subscription_data.get('status'),
                'billing_cycle': subscription_data.get('billing_cycle'),
                'price': float(subscription_data.get('price', 0)) if subscription_data.get('price') else 0,
                'current_period_start': subscription_data.get('current_period_start').isoformat() if subscription_data.get('current_period_start') else None,
                'current_period_end': subscription_data.get('current_period_end').isoformat() if subscription_data.get('current_period_end') else None,
                'cancel_at_period_end': subscription_data.get('cancel_at_period_end', False),
                'plan_features': subscription_data.get('plan_features', {}),
                'included_tokens': subscription_data.get('included_tokens', 0),
                'created_at': subscription_data.get('created_at').isoformat() if subscription_data.get('created_at') else None
            }
        else:
            # Free plan - no subscription record
            response['subscription'] = None
            response['message'] = 'No active subscription. You are on the free plan.'

        return jsonify(response), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to get subscription',
            'details': str(e)
        }), 500

