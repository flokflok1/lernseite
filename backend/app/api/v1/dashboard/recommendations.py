"""
LernsystemX Dashboard Recommendations API

KI recommendations endpoints:
- GET    /api/v1/dashboard/recommendations - Get recommendations
- POST   /api/v1/dashboard/recommendations/{id}/dismiss - Dismiss recommendation
- POST   /api/v1/dashboard/recommendations/{id}/accept - Accept recommendation
- GET    /api/v1/dashboard/recommendations/stats - Get stats

ISO 27001:2013 compliant - Recommendations API
"""

from flask import Blueprint, request, jsonify

from app.middleware.auth import token_required, get_current_user
from app.api.v1.dashboard.services import DashboardRecommendationService


recommendations_bp = Blueprint(
    'recommendations',
    __name__,
    url_prefix='/dashboard/recommendations'
)


@recommendations_bp.route('', methods=['GET'])
@token_required
def get_recommendations():
    """
    Get KI recommendations for user

    Headers:
        Authorization: Bearer <access_token>

    Query Parameters:
        limit: Max recommendations (default: 10)
        include_dismissed: Include dismissed (default: false)

    Response:
        200: List of recommendations
        403: User not Premium+ (no KI access)

    Example Response:
        {
            "success": true,
            "recommendations": [
                {
                    "recommendation_id": "uuid",
                    "recommendation_type": "course",
                    "target_type": "course",
                    "target_id": "uuid",
                    "score": 0.92,
                    "confidence": 0.87,
                    "reason": "Basierend auf deinem Interesse an IT-Netzwerken",
                    "context": {},
                    "created_at": "2026-01-02T10:00:00Z"
                }
            ],
            "count": 5
        }
    """
    try:
        user = get_current_user()
        limit = request.args.get('limit', 10, type=int)
        include_dismissed = request.args.get('include_dismissed', 'false').lower() == 'true'

        # Check Premium access
        user_role = user.get('role', 'free')
        if user_role not in ['premium', 'creator', 'teacher', 'school_admin', 'company_admin', 'admin']:
            return jsonify({
                'success': False,
                'error': 'Premium required',
                'message': 'KI recommendations require Premium subscription'
            }), 403

        recommendations = DashboardRecommendationService.get_recommendations(
            user,
            limit=limit,
            include_dismissed=include_dismissed
        )

        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get recommendations',
            'details': str(e)
        }), 500


@recommendations_bp.route('/<recommendation_id>/dismiss', methods=['POST'])
@token_required
def dismiss_recommendation(recommendation_id: str):
    """
    Dismiss a recommendation

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Recommendation dismissed
        404: Recommendation not found
    """
    try:
        user = get_current_user()

        success = DashboardRecommendationService.dismiss_recommendation(user, recommendation_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Recommendation dismissed'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Recommendation not found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to dismiss recommendation',
            'details': str(e)
        }), 500


@recommendations_bp.route('/<recommendation_id>/accept', methods=['POST'])
@token_required
def accept_recommendation(recommendation_id: str):
    """
    Accept a recommendation

    Enrolls user in course or performs action based on recommendation type.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Recommendation accepted
        404: Recommendation not found
    """
    try:
        user = get_current_user()

        result = DashboardRecommendationService.accept_recommendation(user, recommendation_id)

        return jsonify({
            'success': True,
            'message': 'Recommendation accepted',
            'result': result
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Not found',
            'message': str(e)
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to accept recommendation',
            'details': str(e)
        }), 500


@recommendations_bp.route('/stats', methods=['GET'])
@token_required
def get_recommendation_stats():
    """
    Get recommendation statistics

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Recommendation stats

    Example Response:
        {
            "success": true,
            "stats": {
                "total": 50,
                "accepted": 12,
                "dismissed": 8,
                "pending": 30,
                "acceptance_rate": 0.24
            }
        }
    """
    try:
        user = get_current_user()

        stats = DashboardRecommendationService.get_stats(user)

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get stats',
            'details': str(e)
        }), 500
