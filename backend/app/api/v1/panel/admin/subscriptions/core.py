"""
LernsystemX Subscriptions API - Core Routes (Part 1)

User Subscription Information:
- GET /subscriptions/me - Get current user's subscription

Public Plans:
- GET /subscriptions/plans - List all subscription plans

User Billing Operations:
- POST /subscriptions/change - Change subscription plan

See core_part2.py for cancel, reactivate, and admin routes.

All routes: /api/v1/subscriptions/*
ISO 27001:2013 compliant - Subscription and billing security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.domain.models.schemas.subscription import (
    SubscriptionResponse,
    SubscriptionChangeRequest,
    SubscriptionPlanResponse,
)
from app.infrastructure.persistence.repositories.subscription import SubscriptionRepository
from app.application.services.system.billing.service import BillingService
from app.api.middleware.auth import token_required, get_current_user

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
                user['organisation_id']
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
                'organisation_id': str(subscription_data.get('organisation_id', '')) if subscription_data.get('organisation_id') else None,
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
            if user.get('organisation_id'):
                org_sub = SubscriptionRepository.get_subscription_for_organisation(
                    user['organisation_id']
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
