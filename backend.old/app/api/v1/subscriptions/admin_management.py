"""
LernsystemX Subscriptions API - Admin Module

Admin-only subscription management endpoints:
- GET /api/v1/subscriptions/stats - Get subscription statistics
- GET /api/v1/subscriptions/expiring - Get subscriptions expiring soon

ISO 27001:2013 compliant - Subscription and billing security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, request, jsonify

from app.models.subscription import SubscriptionStats
from app.repositories.subscription import SubscriptionRepository
from app.middleware.auth import token_required, admin_required


subscriptions_admin_bp = Blueprint(
    'subscriptions_admin',
    __name__,
    url_prefix='/subscriptions'
)


@subscriptions_admin_bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def get_subscription_stats():
    """
    Get subscription statistics (admin only)

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Subscription statistics
        {
            "success": true,
            "stats": {
                "total_subscribers": 1523,
                "active_subscribers": 1342,
                "trial_subscribers": 54,
                "cancelled_subscribers": 127,
                "by_plan": {
                    "free": 500,
                    "premium": 800,
                    "creator": 42
                },
                "by_status": {
                    "active": 1342,
                    "trial": 54,
                    "cancelled": 127
                },
                "mrr": 18950.58,
                "arr": 227406.96
            }
        }
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


@subscriptions_admin_bp.route('/expiring', methods=['GET'])
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
