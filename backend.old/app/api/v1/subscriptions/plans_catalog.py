"""
LernsystemX Subscriptions API - Plans Module

Public subscription plan endpoints:
- GET /api/v1/subscriptions/plans - List all subscription plans (public)

ISO 27001:2013 compliant - Subscription and billing security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, request, jsonify

from app.models.subscription import SubscriptionPlanResponse
from app.repositories.subscription import SubscriptionRepository


subscriptions_plans_bp = Blueprint(
    'subscriptions_plans',
    __name__,
    url_prefix='/subscriptions'
)


@subscriptions_plans_bp.route('/plans', methods=['GET'])
def list_subscription_plans():
    """
    List all subscription plans

    Query Parameters:
        active_only: Only return active plans (default: true)

    Response:
        200: List of subscription plans
        {
            "success": true,
            "plans": [
                {
                    "plan_id": 1,
                    "name": "premium",
                    "tier": "premium",
                    "monthly_price_eur": 14.99,
                    "yearly_price_eur": 129.99,
                    "included_tokens": 10000,
                    "features": {
                        "ai_access": true,
                        "learning_methods": 21,
                        "course_creation": true
                    },
                    "active": true
                }
            ],
            "total": 6
        }
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
