"""
LernsystemX Admin System API - AI Models Module

Endpoints:
- GET /api/v1/admin/ai/models/grouped - Models grouped by provider (legacy)
- GET /api/v1/admin/ai/models/registry - Full model registry
- PATCH /api/v1/admin/ai/models/<id>/default - Set model as default
- GET /api/v1/admin/ai/models/default - Get default model

Phase C3.0 - AI Model Selector System
"""

from flask import request, jsonify, current_app, g
from datetime import datetime

from app.api.v1.admin.system_operations import api_v1
from app.security.permissions import require_permission, Permissions
from app.services.audit_service import AuditService
from app.database.connection import fetch_all, fetch_one, execute_query


@api_v1.route('/admin/ai/models/grouped', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_models_grouped():
    """
    Get AI models grouped by provider (Legacy format for AdminAISettingsPage).

    This endpoint returns models in the provider-grouped format that
    AdminAISettingsPage.vue expects.

    **Endpoint:** GET /api/v1/admin/ai/models/grouped

    **Authentication:** Required (Admin only)

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "openai": {
                "display_name": "OpenAI",
                "models": [
                    {"name": "gpt-4o", "input_price": 0.005, "output_price": 0.015}
                ]
            },
            "anthropic": {
                "display_name": "Anthropic",
                "models": [...]
            }
        }
    }
    ```
    """
    try:
        # Query models from database grouped by provider
        query = """
            SELECT
                m.model_name,
                m.display_name,
                m.input_price_per_1k,
                m.output_price_per_1k,
                m.max_output_tokens,
                m.context_window,
                p.name as provider_name,
                p.display_name as provider_display_name
            FROM ai_models m
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.active = TRUE
            ORDER BY p.name ASC, m.model_name ASC
        """
        models = fetch_all(query, ())

        # Build provider-grouped response format
        result = {}
        for model in models:
            provider_name = model.get('provider_name') or 'unknown'
            if provider_name not in result:
                result[provider_name] = {
                    'display_name': model.get('provider_display_name') or provider_name.title(),
                    'models': []
                }
            result[provider_name]['models'].append({
                'name': model.get('model_name'),
                'input_price': model.get('input_price_per_1k') or 0,
                'output_price': model.get('output_price_per_1k') or 0,
                'max_tokens': model.get('max_output_tokens') or 4096,
                'context_window': model.get('context_window') or 128000
            })

        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get AI models (grouped): {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI models',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/models/registry', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_models_registry():
    """
    Get all available AI models for Model Selector Window (Phase C3.0).

    Returns flat list of all AI models with category, cost, speed info.
    Falls back to AIAdapter.PROVIDERS if database table is empty.
    Used by AdminModelSelectorWindow.vue.

    **Endpoint:** GET /api/v1/admin/ai/models/registry

    **Authentication:** Required (Admin only)

    **Query Parameters:**
        category: Filter by category (reasoning, chat, realtime, audio, image, embedding, moderation)
        active_only: Only show active models (default: true)
        search: Search in model name or description
        provider: Filter by provider name (openai, anthropic, etc.)
        configured_only: Only show models from providers with API keys (default: false)

    **Response:**
    ```json
    {
        "success": true,
        "data": [
            {
                "model_id": 1,
                "model_name": "gpt-4o",
                "display_name": "GPT-4o",
                "category": "chat",
                "description": "Most capable GPT-4 model with vision",
                "cost_level": "high",
                "speed": "fast",
                "context_window": 128000,
                "supports_vision": true,
                "is_default": true,
                "active": true
            }
        ],
        "categories": [
            {"id": "chat", "label": "Chat/Reasoning"},
            {"id": "image", "label": "Image Generation"},
            ...
        ]
    }
    ```
    """
    try:
        from app.services.ai_adapter import AIAdapter

        # Parse query parameters
        category_filter = request.args.get('category')
        search = request.args.get('search', '').lower()
        provider_filter = request.args.get('provider')
        configured_only = request.args.get('configured_only', 'false').lower() == 'true'

        # Get providers with API key status
        providers_data = []
        configured_provider_names = set()
        try:
            provider_query = """
                SELECT
                    provider_id,
                    name,
                    display_name,
                    CASE WHEN encrypted_api_key IS NOT NULL THEN TRUE ELSE FALSE END as has_api_key
                FROM ai_providers
                WHERE active = TRUE
                ORDER BY display_name ASC
            """
            providers_data = fetch_all(provider_query, ())
            configured_provider_names = {p['name'] for p in providers_data if p.get('has_api_key')}
        except Exception as prov_err:
            current_app.logger.warning(f"Failed to fetch providers: {prov_err}")

        # Try database first
        models = []
        try:
            query = """
                SELECT
                    m.model_id,
                    m.model_name,
                    m.display_name,
                    m.model_type,
                    m.category,
                    m.description,
                    m.cost_level,
                    m.speed,
                    m.context_window,
                    m.max_output_tokens,
                    m.supports_vision,
                    m.supports_functions,
                    m.supports_streaming,
                    m.is_default,
                    m.active,
                    m.input_price_per_1k,
                    m.output_price_per_1k,
                    p.name as provider
                FROM ai_models m
                LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
                WHERE m.active = TRUE
                ORDER BY m.model_name ASC
            """
            models = fetch_all(query, ())
        except Exception as db_err:
            current_app.logger.warning(f"Database query failed, using AIAdapter fallback: {db_err}")

        # Apply filters
        if category_filter:
            models = [m for m in models if m.get('category') == category_filter]

        if provider_filter:
            models = [m for m in models if m.get('provider') == provider_filter]

        if configured_only and configured_provider_names:
            models = [m for m in models if m.get('provider') in configured_provider_names]

        if search:
            models = [m for m in models if
                      search in m.get('model_name', '').lower() or
                      search in m.get('display_name', '').lower() or
                      search in (m.get('description') or '').lower()]

        # Sort by category priority, then default, then name
        category_order = {
            'chat': 1, 'reasoning': 2, 'coding': 3, 'search': 4, 'agent': 5,
            'realtime': 6, 'audio': 7, 'video': 8, 'image': 9,
            'embedding': 10, 'moderation': 11, 'open-source': 12, 'legacy': 13
        }
        models.sort(key=lambda m: (
            category_order.get(m.get('category', 'chat'), 99),
            0 if m.get('is_default') else 1,
            m.get('model_name', '')
        ))

        # Get unique categories from models
        unique_cats = sorted(set(m.get('category', 'chat') for m in models))
        category_labels = {
            'chat': 'Chat',
            'reasoning': 'Reasoning',
            'coding': 'Coding',
            'search': 'Web Search',
            'agent': 'Agentic',
            'realtime': 'Realtime',
            'audio': 'Audio',
            'video': 'Video',
            'image': 'Image',
            'embedding': 'Embedding',
            'moderation': 'Moderation',
            'open-source': 'Open Source',
            'legacy': 'Legacy'
        }
        categories = [{'id': c, 'label': category_labels.get(c, c.title())} for c in unique_cats]

        return jsonify({
            'success': True,
            'data': models,
            'categories': categories,
            'providers': providers_data,
            'total': len(models),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get AI models registry: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI models',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/models/<int:model_id>/default', methods=['PATCH'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def set_ai_model_default(model_id: int):
    """
    Set an AI model as the default for its category (Phase C3.0).

    **Endpoint:** PATCH /api/v1/admin/ai/models/<model_id>/default

    **Authentication:** Required (Admin only)

    **Body:**
    ```json
    {
        "is_default": true
    }
    ```
    """
    try:
        data = request.get_json() or {}
        is_default = data.get('is_default', True)

        # Get model info
        model = fetch_one(
            "SELECT model_id, model_name, category FROM ai_models WHERE model_id = %s",
            (model_id,)
        )

        if not model:
            return jsonify({
                'success': False,
                'error': 'Model not found'
            }), 404

        if is_default:
            # First, unset default for all models in this category
            execute_query(
                "UPDATE ai_models SET is_default = FALSE WHERE category = %s",
                (model['category'],)
            )

        # Set/unset this model as default
        execute_query(
            "UPDATE ai_models SET is_default = %s, updated_at = NOW() WHERE model_id = %s",
            (is_default, model_id)
        )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='set_default_model',
            resource_type='ai_models',
            resource_id=str(model_id),
            severity='info',
            details={
                'model_name': model['model_name'],
                'category': model['category'],
                'is_default': is_default
            }
        )

        return jsonify({
            'success': True,
            'message': (
                f"Model '{model['model_name']}' "
                f"{'set as' if is_default else 'removed as'} default for {model['category']}"
            ),
            'data': {
                'model_id': model_id,
                'model_name': model['model_name'],
                'category': model['category'],
                'is_default': is_default
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to set default model: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to set default model',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/models/default', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_default_ai_model():
    """
    Get the current default AI model (for chat category).

    **Endpoint:** GET /api/v1/admin/ai/models/default

    **Query Parameters:**
        category: Category to get default for (default: 'chat')
    """
    try:
        category = request.args.get('category', 'chat')

        model = fetch_one("""
            SELECT model_id, model_name, display_name, category, cost_level, speed
            FROM ai_models
            WHERE category = %s AND is_default = TRUE AND active = TRUE
            LIMIT 1
        """, (category,))

        if not model:
            # Fallback to gpt-4o if no default set
            model = fetch_one("""
                SELECT model_id, model_name, display_name, category, cost_level, speed
                FROM ai_models
                WHERE model_name = 'gpt-4o' AND active = TRUE
                LIMIT 1
            """)

        return jsonify({
            'success': True,
            'data': model
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get default model: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get default model',
            'message': str(e)
        }), 500
