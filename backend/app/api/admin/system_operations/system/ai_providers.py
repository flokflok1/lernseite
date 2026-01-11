"""
LernsystemX Admin System API - AI Providers Module

Endpoints:
- GET /api/v1/admin/ai/providers - List all AI providers
- GET /api/v1/admin/ai/providers/<id> - Get single provider
- PUT /api/v1/admin/ai/providers/<id>/api-key - Update API key
- DELETE /api/v1/admin/ai/providers/<id>/api-key - Remove API key
- PATCH /api/v1/admin/ai/providers/<id> - Update provider settings
- POST /api/v1/admin/ai/providers/<id>/test - Test provider connection

Phase B24-05 - AI Provider Management
"""

from flask import request, jsonify, current_app, g
from datetime import datetime
import time

from app.api.admin.system_operations.system import api_v1
from app.security.permissions import require_permission, Permissions
from app.repositories.ai.providers import AIProviderRepository
from app.services.audit_service import AuditService


@api_v1.route('/admin/ai/providers', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_providers():
    """
    Get all AI providers.

    Returns list of configured AI providers with their status.
    API keys are NOT returned, only whether they are configured.

    **Endpoint:** GET /api/v1/admin/ai/providers

    **Authentication:** Required (Admin only)

    **Response:**
    ```json
    {
        "success": true,
        "data": [
            {
                "provider_id": 1,
                "name": "openai",
                "display_name": "OpenAI",
                "provider_type": "openai",
                "active": true,
                "has_api_key": true,
                "priority": 100
            }
        ]
    }
    ```
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        providers = AIProviderRepository.get_all(include_inactive=include_inactive)

        # Convert timestamps to ISO format
        for provider in providers:
            if provider.get('created_at'):
                provider['created_at'] = provider['created_at'].isoformat()
            if provider.get('updated_at'):
                provider['updated_at'] = provider['updated_at'].isoformat()
            if provider.get('last_validated'):
                provider['last_validated'] = provider['last_validated'].isoformat()

        return jsonify({
            'success': True,
            'data': providers,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get AI providers: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI providers',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_provider(provider_id: int):
    """
    Get single AI provider details.

    **Endpoint:** GET /api/v1/admin/ai/providers/<provider_id>
    """
    try:
        provider = AIProviderRepository.get_by_id(provider_id)

        if not provider:
            return jsonify({
                'success': False,
                'error': 'Provider not found'
            }), 404

        # Convert timestamps
        if provider.get('created_at'):
            provider['created_at'] = provider['created_at'].isoformat()
        if provider.get('updated_at'):
            provider['updated_at'] = provider['updated_at'].isoformat()
        if provider.get('last_validated'):
            provider['last_validated'] = provider['last_validated'].isoformat()

        return jsonify({
            'success': True,
            'data': provider
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get AI provider: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI provider',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>/api-key', methods=['PUT'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_ai_provider_api_key(provider_id: int):
    """
    Update AI provider API key.

    The API key is encrypted before storage.

    **Endpoint:** PUT /api/v1/admin/ai/providers/<provider_id>/api-key

    **Body:**
    ```json
    {
        "api_key": "sk-..."
    }
    ```
    """
    try:
        data = request.get_json()

        if not data or 'api_key' not in data:
            return jsonify({
                'success': False,
                'error': 'API key is required'
            }), 400

        api_key = data['api_key'].strip()

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key cannot be empty'
            }), 400

        # Update API key (encrypted)
        result = AIProviderRepository.update_api_key(provider_id, api_key)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Provider not found'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='update_api_key',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            severity='warning',
            details={'provider_name': result.get('name')}
        )

        current_app.logger.info(
            f"AI provider API key updated: {result.get('name')} by user {g.current_user['user_id']}"
        )

        return jsonify({
            'success': True,
            'message': 'API key updated successfully',
            'data': result
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to update AI provider API key: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update API key',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>/api-key', methods=['DELETE'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def delete_ai_provider_api_key(provider_id: int):
    """
    Remove API key from provider (deactivates provider).

    **Endpoint:** DELETE /api/v1/admin/ai/providers/<provider_id>/api-key
    """
    try:
        result = AIProviderRepository.clear_api_key(provider_id)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Provider not found'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='delete_api_key',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            severity='warning',
            details={'provider_name': result.get('name')}
        )

        return jsonify({
            'success': True,
            'message': 'API key removed successfully',
            'data': result
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to delete AI provider API key: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete API key',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_ai_provider(provider_id: int):
    """
    Update AI provider settings.

    **Endpoint:** PATCH /api/v1/admin/ai/providers/<provider_id>

    **Body:**
    ```json
    {
        "active": true,
        "priority": 100,
        "rate_limit_per_minute": 60
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

        result = AIProviderRepository.update_provider(provider_id, data)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Provider not found'
            }), 404

        # Convert timestamps
        if result.get('created_at'):
            result['created_at'] = (
                result['created_at'].isoformat()
                if hasattr(result['created_at'], 'isoformat')
                else result['created_at']
            )
        if result.get('updated_at'):
            result['updated_at'] = (
                result['updated_at'].isoformat()
                if hasattr(result['updated_at'], 'isoformat')
                else result['updated_at']
            )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='update_provider',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            severity='info',
            details={'changes': list(data.keys())}
        )

        return jsonify({
            'success': True,
            'message': 'Provider updated successfully',
            'data': result
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to update AI provider: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update provider',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>/test', methods=['POST'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def test_ai_provider(provider_id: int):
    """
    Test AI provider connection.

    Validates the API key by making a simple API call.

    **Endpoint:** POST /api/v1/admin/ai/providers/<provider_id>/test
    """
    try:
        provider = (
            AIProviderRepository.get_by_name_by_id(provider_id)
            if hasattr(AIProviderRepository, 'get_by_name_by_id')
            else AIProviderRepository.get_by_id(provider_id)
        )

        if not provider:
            return jsonify({
                'success': False,
                'error': 'Provider not found'
            }), 404

        # Get decrypted API key
        provider_full = AIProviderRepository.get_by_name(provider.get('name'))
        if not provider_full or not provider_full.get('encrypted_api_key'):
            return jsonify({
                'success': False,
                'error': 'No API key configured for this provider'
            }), 400

        api_key = AIProviderRepository._decrypt_api_key(
            provider_full.get('encrypted_api_key'),
            provider_full.get('encryption_salt')
        )

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Failed to decrypt API key'
            }), 500

        # Test based on provider type
        provider_type = provider.get('provider_type')
        test_result = {'valid': False, 'message': 'Unknown provider type'}

        start_time = time.time()

        if provider_type == 'openai':
            test_result = _test_openai_key(api_key)
        elif provider_type == 'anthropic':
            test_result = _test_anthropic_key(api_key)
        elif provider_type == 'google':
            test_result = _test_google_key(api_key)
        else:
            test_result = {'valid': False, 'message': f'Testing not implemented for {provider_type}'}

        response_time_ms = int((time.time() - start_time) * 1000)

        # Log health check
        status = 'healthy' if test_result['valid'] else 'down'
        AIProviderRepository.log_health_check(
            provider_id,
            status,
            response_time_ms,
            None if test_result['valid'] else test_result.get('message')
        )

        # Update validation timestamp
        if test_result['valid']:
            AIProviderRepository.validate_api_key(provider_id, True)

        return jsonify({
            'success': True,
            'data': {
                'valid': test_result['valid'],
                'message': test_result.get('message', 'OK'),
                'response_time_ms': response_time_ms
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to test AI provider: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to test provider',
            'message': str(e)
        }), 500


# ============================================================================
# Test Helper Functions
# ============================================================================

def _test_openai_key(api_key: str) -> dict:
    """Test OpenAI API key validity."""
    try:
        import requests
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        if response.status_code == 200:
            return {'valid': True, 'message': 'API key is valid'}
        elif response.status_code == 401:
            return {'valid': False, 'message': 'Invalid API key'}
        else:
            return {'valid': False, 'message': f'API error: {response.status_code}'}
    except Exception as e:
        return {'valid': False, 'message': str(e)}


def _test_anthropic_key(api_key: str) -> dict:
    """Test Anthropic API key validity."""
    try:
        import requests
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            json={
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 10,
                'messages': [{'role': 'user', 'content': 'Hi'}]
            },
            timeout=15
        )
        if response.status_code == 200:
            return {'valid': True, 'message': 'API key is valid'}
        elif response.status_code == 401:
            return {'valid': False, 'message': 'Invalid API key'}
        else:
            error_detail = response.json().get('error', {}).get('message', 'Unknown error')
            return {'valid': False, 'message': f'API error: {error_detail}'}
    except Exception as e:
        return {'valid': False, 'message': str(e)}


def _test_google_key(api_key: str) -> dict:
    """Test Google AI API key validity."""
    try:
        import requests
        response = requests.get(
            f'https://generativelanguage.googleapis.com/v1/models?key={api_key}',
            timeout=10
        )
        if response.status_code == 200:
            return {'valid': True, 'message': 'API key is valid'}
        elif response.status_code == 400 or response.status_code == 403:
            return {'valid': False, 'message': 'Invalid API key'}
        else:
            return {'valid': False, 'message': f'API error: {response.status_code}'}
    except Exception as e:
        return {'valid': False, 'message': str(e)}
