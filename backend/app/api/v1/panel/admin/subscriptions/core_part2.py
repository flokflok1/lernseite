"""
LernsystemX Subscriptions API - Cancel, Reactivate & Admin Routes (Part 2)

User Billing Operations:
- POST /subscriptions/cancel - Cancel subscription
- POST /subscriptions/reactivate - Reactivate cancelled subscription

Admin Management:
- GET /subscriptions/stats - Get subscription statistics
- GET /subscriptions/expiring - Get subscriptions expiring soon

See core.py for subscription info, plans, and change routes.

All routes: /api/v1/subscriptions/*
ISO 27001:2013 compliant - Subscription and billing security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from datetime import datetime
from flask import request, jsonify
from pydantic import ValidationError

from app.domain.models.schemas.subscription import (
    SubscriptionCancelRequest,
    SubscriptionStats,
)
from app.infrastructure.persistence.repositories.subscription import SubscriptionRepository
from app.api.middleware.auth import token_required, get_current_user, admin_required
from app.api.v1.panel.admin.subscriptions.core import subscriptions_bp


# =============================================================================
# USER - BILLING OPERATIONS (continued)
# =============================================================================

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
            if user.get('organisation_id'):
                org_sub = SubscriptionRepository.get_subscription_for_organisation(
                    user['organisation_id']
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
