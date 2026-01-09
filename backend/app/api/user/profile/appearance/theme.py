"""
LernsystemX Profile Theme API

Theme preference endpoints (Phase B24 - Theme Support):
- GET   /api/v1/profile/theme - Get theme preference
- PATCH /api/v1/profile/theme - Update theme preference

ISO 27001:2013 compliant - User preference management
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.user import (
    ThemePreferenceResponse,
    ThemePreferenceUpdateRequest
)
from app.repositories.user import UserRepository
from app.services.audit_service import AuditService, Severity
from app.middleware.auth import token_required, get_current_user


profile_theme_bp = Blueprint('profile_theme', __name__, url_prefix='/profile')


@profile_theme_bp.route('/theme', methods=['GET'])
@token_required
def get_theme_preference():
    """
    Get current user's theme preference

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Theme preference
            {
                "theme": "dark" | "light" | "system"
            }
        500: Server error

    Example:
        >>> GET /api/v1/profile/theme
        >>> Headers: Authorization: Bearer <token>
        >>> Response: {"theme": "dark"}
    """
    try:
        user = get_current_user()

        # Get theme preference from repository
        theme = UserRepository.get_theme_preference(user['user_id'])

        # Create response
        response = ThemePreferenceResponse(theme=theme)

        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get theme preference',
            'details': str(e)
        }), 500


@profile_theme_bp.route('/theme', methods=['PATCH'])
@token_required
def update_theme_preference():
    """
    Update current user's theme preference

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "theme": "dark" | "light" | "system"
        }

    Response:
        200: Theme updated successfully
            {
                "theme": "dark" | "light" | "system"
            }
        400: Validation error (invalid theme value)
        401: Not authenticated
        500: Server error

    Example:
        >>> PATCH /api/v1/profile/theme
        >>> Headers: Authorization: Bearer <token>
        >>> Body: {"theme": "light"}
        >>> Response: {"theme": "light"}
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate with Pydantic
        theme_request = ThemePreferenceUpdateRequest(**data)

        # Get current theme for audit log
        old_theme = UserRepository.get_theme_preference(user['user_id'])

        # Update theme preference
        new_theme = UserRepository.update_theme_preference(
            user['user_id'],
            theme_request.theme
        )

        # Audit log: Theme preference changed
        AuditService.log_event(
            event_type='preferences',
            event_category='data_modification',
            action='change_theme',
            severity=Severity.INFO,
            user_id=user.get('user_id'),
            user_email=user.get('email'),
            user_role=user.get('role'),
            resource_type='user_preferences',
            resource_id=str(user['user_id']),
            description=f"User changed theme from '{old_theme}' to '{new_theme}'",
            metadata={
                'old_theme': old_theme,
                'new_theme': new_theme
            },
            success=True
        )

        # Create response
        response = ThemePreferenceResponse(theme=new_theme)

        return jsonify(response.model_dump()), 200

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
            'error': 'Failed to update theme preference',
            'details': str(e)
        }), 500
