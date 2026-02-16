"""
LernsystemX Dashboard Widgets

Consolidated widget management endpoints:

Widget Registry:
- GET /api/v1/dashboard/widgets - Get available widgets for user's role

Widget Instances:
- GET    /api/v1/dashboard/widgets/user - Get user's widget instances
- POST   /api/v1/dashboard/widgets/add - Add widget to dashboard
- DELETE /api/v1/dashboard/widgets/{id} - Remove widget
- PATCH  /api/v1/dashboard/widgets/{id}/position - Update position (Drag & Drop)
- PATCH  /api/v1/dashboard/widgets/{id}/settings - Update custom settings
- PATCH  /api/v1/dashboard/widgets/{id}/toggle - Toggle visibility

Consolidated from:
- widgets/models.py (Pydantic models)
- widgets/registry.py (Widget registry endpoints)
- widgets/instances.py (Widget instance management endpoints)

ISO 27001:2013 compliant - Widget management
"""

from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError
from typing import Optional, Dict

from app.api.middleware.auth import token_required, get_current_user
from app.api.v1.panel.user.dashboard.shared.services import DashboardWidgetService


# ===== PYDANTIC MODELS =====

class AddWidgetRequest(BaseModel):
    """Request model for adding widget"""
    widget_key: str
    layout_id: Optional[str] = None
    position_x: int = 0
    position_y: int = 0
    width: int = 2
    height: int = 1
    custom_settings: Optional[Dict] = None


class UpdatePositionRequest(BaseModel):
    """Request model for updating widget position"""
    position_x: int
    position_y: int
    width: Optional[int] = None
    height: Optional[int] = None


class UpdateSettingsRequest(BaseModel):
    """Request model for updating widget settings"""
    custom_settings: Dict


# ===== BLUEPRINTS =====

widgets_registry_bp = Blueprint(
    'widgets_registry',
    __name__,
    url_prefix='/dashboard/widgets'
)

widgets_instances_bp = Blueprint(
    'widgets_instances',
    __name__,
    url_prefix='/dashboard/widgets'
)


# ===== WIDGET REGISTRY ENDPOINTS =====

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


# ===== WIDGET INSTANCE MANAGEMENT ENDPOINTS =====

@widgets_instances_bp.route('/user', methods=['GET'])
@token_required
def get_user_widgets():
    """
    Get user's widget instances

    Headers:
        Authorization: Bearer <access_token>

    Query Parameters:
        layout_id: Optional layout UUID

    Response:
        200: List of user's widgets

    Example Response:
        {
            "success": true,
            "widgets": [
                {
                    "instance_id": "uuid",
                    "widget_key": "ki_recommendations",
                    "position_x": 0,
                    "position_y": 0,
                    "width": 2,
                    "height": 2,
                    "is_visible": true,
                    "custom_settings": {}
                }
            ],
            "count": 8
        }
    """
    try:
        user = get_current_user()
        layout_id = request.args.get('layout_id')

        widgets = DashboardWidgetService.get_user_widgets(user, layout_id)

        return jsonify({
            'success': True,
            'widgets': widgets,
            'count': len(widgets)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get user widgets',
            'details': str(e)
        }), 500


@widgets_instances_bp.route('/add', methods=['POST'])
@token_required
def add_widget():
    """
    Add widget to dashboard

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "widget_key": "ki_recommendations",
            "layout_id": "uuid",
            "position_x": 0,
            "position_y": 0,
            "width": 2,
            "height": 2,
            "custom_settings": {}
        }

    Response:
        200: Widget added successfully
        403: User cannot customize dashboard (Free users)
        400: Validation error
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate request
        add_request = AddWidgetRequest(**data)

        # Add widget
        widget = DashboardWidgetService.add_widget(
            user=user,
            widget_key=add_request.widget_key,
            layout_id=add_request.layout_id,
            position_x=add_request.position_x,
            position_y=add_request.position_y,
            width=add_request.width,
            height=add_request.height,
            custom_settings=add_request.custom_settings
        )

        return jsonify({
            'success': True,
            'message': 'Widget added successfully',
            'widget': widget
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to add widget',
            'details': str(e)
        }), 500


@widgets_instances_bp.route('/<widget_instance_id>', methods=['DELETE'])
@token_required
def remove_widget(widget_instance_id: str):
    """
    Remove widget from dashboard

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Widget removed successfully
        403: Permission denied
        404: Widget not found
    """
    try:
        user = get_current_user()

        success = DashboardWidgetService.remove_widget(user, widget_instance_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Widget removed successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Widget not found'
            }), 404

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to remove widget',
            'details': str(e)
        }), 500


@widgets_instances_bp.route('/<widget_instance_id>/position', methods=['PATCH'])
@token_required
def update_widget_position(widget_instance_id: str):
    """
    Update widget position (Drag & Drop)

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "position_x": 4,
            "position_y": 2,
            "width": 2,
            "height": 1
        }

    Response:
        200: Position updated successfully
        403: Permission denied
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate request
        position_request = UpdatePositionRequest(**data)

        # Update position
        widget = DashboardWidgetService.update_widget_position(
            user=user,
            widget_instance_id=widget_instance_id,
            position_x=position_request.position_x,
            position_y=position_request.position_y,
            width=position_request.width,
            height=position_request.height
        )

        return jsonify({
            'success': True,
            'message': 'Widget position updated',
            'widget': widget
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update position',
            'details': str(e)
        }), 500


@widgets_instances_bp.route('/<widget_instance_id>/settings', methods=['PATCH'])
@token_required
def update_widget_settings(widget_instance_id: str):
    """
    Update widget settings

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "custom_settings": {
                "theme": "dark",
                "show_details": true
            }
        }

    Response:
        200: Settings updated successfully
        403: Permission denied
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate request
        settings_request = UpdateSettingsRequest(**data)

        # Update settings
        widget = DashboardWidgetService.update_widget_settings(
            user=user,
            widget_instance_id=widget_instance_id,
            custom_settings=settings_request.custom_settings
        )

        return jsonify({
            'success': True,
            'message': 'Widget settings updated',
            'widget': widget
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update settings',
            'details': str(e)
        }), 500


@widgets_instances_bp.route('/<widget_instance_id>/toggle', methods=['PATCH'])
@token_required
def toggle_widget_visibility(widget_instance_id: str):
    """
    Toggle widget visibility

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Visibility toggled
        403: Permission denied
    """
    try:
        user = get_current_user()

        is_visible = DashboardWidgetService.toggle_widget_visibility(user, widget_instance_id)

        return jsonify({
            'success': True,
            'message': 'Widget visibility toggled',
            'is_visible': is_visible
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to toggle visibility',
            'details': str(e)
        }), 500
