"""
LernsystemX Dashboard Widgets - Registry

Widget registry endpoints:
- GET /api/v1/dashboard/widgets - Get available widgets for user's role

ISO 27001:2013 compliant - Widget registry
"""

from flask import Blueprint, jsonify

from app.middleware.auth import token_required, get_current_user
from app.api.user.dashboard.core import DashboardDashboardWidgetService


widgets_registry_bp = Blueprint(
    'widgets_registry',
    __name__,
    url_prefix='/dashboard/widgets'
)


@widgets_registry_bp.route('', methods=['GET'])
@token_required
def get_available_widgets():
    """
    Get all widgets available for user's role

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: List of available widgets

    Example Response:
        {
            "success": true,
            "widgets": [
                {
                    "widget_key": "ki_recommendations",
                    "widget_name": "KI Recommendations",
                    "description": "Personalisierte Kursvorschläge",
                    "category": "learning",
                    "requires_premium": true,
                    "default_width": 2,
                    "default_height": 2,
                    "is_available": true
                }
            ],
            "count": 15
        }
    """
    try:
        user = get_current_user()

        widgets = DashboardWidgetService.get_available_widgets(user)

        return jsonify({
            'success': True,
            'widgets': widgets,
            'count': len(widgets)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get available widgets',
            'details': str(e)
        }), 500
