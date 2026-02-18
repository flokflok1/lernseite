"""
LernsystemX Dashboard Layouts API

Dashboard layout management endpoints:
- GET    /api/v1/dashboard/layout - Get user's dashboard layout
- PUT    /api/v1/dashboard/layout - Save user's dashboard layout
- POST   /api/v1/dashboard/layout/reset - Reset layout to default

ISO 27001:2013 compliant - Dashboard layout management
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.domain.models.schemas.dashboard import (
    DashboardLayout,
    DashboardLayoutSaveRequest,
    DashboardLayoutResponse,
    DashboardLayoutResetResponse
)
from app.api.v1.panel.user.dashboard.shared.services import DashboardLayoutService
from app.api.middleware.auth import token_required, get_current_user


layouts_bp = Blueprint('layouts', __name__, url_prefix='/dashboard/layout')


@layouts_bp.route('', methods=['GET'])
@token_required
def get_dashboard_layout():
    """
    Get user's dashboard layout

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Dashboard layout
        - If user has custom layout: returns saved layout
        - If no custom layout: returns default layout for role
        - Free users always get role default (no custom layouts)

    Example Response:
        {
            "success": true,
            "layout": {
                "userId": 123,
                "role": "premium",
                "widgets": [
                    {
                        "instanceId": "premium-welcome",
                        "widgetId": "welcome",
                        "order": 0,
                        "visible": true
                    },
                    ...
                ],
                "presetId": "premium-default",
                "updatedAt": "2025-11-16T10:30:00",
                "version": 1
            }
        }
    """
    try:
        user = get_current_user()

        # Get effective layout (custom or default)
        layout = DashboardLayoutService.get_effective_layout(user)

        return jsonify({
            'success': True,
            'layout': layout.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get dashboard layout',
            'details': str(e)
        }), 500


@layouts_bp.route('', methods=['PUT'])
@token_required
def save_dashboard_layout():
    """
    Save user's dashboard layout

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "widgets": [
                {
                    "instanceId": "user-welcome",
                    "widgetId": "welcome",
                    "order": 0,
                    "visible": true,
                    "config": {}
                },
                ...
            ],
            "presetId": null
        }

    Response:
        200: Layout saved successfully
        403: User role cannot customize dashboard (Free users)
        400: Validation error

    Permissions:
        - Premium, Creator, Teacher, School Admin, Company Admin, Admin: Can save
        - Free, Moderator, Support: Cannot save (403)
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate request body
        save_request = DashboardLayoutSaveRequest(**data)

        # Build complete layout object
        layout = DashboardLayout(
            userId=user['user_id'],
            role=user.get('role', 'user'),
            widgets=save_request.widgets,
            presetId=save_request.presetId,
            version=1
        )

        # Save layout (includes permission check)
        saved_layout = DashboardLayoutService.save_layout(user, layout)

        return jsonify({
            'success': True,
            'message': 'Dashboard layout saved successfully',
            'layout': saved_layout.model_dump()
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

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
            'error': 'Failed to save dashboard layout',
            'details': str(e)
        }), 500


@layouts_bp.route('/reset', methods=['POST'])
@token_required
def reset_dashboard_layout():
    """
    Reset dashboard layout to default

    Deletes user's custom layout.
    Next GET /dashboard/layout will return role default.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Layout reset successfully
        403: User role cannot reset dashboard (Free users)

    Example Response:
        {
            "success": true,
            "message": "Dashboard layout reset to default",
            "layout": {
                "userId": 123,
                "role": "premium",
                "widgets": [...],
                "presetId": "premium-default",
                "source": "role",
                "isDefault": true
            }
        }

    Permissions:
        - Premium, Creator, Teacher, School Admin, Company Admin, Admin: Can reset
        - Free, Moderator, Support: Cannot reset (403)
    """
    try:
        user = get_current_user()

        # Reset layout (includes permission check)
        default_layout = DashboardLayoutService.reset_layout(user)

        return jsonify({
            'success': True,
            'message': 'Dashboard layout reset to default',
            'layout': default_layout.model_dump()
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to reset dashboard layout',
            'details': str(e)
        }), 500
