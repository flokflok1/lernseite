"""
LernsystemX Subscriptions API - Billing Operations

User subscription billing endpoints:
- POST /api/v1/subscriptions/change - Change subscription plan
- POST /api/v1/subscriptions/cancel - Cancel subscription
- POST /api/v1/subscriptions/reactivate - Reactivate cancelled subscription

ISO 27001:2013 compliant - Subscription and billing security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.subscription import (
    SubscriptionResponse,
    SubscriptionChangeRequest,
    SubscriptionCancelRequest
)
from app.repositories.subscription import SubscriptionRepository
from app.services.billing_service import BillingService
from app.middleware.auth import token_required, get_current_user


subscriptions_billing_bp = Blueprint(
    'subscriptions_billing',
    __name__,
    url_prefix='/subscriptions'
)
@subscriptions_billing_bp.route('/change', methods=['POST'])
@token_required
def change_subscription():
    """
    Change subscription plan

    Only available for users with direct subscriptions (not organisation subscriptions).
    Organisation admins should use organisation management endpoints.

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "new_plan_id": 3,
            "reason": "Upgrade to Creator plan",
            "prorate": true
        }

    Response:
        200: Subscription changed successfully
        400: Validation error or invalid plan change
        403: Not allowed (organisation subscription or no permission)
        404: No active subscription to change
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate request
        change_request = SubscriptionChangeRequest(**data)

        # Check if user has direct subscription
        subscription = SubscriptionRepository.get_subscription_for_user(user['user_id'])

        if not subscription:
            # Check if user has organisation subscription
            if user.get('organization_id'):
                org_sub = SubscriptionRepository.get_subscription_for_organisation(
                    user['organization_id']
                )
                if org_sub:
                    return jsonify({
                        'success': False,
                        'error': 'Forbidden',
                        'message': 'Your subscription is managed by your organisation. Contact your organisation admin to change plans.'
                    }), 403

            return jsonify({
                'success': False,
                'error': 'No subscription found',
                'message': 'You do not have an active subscription to change. Please create a subscription first.'
            }), 404

        # Verify subscription is active
        if subscription['status'] not in ['active', 'trial']:
            return jsonify({
                'success': False,
                'error': 'Subscription not active',
                'message': f'Cannot change subscription with status: {subscription["status"]}'
            }), 400

        # Verify new plan exists and is active
        new_plan = SubscriptionRepository.get_plan_by_id(change_request.new_plan_id)

        if not new_plan or not new_plan.get('active', False):
            return jsonify({
                'success': False,
                'error': 'Invalid plan',
                'message': 'The selected plan is not available'
            }), 400

        # Verify not changing to same plan
        if subscription['plan_id'] == change_request.new_plan_id:
            return jsonify({
                'success': False,
                'error': 'Same plan',
                'message': 'You are already on this plan'
            }), 400

        # Change subscription
        updated_subscription = SubscriptionRepository.change_subscription(
            subscription_id=subscription['subscription_id'],
            new_plan_id=change_request.new_plan_id,
            reason=change_request.reason
        )

        # Get updated subscription with plan details
        updated_with_plan = SubscriptionRepository.get_subscription_for_user(user['user_id'])

        # Convert to response model
        subscription_response = SubscriptionResponse(**updated_with_plan)

        # TODO: Handle proration logic
        # TODO: Send confirmation email
        # TODO: Log subscription change event

        return jsonify({
            'success': True,
            'message': f'Subscription changed to {new_plan["name"]} plan',
            'subscription': subscription_response.model_dump()
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to change subscription',
            'details': str(e)
        }), 500


@subscriptions_billing_bp.route('/cancel', methods=['POST'])
@token_required
def cancel_subscription():
    """
    Cancel subscription

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "reason": "Too expensive",
            "immediate": false,
            "feedback": "Would reconsider if price was lower"
        }

    Response:
        200: Subscription cancelled
        403: Organisation subscription (not allowed)
        404: No subscription to cancel
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate request
        cancel_request = SubscriptionCancelRequest(**data)

        # Get user's subscription
        subscription = SubscriptionRepository.get_subscription_for_user(user['user_id'])

        if not subscription:
            # Check if organisation subscription
            if user.get('organization_id'):
                org_sub = SubscriptionRepository.get_subscription_for_organisation(
                    user['organization_id']
                )
                if org_sub:
                    return jsonify({
                        'success': False,
                        'error': 'Forbidden',
                        'message': 'Your subscription is managed by your organisation. Contact your organisation admin.'
                    }), 403

            return jsonify({
                'success': False,
                'error': 'No subscription',
                'message': 'You do not have an active subscription to cancel'
            }), 404

        # Cancel subscription
        cancelled_subscription = SubscriptionRepository.cancel_subscription(
            subscription_id=subscription['subscription_id'],
            reason=cancel_request.reason,
            immediate=cancel_request.immediate
        )

        # TODO: Send cancellation confirmation email
        # TODO: Log cancellation event
        # TODO: Store feedback for analysis

        if cancel_request.immediate:
            message = 'Your subscription has been cancelled immediately. You no longer have access to premium features.'
        else:
            message = f'Your subscription will be cancelled at the end of the billing period ({subscription["expires_at"]}). You can continue using premium features until then.'

        return jsonify({
            'success': True,
            'message': message,
            'cancelled_at': cancelled_subscription['cancelled_at'].isoformat() if cancelled_subscription.get('cancelled_at') else None,
            'expires_at': cancelled_subscription['expires_at'].isoformat() if cancelled_subscription.get('expires_at') else None
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to cancel subscription',
            'details': str(e)
        }), 500


@subscriptions_billing_bp.route('/reactivate', methods=['POST'])
@token_required
def reactivate_subscription():
    """
    Reactivate cancelled subscription

    Only works if subscription hasn't expired yet.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Subscription reactivated
        400: Subscription already active or expired
        404: No subscription found
    """
    try:
        user = get_current_user()

        # Get user's subscription
        subscription = SubscriptionRepository.get_subscription_for_user(user['user_id'])

        if not subscription:
            return jsonify({
                'success': False,
                'error': 'No subscription',
                'message': 'You do not have a subscription to reactivate'
            }), 404

        # Check if subscription is cancelled
        if subscription['status'] != 'cancelled':
            return jsonify({
                'success': False,
                'error': 'Not cancelled',
                'message': f'Subscription is {subscription["status"]}, not cancelled'
            }), 400

        # Check if subscription hasn't expired yet
        if subscription.get('expires_at') and subscription['expires_at'] < datetime.now():
            return jsonify({
                'success': False,
                'error': 'Expired',
                'message': 'Subscription has expired and cannot be reactivated. Please create a new subscription.'
            }), 400

        # Reactivate subscription
        reactivated_subscription = SubscriptionRepository.reactivate_subscription(
            subscription['subscription_id']
        )

        # TODO: Send reactivation confirmation email
        # TODO: Log reactivation event

        return jsonify({
            'success': True,
            'message': 'Your subscription has been reactivated successfully',
            'subscription': {
                'status': reactivated_subscription['status'],
                'auto_renew': reactivated_subscription['auto_renew'],
                'expires_at': reactivated_subscription['expires_at'].isoformat() if reactivated_subscription.get('expires_at') else None
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to reactivate subscription',
            'details': str(e)
        }), 500
