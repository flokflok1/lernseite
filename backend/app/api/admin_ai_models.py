"""
LernsystemX Admin AI Models API

AI model management endpoints:
- GET /api/v1/admin/ai/models - List all AI models
- GET /api/v1/admin/ai/models/<id> - Get model by ID
- PUT /api/v1/admin/ai/models/<id> - Update model
- POST /api/v1/admin/ai/models/sync - Sync models from providers
- POST /api/v1/admin/ai/models/sync/adapter - Sync from ai_adapter.py
- GET /api/v1/admin/ai/models/stats - Get model statistics
- PUT /api/v1/admin/ai/models/<id>/default - Set default model

Phase KI-Architektur - Model Management
"""

from flask import request, jsonify, g
from datetime import datetime

from app.api import api_v1
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.ai_models_repository import AIModelsRepository
from app.repositories.ai_provider_repository import AIProviderRepository
from app.services.ai_model_sync_service import AIModelSyncService
from app.services.audit_service import AuditService


# ============================================================================
# AI Models Management
# ============================================================================

@api_v1.route('/admin/ai/models', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def list_ai_models():
    """
    List all AI models.

    **Query Parameters:**
    - include_inactive (bool): Include inactive models (default: false)
    - provider (string): Filter by provider name (openai, anthropic, etc.)
    - category (string): Filter by category (chat, reasoning, etc.)

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "models": [...],
            "count": 50,
            "categories": ["chat", "reasoning", "audio", ...]
        }
    }
    ```
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        provider_name = request.args.get('provider')
        category = request.args.get('category')

        # Get provider_id if provider name specified
        provider_id = None
        if provider_name:
            provider = AIProviderRepository.get_by_name(provider_name)
            if provider:
                provider_id = provider.get('provider_id')

        # Get models
        if category:
            models = AIModelsRepository.get_by_category(category, active_only=not include_inactive)
        else:
            models = AIModelsRepository.get_all(
                include_inactive=include_inactive,
                provider_id=provider_id
            )

        # Get categories
        categories = AIModelsRepository.get_categories()

        return jsonify({
            'success': True,
            'data': {
                'models': models,
                'count': len(models),
                'categories': categories
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'LIST_MODELS_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/models/<int:model_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_model(model_id: int):
    """
    Get AI model by ID.

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "model_id": 1,
            "model_name": "gpt-4o",
            "display_name": "GPT-4o",
            ...
        }
    }
    ```
    """
    try:
        model = AIModelsRepository.get_by_id(model_id)

        if not model:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MODEL_NOT_FOUND',
                    'message': f'Model {model_id} not found'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': model
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_MODEL_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/models/<int:model_id>', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_ai_model(model_id: int):
    """
    Update AI model.

    **Request Body:**
    ```json
    {
        "display_name": "GPT-4o Updated",
        "description": "Most capable GPT-4 model",
        "active": true,
        "input_price_per_1k": 0.005,
        "output_price_per_1k": 0.015
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "data": { ... }
    }
    ```
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Request body required'
                }
            }), 400

        # Check if model exists
        existing = AIModelsRepository.get_by_id(model_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MODEL_NOT_FOUND',
                    'message': f'Model {model_id} not found'
                }
            }), 404

        # Update model
        model = AIModelsRepository.update(model_id, data)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='update_ai_model',
            resource_type='ai_model',
            resource_id=str(model_id),
            details={'changes': data}
        )

        return jsonify({
            'success': True,
            'data': model,
            'message': f'Model {model.get("model_name")} updated'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_MODEL_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/models/<int:model_id>/default', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def set_default_model(model_id: int):
    """
    Set model as default for its category.

    **Response:**
    ```json
    {
        "success": true,
        "data": { ... },
        "message": "gpt-4o is now the default model for chat"
    }
    ```
    """
    try:
        model = AIModelsRepository.set_default(model_id)

        if not model:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MODEL_NOT_FOUND',
                    'message': f'Model {model_id} not found'
                }
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='set_default_ai_model',
            resource_type='ai_model',
            resource_id=str(model_id),
            details={'category': model.get('category')}
        )

        return jsonify({
            'success': True,
            'data': model,
            'message': f'{model.get("model_name")} is now the default model for {model.get("category")}'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SET_DEFAULT_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/models/<int:model_id>/active', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def toggle_model_active(model_id: int):
    """
    Toggle model active status.

    **Request Body:**
    ```json
    {
        "active": true
    }
    ```
    """
    try:
        data = request.get_json()
        if data is None or 'active' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'active field required'
                }
            }), 400

        model = AIModelsRepository.set_active(model_id, data['active'])

        if not model:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MODEL_NOT_FOUND',
                    'message': f'Model {model_id} not found'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': model,
            'message': f'Model {model.get("model_name")} {"activated" if data["active"] else "deactivated"}'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'TOGGLE_ACTIVE_ERROR',
                'message': str(e)
            }
        }), 500


# ============================================================================
# Model Sync Endpoints
# ============================================================================

@api_v1.route('/admin/ai/models/sync', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def sync_ai_models():
    """
    Sync models from all active provider APIs.

    This fetches the model list from OpenAI /v1/models endpoint and
    merges with local price data (prices are not available via API).

    **Request Body (optional):**
    ```json
    {
        "provider": "openai"  // Optional: sync only specific provider
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "timestamp": "2025-12-04T10:30:00Z",
            "providers": {
                "openai": {
                    "synced": 84,
                    "added": 10,
                    "updated": 74,
                    "api_models": 84,
                    "errors": []
                }
            },
            "total_synced": 84,
            "total_added": 10,
            "total_updated": 74,
            "errors": []
        }
    }
    ```
    """
    try:
        data = request.get_json() or {}
        provider = data.get('provider')

        if provider == 'openai':
            result = AIModelSyncService.sync_openai_models()
            result = {
                'timestamp': datetime.utcnow().isoformat(),
                'providers': {'openai': result},
                'total_synced': result.get('synced', 0),
                'total_added': result.get('added', 0),
                'total_updated': result.get('updated', 0),
                'errors': result.get('errors', [])
            }
        elif provider == 'anthropic':
            result = AIModelSyncService.sync_anthropic_models()
            result = {
                'timestamp': datetime.utcnow().isoformat(),
                'providers': {'anthropic': result},
                'total_synced': result.get('synced', 0),
                'total_added': result.get('added', 0),
                'total_updated': result.get('updated', 0),
                'errors': result.get('errors', [])
            }
        elif provider == 'google':
            result = AIModelSyncService.sync_google_models()
            result = {
                'timestamp': datetime.utcnow().isoformat(),
                'providers': {'google': result},
                'total_synced': result.get('synced', 0),
                'total_added': result.get('added', 0),
                'total_updated': result.get('updated', 0),
                'errors': result.get('errors', [])
            }
        else:
            result = AIModelSyncService.sync_all_providers()

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='sync_ai_models',
            resource_type='ai_model',
            resource_id='all' if not provider else provider,
            details={
                'synced': result.get('total_synced', 0),
                'added': result.get('total_added', 0),
                'updated': result.get('total_updated', 0)
            }
        )

        return jsonify({
            'success': True,
            'data': result,
            'message': f'Synced {result.get("total_synced", 0)} models ({result.get("total_added", 0)} new, {result.get("total_updated", 0)} updated)'
        }), 200

    except Exception as e:
        import traceback
        from flask import current_app
        current_app.logger.error(f'AI Model Sync Error: {str(e)}')
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': {
                'code': 'SYNC_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/models/sync/adapter', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def sync_from_adapter():
    """
    Sync all models from ai_adapter.py static definitions.

    This adds all models defined in AIAdapter.PROVIDERS to the database,
    including prices which are not available via external API.

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "timestamp": "2025-12-04T10:30:00Z",
            "providers": { ... },
            "total_synced": 100,
            "total_added": 50,
            "total_updated": 50
        }
    }
    ```
    """
    try:
        result = AIModelSyncService.sync_from_adapter()

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='sync_ai_models_from_adapter',
            resource_type='ai_model',
            resource_id='adapter',
            details={
                'synced': result.get('total_synced', 0),
                'added': result.get('total_added', 0),
                'updated': result.get('total_updated', 0)
            }
        )

        return jsonify({
            'success': True,
            'data': result,
            'message': f'Synced {result.get("total_synced", 0)} models from adapter ({result.get("total_added", 0)} new, {result.get("total_updated", 0)} updated)'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SYNC_ADAPTER_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/models/stats', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_model_stats():
    """
    Get AI model statistics.

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "stats": {
                "total_models": 100,
                "active_models": 90,
                "providers": 5,
                "categories": 8,
                "default_models": 8
            },
            "categories": ["chat", "reasoning", "audio", ...],
            "adapter_models": {
                "openai": 84,
                "anthropic": 5,
                "google": 5
            }
        }
    }
    ```
    """
    try:
        status = AIModelSyncService.get_sync_status()

        return jsonify({
            'success': True,
            'data': status
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_STATS_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/models/default/<category>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_default_model_for_category(category: str):
    """
    Get default model for a category.

    **URL Parameters:**
    - category: Model category (chat, reasoning, audio, image, etc.)

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "model_id": 1,
            "model_name": "gpt-4o",
            ...
        }
    }
    ```
    """
    try:
        model = AIModelsRepository.get_default_model(category)

        if not model:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_DEFAULT_MODEL',
                    'message': f'No default model configured for category: {category}'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': model
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_DEFAULT_ERROR',
                'message': str(e)
            }
        }), 500


# ============================================================================
# AI Provider Management - Additional Endpoints
# Note: GET /admin/ai/providers and GET /admin/ai/providers/<id> are in admin_system.py
# ============================================================================

@api_v1.route('/admin/ai/providers/<int:provider_id>/api-key', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_provider_api_key(provider_id: int):
    """
    Update provider API key.

    **Request Body:**
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
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'api_key field required'
                }
            }), 400

        # Check if provider exists
        existing = AIProviderRepository.get_by_id(provider_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PROVIDER_NOT_FOUND',
                    'message': f'Provider {provider_id} not found'
                }
            }), 404

        # Update API key (encrypted)
        result = AIProviderRepository.update_api_key(provider_id, data['api_key'])

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='update_provider_api_key',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            details={'provider': existing.get('name')}
        )

        return jsonify({
            'success': True,
            'data': result,
            'message': f'API key for {existing.get("display_name")} updated'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_API_KEY_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>/test', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def test_provider_connection(provider_id: int):
    """
    Test provider API connection.

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "connected": true,
            "response_time_ms": 245,
            "models_available": 50
        }
    }
    ```
    """
    import time

    try:
        provider = AIProviderRepository.get_by_id(provider_id)

        if not provider:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PROVIDER_NOT_FOUND',
                    'message': f'Provider {provider_id} not found'
                }
            }), 404

        if not provider.get('has_api_key'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_API_KEY',
                    'message': 'No API key configured for this provider'
                }
            }), 400

        # Get decrypted API key
        api_key = AIProviderRepository.get_decrypted_api_key(provider['name'])

        if not api_key:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'DECRYPTION_FAILED',
                    'message': 'Failed to decrypt API key. Check SECRET_KEY configuration.'
                }
            }), 500

        # Test connection based on provider type
        provider_name = provider['name'].lower()
        start_time = time.time()

        if provider_name == 'openai':
            import requests
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=10)
            response.raise_for_status()
            models_count = len(response.json().get('data', []))

        elif provider_name == 'anthropic':
            import requests
            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            # Anthropic doesn't have a models endpoint, so we just validate the key format
            # and make a minimal request
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json={
                    'model': 'claude-3-haiku-20240307',
                    'max_tokens': 1,
                    'messages': [{'role': 'user', 'content': 'Hi'}]
                },
                timeout=15
            )
            if response.status_code == 401:
                raise Exception('Invalid API key')
            models_count = 5  # Anthropic has ~5 main models

        elif provider_name == 'google':
            import requests
            response = requests.get(
                f'https://generativelanguage.googleapis.com/v1/models?key={api_key}',
                timeout=10
            )
            response.raise_for_status()
            models_count = len(response.json().get('models', []))

        elif provider_name == 'deepl':
            import requests
            # DeepL Pro vs Free API
            base_url = 'https://api.deepl.com/v2' if not api_key.endswith(':fx') else 'https://api-free.deepl.com/v2'
            headers = {'Authorization': f'DeepL-Auth-Key {api_key}'}
            response = requests.get(f'{base_url}/usage', headers=headers, timeout=10)
            response.raise_for_status()
            models_count = 1  # DeepL is a single service

        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNSUPPORTED_PROVIDER',
                    'message': f'Testing not implemented for provider: {provider_name}'
                }
            }), 400

        response_time_ms = int((time.time() - start_time) * 1000)

        # Log successful health check
        AIProviderRepository.log_health_check(provider_id, 'healthy', response_time_ms)

        # Update validation timestamp
        AIProviderRepository.validate_api_key(provider_id, True)

        return jsonify({
            'success': True,
            'data': {
                'connected': True,
                'response_time_ms': response_time_ms,
                'models_available': models_count
            }
        }), 200

    except Exception as e:
        # Log failed health check
        try:
            AIProviderRepository.log_health_check(provider_id, 'down', error_message=str(e))
        except Exception:
            pass

        return jsonify({
            'success': False,
            'error': {
                'code': 'CONNECTION_TEST_FAILED',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>/active', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def toggle_provider_active(provider_id: int):
    """
    Toggle provider active status.

    **Request Body:**
    ```json
    {
        "active": true
    }
    ```
    """
    try:
        data = request.get_json()
        if data is None or 'active' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'active field required'
                }
            }), 400

        provider = AIProviderRepository.set_active(provider_id, data['active'])

        if not provider:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PROVIDER_NOT_FOUND',
                    'message': f'Provider {provider_id} not found'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': provider,
            'message': f'Provider {provider.get("name")} {"activated" if data["active"] else "deactivated"}'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'TOGGLE_ACTIVE_ERROR',
                'message': str(e)
            }
        }), 500


# ============================================================================
# AI Usage Statistics
# ============================================================================

@api_v1.route('/admin/ai/usage-stats', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_usage_stats():
    """
    Get AI usage statistics for dashboard.

    **Query Parameters:**
    - period: 'today', 'week', 'month', 'year' (default: 'month')
    - user_id: Optional filter by user

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "overview": {
                "total_tokens": 2400000,
                "total_cost": 142.50,
                "total_generations": 1234
            },
            "by_model": [...],
            "by_category": [...],
            "recent_activity": [...]
        }
    }
    ```
    """
    from app.database.connection import fetch_one, fetch_all

    try:
        period = request.args.get('period', 'month')
        user_id = request.args.get('user_id')

        # Define period filter
        period_sql = {
            'today': "created_at >= CURRENT_DATE",
            'week': "created_at >= CURRENT_DATE - INTERVAL '7 days'",
            'month': "created_at >= CURRENT_DATE - INTERVAL '30 days'",
            'year': "created_at >= CURRENT_DATE - INTERVAL '365 days'"
        }.get(period, "created_at >= CURRENT_DATE - INTERVAL '30 days'")

        # Build user filter
        user_filter = f"AND user_id = '{user_id}'" if user_id else ""

        # Get overview stats from ai_studio_analytics
        overview_query = f"""
            SELECT
                COALESCE(SUM(tokens_used), 0) AS total_tokens,
                COUNT(*) AS total_generations,
                COALESCE(AVG(generation_time_ms), 0) AS avg_latency_ms,
                COUNT(DISTINCT session_id) AS total_sessions
            FROM ai_studio_analytics
            WHERE {period_sql} {user_filter}
        """
        overview = fetch_one(overview_query) or {}

        # Get cost estimate (based on token usage and average price)
        total_tokens = int(overview.get('total_tokens', 0))
        # Estimate: ~$0.002 per 1K tokens average across all models
        estimated_cost = round(total_tokens * 0.002 / 1000, 2)

        # Get usage by model
        model_usage_query = f"""
            SELECT
                ai_model AS model_name,
                ai_provider AS provider,
                COUNT(*) AS request_count,
                COALESCE(SUM(tokens_used), 0) AS tokens_used
            FROM ai_studio_analytics
            WHERE {period_sql} {user_filter}
                AND ai_model IS NOT NULL
            GROUP BY ai_model, ai_provider
            ORDER BY tokens_used DESC
            LIMIT 10
        """
        model_usage = fetch_all(model_usage_query) or []

        # Get usage by event type (category)
        category_usage_query = f"""
            SELECT
                event_type AS category,
                COUNT(*) AS count,
                COALESCE(SUM(tokens_used), 0) AS tokens
            FROM ai_studio_analytics
            WHERE {period_sql} {user_filter}
            GROUP BY event_type
            ORDER BY tokens DESC
        """
        category_usage = fetch_all(category_usage_query) or []

        # Get recent activity
        recent_query = f"""
            SELECT
                event_id::text AS id,
                event_type AS type,
                ai_model AS model,
                tokens_used AS tokens,
                generation_time_ms AS latency_ms,
                created_at,
                step_name,
                component_name
            FROM ai_studio_analytics
            WHERE {period_sql} {user_filter}
            ORDER BY created_at DESC
            LIMIT 20
        """
        recent_activity = fetch_all(recent_query) or []

        # Format recent activity
        formatted_activity = []
        for activity in recent_activity:
            formatted_activity.append({
                'id': activity.get('id'),
                'type': activity.get('type', 'unknown'),
                'title': f"{activity.get('step_name', '')} - {activity.get('component_name', '')}".strip(' - ') or activity.get('type', 'KI-Aktion'),
                'model': activity.get('model', '-'),
                'tokens': activity.get('tokens', 0) or 0,
                'time': _format_relative_time(activity.get('created_at'))
            })

        # Performance metrics
        performance_query = f"""
            SELECT
                COALESCE(AVG(generation_time_ms), 0) AS avg_latency_ms,
                COUNT(*) AS total_requests,
                COUNT(*) FILTER (WHERE generation_time_ms IS NOT NULL AND generation_time_ms > 0) AS successful_requests
            FROM ai_studio_analytics
            WHERE {period_sql} {user_filter}
        """
        performance = fetch_one(performance_query) or {}

        success_rate = 0
        if performance.get('total_requests', 0) > 0:
            success_rate = round(performance.get('successful_requests', 0) / performance.get('total_requests', 1) * 100, 1)

        return jsonify({
            'success': True,
            'data': {
                'period': period,
                'overview': {
                    'total_tokens': total_tokens,
                    'total_cost': estimated_cost,
                    'total_generations': overview.get('total_generations', 0),
                    'total_sessions': overview.get('total_sessions', 0),
                    'avg_latency_ms': round(overview.get('avg_latency_ms', 0), 0)
                },
                'by_model': model_usage,
                'by_category': category_usage,
                'recent_activity': formatted_activity,
                'performance': {
                    'avg_latency_ms': round(performance.get('avg_latency_ms', 0), 0),
                    'success_rate': success_rate,
                    'total_requests': performance.get('total_requests', 0)
                }
            }
        }), 200

    except Exception as e:
        import traceback
        from flask import current_app
        current_app.logger.error(f'AI Usage Stats Error: {str(e)}')
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_USAGE_STATS_ERROR',
                'message': str(e)
            }
        }), 500


def _format_relative_time(dt) -> str:
    """Format datetime as relative time string"""
    if not dt:
        return '-'

    from datetime import datetime as dt_class, timezone

    if isinstance(dt, str):
        dt = dt_class.fromisoformat(dt.replace('Z', '+00:00'))

    now = dt_class.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt

    if diff.total_seconds() < 60:
        return 'gerade eben'
    elif diff.total_seconds() < 3600:
        mins = int(diff.total_seconds() / 60)
        return f'vor {mins} Min'
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f'vor {hours} Std'
    else:
        days = int(diff.total_seconds() / 86400)
        return f'vor {days} Tag{"en" if days > 1 else ""}'
