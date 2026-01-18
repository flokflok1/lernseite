"""
LernsystemX Subscriptions API - Consolidated

User Subscription Information:
- GET /subscriptions/me - Get current user's subscription

Public Plans:
- GET /subscriptions/plans - List all subscription plans

User Billing Operations:
- POST /subscriptions/change - Change subscription plan
- POST /subscriptions/cancel - Cancel subscription
- POST /subscriptions/reactivate - Reactivate cancelled subscription

Admin Management:
- GET /subscriptions/stats - Get subscription statistics
- GET /subscriptions/expiring - Get subscriptions expiring soon

All routes: /api/v1/subscriptions/*
ISO 27001:2013 compliant - Subscription and billing security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.domain.models.subscription import (
    SubscriptionResponse,
    SubscriptionChangeRequest,
    SubscriptionCancelRequest,
    SubscriptionPlanResponse,
    SubscriptionStats
)
from app.infrastructure.persistence.repositories.subscription import SubscriptionRepository
from app.services.system.billing.service import BillingService
from app.api.middleware.auth import token_required, get_current_user, admin_required

subscriptions_bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')

__all__ = ['subscriptions_bp']


# =============================================================================
# USER - SUBSCRIPTION INFORMATION
# =============================================================================

@subscriptions_bp.route('/me', methods=['GET'])
@token_required
def get_my_subscription():
    """
    Get current user's subscription

    Checks user's direct subscription first, then organisation subscription.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Subscription information
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


# =============================================================================
# PUBLIC - SUBSCRIPTION PLANS
# =============================================================================

@subscriptions_bp.route('/plans', methods=['GET'])
def list_subscription_plans():
    """
    List all subscription plans

    Query Parameters:
        active_only: Only return active plans (default: true)

    Response:
        200: List of subscription plans
    """
    try:
        # Get query parameters
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        # Get all plans
        plans = SubscriptionRepository.get_all_plans(active_only)

        # Convert to response models
        plan_responses = [SubscriptionPlanResponse(**plan) for plan in plans]

        return jsonify({
            'success': True,
            'plans': [p.model_dump() for p in plan_responses],
            'total': len(plans)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list subscription plans',
            'details': str(e)
        }), 500


# =============================================================================
# USER - BILLING OPERATIONS
# =============================================================================

@subscriptions_bp.route('/change', methods=['POST'])
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


@subscriptions_bp.route('/cancel', methods=['POST'])
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


@subscriptions_bp.route('/reactivate', methods=['POST'])
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


# =============================================================================
# ADMIN - MANAGEMENT & STATISTICS
# =============================================================================

@subscriptions_bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def get_subscription_stats():
    """
    Get subscription statistics (admin only)

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Subscription statistics
    """
    try:
        # Get subscription statistics
        stats = SubscriptionRepository.get_subscription_stats()

        # Convert to response model
        stats_response = SubscriptionStats(**stats)

        return jsonify({
            'success': True,
            'stats': stats_response.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get subscription statistics',
            'details': str(e)
        }), 500


@subscriptions_bp.route('/expiring', methods=['GET'])
@token_required
@admin_required
def get_expiring_subscriptions():
    """
    Get subscriptions expiring soon (admin only)

    Query Parameters:
        days: Days until expiry (default: 3)

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: List of expiring subscriptions
    """
    try:
        # Get query parameters
        days = int(request.args.get('days', 3))

        # Get expiring subscriptions
        expiring = SubscriptionRepository.get_expiring_subscriptions(days)

        return jsonify({
            'success': True,
            'subscriptions': expiring,
            'total': len(expiring),
            'days': days
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get expiring subscriptions',
            'details': str(e)
        }), 500
