"""
LernsystemX Admin System API - AI Settings Module

Endpoints:
- GET /api/v1/admin/ai/settings - Get global AI settings
- PUT /api/v1/admin/ai/settings - Update global AI settings

Phase C3.0 - AI Model Selector System
"""

from flask import request, jsonify, current_app, g
from datetime import datetime

from app.api.admin.system_operations.system import api_v1
from app.security.permissions import require_permission, Permissions
from app.services.audit_service import AuditService


@api_v1.route('/admin/ai/settings', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_settings():
    """
    Get global AI settings including default provider and model.

    **Endpoint:** GET /api/v1/admin/ai/settings
    """
    try:
        # Get current settings from config or database
        settings = {
            'default_provider': current_app.config.get('AI_DEFAULT_PROVIDER', 'openai'),
            'default_model': current_app.config.get('AI_DEFAULT_MODEL', 'gpt-4o-mini'),
            'max_tokens': current_app.config.get('AI_MAX_TOKENS', 4096),
            'temperature': current_app.config.get('AI_TEMPERATURE', 0.7)
        }

        return jsonify({
            'success': True,
            'data': settings,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get AI settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI settings',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/settings', methods=['PUT'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_ai_settings():
    """
    Update global AI settings.

    **Endpoint:** PUT /api/v1/admin/ai/settings

    **Body:**
    ```json
    {
        "default_provider": "openai",
        "default_model": "gpt-5-mini"
    }
    ```
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Validate provider and model
        from app.services.ai_adapter import AIAdapter

        if 'default_provider' in data:
            provider = data['default_provider']
            if provider not in AIAdapter.PROVIDERS:
                return jsonify({
                    'success': False,
                    'error': f'Invalid provider: {provider}'
                }), 400

        if 'default_model' in data and 'default_provider' in data:
            provider = data['default_provider']
            model = data['default_model']
            if model not in AIAdapter.PROVIDERS.get(provider, {}).get('models', {}):
                return jsonify({
                    'success': False,
                    'error': f'Invalid model: {model} for provider {provider}'
                }), 400

        # Update settings in database
        # For now, we'll just update the app config (in production this should be stored in DB)
        if 'default_provider' in data:
            current_app.config['AI_DEFAULT_PROVIDER'] = data['default_provider']
        if 'default_model' in data:
            current_app.config['AI_DEFAULT_MODEL'] = data['default_model']
        if 'max_tokens' in data:
            current_app.config['AI_MAX_TOKENS'] = int(data['max_tokens'])
        if 'temperature' in data:
            current_app.config['AI_TEMPERATURE'] = float(data['temperature'])

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='update_ai_settings',
            resource_type='ai_settings',
            severity='warning',
            details={'changes': list(data.keys())}
        )

        return jsonify({
            'success': True,
            'message': 'AI settings updated successfully',
            'data': {
                'default_provider': current_app.config.get('AI_DEFAULT_PROVIDER'),
                'default_model': current_app.config.get('AI_DEFAULT_MODEL'),
                'max_tokens': current_app.config.get('AI_MAX_TOKENS'),
                'temperature': current_app.config.get('AI_TEMPERATURE')
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to update AI settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update AI settings',
            'message': str(e)
        }), 500
