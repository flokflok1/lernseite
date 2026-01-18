"""
LernsystemX Admin API - System Settings

Admin endpoints for system configuration:
- Environment switching (Dev/Prod)
- Maintenance mode management
- System status monitoring
- Settings management

ISO 27001:2013 compliant - Admin API
"""

from flask import request, jsonify
from pydantic import ValidationError

from .system_operations import api_v1
from app.middleware.auth import token_required, admin_required, get_current_user
from app.services.system.system_mode_service import SystemModeService
from app.repositories.settings.system import SystemSettingsRepository
from app.domain.models.system_settings import (
    SwitchModeRequest,
    MaintenanceModeRequest,
    UpdateSettingRequest
)


# ============================================================================
# Environment Management
# ============================================================================

@api_v1.route('/admin/settings/system/mode', methods=['POST'])
@token_required
@admin_required
def switch_system_mode():
    """
    Switch system environment mode (development/production)

    Request Body:
        {
            "mode": "development"|"production"
        }

    Response:
        200: Mode switched successfully
        400: Validation error or already in target mode
        403: Forbidden (requires admin role)
        500: Server error
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate request
        mode_request = SwitchModeRequest(**data)

        # Switch mode
        result = SystemModeService.switch_environment(
            environment=mode_request.mode,
            user_id=user.get('user_id')
        )

        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'previous_environment': result['previous_environment'],
                'new_environment': result['new_environment'],
                'requires_restart': result['requires_restart'],
                'restart_instructions': result['restart_instructions']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to switch mode')
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
            'error': 'Failed to switch mode',
            'details': str(e)
        }), 500


# ============================================================================
# Maintenance Mode
# ============================================================================

@api_v1.route('/admin/settings/system/maintenance', methods=['POST'])
@token_required
@admin_required
def toggle_maintenance_mode():
    """
    Enable or disable maintenance mode

    Request Body:
        {
            "enabled": true|false,
            "message": "Custom message" (optional)
        }

    Response:
        200: Maintenance mode toggled successfully
        400: Validation error
        403: Forbidden (requires admin role)
        500: Server error
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate request
        maintenance_request = MaintenanceModeRequest(**data)

        # Toggle maintenance mode
        result = SystemModeService.toggle_maintenance(
            enabled=maintenance_request.enabled,
            message=maintenance_request.message,
            user_id=user.get('user_id')
        )

        return jsonify({
            'success': True,
            'message': result['message'],
            'maintenance_enabled': result['maintenance_enabled'],
            'maintenance_message': result['maintenance_message'],
            'debug_auto_enabled': result.get('debug_auto_enabled', False)
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
            'error': 'Failed to toggle maintenance mode',
            'details': str(e)
        }), 500


# ============================================================================
# System Status
# ============================================================================

@api_v1.route('/admin/settings/system/status', methods=['GET'])
@token_required
@admin_required
def get_system_status():
    """
    Get comprehensive system status

    Response:
        200: System status retrieved
        403: Forbidden (requires admin role)
        500: Server error
    """
    try:
        status = SystemModeService.get_system_status()

        return jsonify({
            'success': True,
            'status': status
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get system status',
            'details': str(e)
        }), 500


# ============================================================================
# Settings Management
# ============================================================================

@api_v1.route('/admin/settings/system/settings', methods=['GET'])
@token_required
@admin_required
def get_all_settings():
    """
    Get all system settings

    Query Parameters:
        category: Optional category filter

    Response:
        200: Settings retrieved
        403: Forbidden (requires admin role)
        500: Server error
    """
    try:
        category = request.args.get('category')

        settings = SystemSettingsRepository.get_all_settings(category=category)

        return jsonify({
            'success': True,
            'settings': settings,
            'count': len(settings)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get settings',
            'details': str(e)
        }), 500


@api_v1.route('/admin/settings/system/settings/<key>', methods=['GET'])
@token_required
@admin_required
def get_setting(key: str):
    """
    Get single setting by key

    Response:
        200: Setting retrieved
        404: Setting not found
        403: Forbidden (requires admin role)
        500: Server error
    """
    try:
        setting = SystemSettingsRepository.get_setting_obj(key)

        if not setting:
            return jsonify({
                'success': False,
                'error': f'Setting not found: {key}'
            }), 404

        return jsonify({
            'success': True,
            'setting': setting
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get setting',
            'details': str(e)
        }), 500


@api_v1.route('/admin/settings/system/settings/<key>', methods=['PATCH'])
@token_required
@admin_required
def update_setting(key: str):
    """
    Update single setting value

    Request Body:
        {
            "value": "new value",
            "value_type": "string"|"number"|"boolean"|"json" (optional)
        }

    Response:
        200: Setting updated
        400: Validation error
        404: Setting not found
        403: Forbidden (requires admin role)
        500: Server error
    """
    try:
        data = request.get_json()

        # Validate request
        update_request = UpdateSettingRequest(**data)

        # Check if setting exists
        if not SystemSettingsRepository.setting_exists(key):
            return jsonify({
                'success': False,
                'error': f'Setting not found: {key}'
            }), 404

        # Update setting
        success = SystemSettingsRepository.update_setting(
            key=key,
            value=update_request.value,
            value_type=update_request.value_type or 'string'
        )

        if success:
            # Get updated setting
            setting = SystemSettingsRepository.get_setting_obj(key)

            return jsonify({
                'success': True,
                'message': 'Setting updated successfully',
                'setting': setting
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update setting'
            }), 500

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update setting',
            'details': str(e)
        }), 500
