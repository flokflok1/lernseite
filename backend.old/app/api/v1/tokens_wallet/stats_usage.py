"""
LernsystemX Tokens Statistics API

Token usage statistics and cost estimation endpoints.

Endpoints:
- GET /api/v1/tokens/usage - Get current user's token usage analytics
- POST /api/v1/tokens/estimate - Estimate AI token cost
"""

from flask import Blueprint, request, jsonify

from app.models.token import TokenUsageStats
from app.repositories.token import TokenRepository
from app.services.billing_service import BillingService
from app.middleware.auth import token_required, get_current_user


tokens_stats_bp = Blueprint(
    'tokens_stats',
    __name__,
    url_prefix='/tokens'
)


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@tokens_stats_bp.route('/usage', methods=['GET'])
@token_required
def get_my_usage():
    """
    Get current user's token usage statistics

    Headers:
        Authorization: Bearer <access_token>

    Query Parameters:
        period_days: Statistics period in days (default: 30)

    Response:
        200: Token usage statistics
        {
            "success": true,
            "stats": {
                "user_id": 42,
                "current_balance": 8500,
                "total_tokens_used": 15000,
                "total_tokens_bought": 20000,
                "total_tokens_granted": 10000,
                "by_reason": {
                    "ai_execution": 15000
                },
                "by_method": {
                    "KI-Tutor": 8000,
                    "KI-Glossar": 7000
                },
                "period_start": "2024-12-16T00:00:00",
                "period_end": "2025-01-15T00:00:00"
            }
        }
    """
    try:
        user = get_current_user()

        # Get query parameters
        period_days = int(request.args.get('period_days', 30))

        # Get usage statistics
        stats = TokenRepository.get_user_token_stats(
            user_id=user['user_id'],
            period_days=period_days
        )

        # Convert to response model
        stats_response = TokenUsageStats(**stats)

        return jsonify({
            'success': True,
            'stats': stats_response.model_dump(),
            'period_days': period_days
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get usage statistics',
            'details': str(e)
        }), 500


@tokens_stats_bp.route('/estimate', methods=['POST'])
@token_required
def estimate_ai_cost():
    """
    Estimate AI token cost for a method

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "method_name": "KI-Tutor",
            "complexity": "medium"  // simple, medium, complex
        }

    Response:
        200: Estimated token cost
        {
            "success": true,
            "estimate": {
                "method_name": "KI-Tutor",
                "complexity": "medium",
                "estimated_tokens": 500,
                "can_afford": true,
                "current_balance": 8500
            }
        }
    """
    try:
        user = get_current_user()
        data = request.get_json()

        method_name = data.get('method_name')
        complexity = data.get('complexity', 'medium')

        if not method_name:
            return jsonify({
                'success': False,
                'error': 'Missing method_name',
                'message': 'Please provide a method_name to estimate cost'
            }), 400

        # Estimate cost
        estimated_tokens = BillingService.estimate_ai_cost(method_name, complexity)

        # Check if user can afford
        can_afford = BillingService.can_user_afford(user['user_id'], estimated_tokens)

        # Get current balance
        wallet = TokenRepository.get_or_create_user_wallet(user['user_id'])

        return jsonify({
            'success': True,
            'estimate': {
                'method_name': method_name,
                'complexity': complexity,
                'estimated_tokens': estimated_tokens,
                'can_afford': can_afford,
                'current_balance': wallet['balance']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to estimate cost',
            'details': str(e)
        }), 500
