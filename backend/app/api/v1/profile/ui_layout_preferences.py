"""
LernsystemX Profile UI Layout Preferences API

UI layout and workspace configuration endpoints:
- GET    /api/v1/profile/preferences/window-sizes              - Get all UI layout preferences
- PUT    /api/v1/profile/preferences/window-sizes              - Update UI layout preference
- DELETE /api/v1/profile/preferences/window-sizes/<window_type> - Delete UI layout preference

ISO 27001:2013 compliant
Split from: profile.py (Part 3/4 - UI Layout)
"""

from flask import Blueprint, request, jsonify

from app.infrastructure.persistence.repositories.settings.user_preferences import UserPreferencesRepository
from app.api.middleware.auth import token_required, get_current_user

ui_layout_preferences_bp = Blueprint('profile_ui_layout', __name__, url_prefix='')


@ui_layout_preferences_bp.route('/preferences/window-sizes', methods=['GET'])
@token_required
def get_window_sizes():
    """
    Get current user's window size preferences

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Window sizes
            {
                "success": true,
                "window_sizes": {
                    "admin-model-selector": {"width": 800, "height": 600},
                    "admin-course-editor": {"width": 1200, "height": 800}
                }
            }
    """
    try:
        user = get_current_user()
        window_sizes = UserPreferencesRepository.get_window_sizes(user['user_id'])

        return jsonify({
            'success': True,
            'window_sizes': window_sizes
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get window sizes',
            'details': str(e)
        }), 500


@ui_layout_preferences_bp.route('/preferences/window-sizes', methods=['PUT'])
@token_required
def update_window_sizes():
    """
    Update window size for a specific window type

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "window_type": "admin-model-selector",
            "width": 900,
            "height": 700
        }

    Response:
        200: Window size updated
            {
                "success": true,
                "message": "Window size updated",
                "window_sizes": {...}
            }
        400: Invalid request
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate required fields
        window_type = data.get('window_type')
        width = data.get('width')
        height = data.get('height')

        if not window_type:
            return jsonify({
                'success': False,
                'error': 'window_type is required'
            }), 400

        if not isinstance(width, int) or not isinstance(height, int):
            return jsonify({
                'success': False,
                'error': 'width and height must be integers'
            }), 400

        # Validate minimum sizes
        if width < 400 or height < 300:
            return jsonify({
                'success': False,
                'error': 'Minimum window size is 400x300'
            }), 400

        # Update window size
        prefs = UserPreferencesRepository.update_window_size(
            user['user_id'],
            window_type,
            width,
            height
        )

        return jsonify({
            'success': True,
            'message': f'Window size for {window_type} updated',
            'window_sizes': prefs.get('window_sizes', {})
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update window size',
            'details': str(e)
        }), 500


@ui_layout_preferences_bp.route('/preferences/window-sizes/<window_type>', methods=['DELETE'])
@token_required
def delete_window_size(window_type: str):
    """
    Delete a specific window size preference

    Headers:
        Authorization: Bearer <access_token>

    URL Parameters:
        window_type: The window type to delete (e.g. admin-model-selector)

    Response:
        200: Window size deleted
        404: Window type not found in preferences
    """
    try:
        user = get_current_user()

        prefs = UserPreferencesRepository.delete_window_size(user['user_id'], window_type)

        if prefs:
            return jsonify({
                'success': True,
                'message': f'Window size for {window_type} deleted',
                'window_sizes': prefs.get('window_sizes', {})
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No preferences found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete window size',
            'details': str(e)
        }), 500


__all__ = ['ui_layout_preferences_bp']
