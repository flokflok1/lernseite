"""
AI Models Provider Synchronization (DDD)

Endpoints for syncing models from AI providers:
- POST /api/v1/admin/settings/ai/models/sync/<provider_id> - Sync models from provider

Uses:
- AIModelFactory for model creation with business rules
- AISyncService for sync operation logic
- AIModelSyncedEvent - Published when sync completes

Business Rules:
- New models are added as active with default margin (33.33%)
- Existing models with pricing changes are updated
- Removed models are deactivated (NOT deleted)
"""

from flask import Blueprint, jsonify, g
from typing import Dict, Any, Tuple
from datetime import datetime
import logging
import uuid
import time

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.ai_models import AIModelsRepository
from app.repositories.ai.providers import AIProviderRepository
from app.services.audit_service import AuditService

# DDD Core Domain
from .core.factory import AIModelFactory
from .core.services import AISyncService
from .core.events import (
    AIModelSyncedEvent,
    EventPublisher,
    EventPriority
)

logger = logging.getLogger(__name__)

models_sync_bp = Blueprint(
    'ai_models_sync',
    __name__,
    url_prefix='/admin-panel/settings/ai/models'
)


@models_sync_bp.route('/sync/<int:provider_id>', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def sync_models_from_provider(provider_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Synchronize models from AI provider.

    Business Rules (enforced by AISyncService):
    1. New models → Add as active with default margin
    2. Pricing changes → Update existing models
    3. Missing models → Deactivate (don't delete)

    Args:
        provider_id: The provider's database ID

    Returns:
        JSON response with sync summary

    DDD:
    - Uses AIModelFactory to create models
    - Uses AISyncService to determine sync operations
    - Publishes AIModelSyncedEvent when complete
    """
    try:
        start_time = time.time()

        # Check if provider exists
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
                    'message': 'Provider has no API key configured'
                }
            }), 400

        # Get models from provider API
        # TODO: Implement actual provider API calls
        # For now, simulating with mock data
        provider_models = _fetch_models_from_provider(provider)

        # Get existing models for this provider
        existing_models = AIModelsRepository.get_by_provider(provider_id)

        # DDD: Use AISyncService to determine operations
        operations = AISyncService.prepare_sync_operations(
            provider_models=provider_models,
            existing_models=existing_models
        )

        # Execute sync operations
        models_added = 0
        models_updated = 0
        models_deactivated = 0

        # Add new models (using Factory)
        for provider_model in operations['add']:
            try:
                model_data = AIModelFactory.create_from_provider_sync(
                    provider_id=str(provider_id),
                    model_identifier=provider_model['model_identifier'],
                    model_name=provider_model['model_name'],
                    category=provider_model['category'],
                    input_cost_per_1k=provider_model['input_cost_per_1k'],
                    output_cost_per_1k=provider_model['output_cost_per_1k'],
                    context_window=provider_model.get('context_window'),
                    supports_streaming=provider_model.get('supports_streaming', True)
                )
                AIModelsRepository.create(model_data)
                models_added += 1
            except Exception as e:
                logger.error(f"Error adding model {provider_model['model_name']}: {e}")

        # Update existing models with pricing changes
        for update_op in operations['update']:
            try:
                AIModelsRepository.update(
                    update_op['model_id'],
                    update_op['changes']
                )
                models_updated += 1
            except Exception as e:
                logger.error(f"Error updating model {update_op['model_id']}: {e}")

        # Deactivate removed models (Business Rule: Don't delete!)
        for model_to_deactivate in operations['deactivate']:
            try:
                AIModelsRepository.set_active(model_to_deactivate['model_id'], False)
                models_deactivated += 1
            except Exception as e:
                logger.error(f"Error deactivating model {model_to_deactivate['model_id']}: {e}")

        sync_duration = time.time() - start_time

        # DDD: Publish Domain Event
        event = AIModelSyncedEvent(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=str(provider_id),
            provider_id=str(provider_id),
            provider_name=provider.get('name'),
            models_added=models_added,
            models_updated=models_updated,
            models_deactivated=models_deactivated,
            sync_duration_seconds=sync_duration,
            priority=EventPriority.MEDIUM
        )
        EventPublisher.publish(event)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='sync_ai_models',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            details={
                'provider_name': provider.get('name'),
                'models_added': models_added,
                'models_updated': models_updated,
                'models_deactivated': models_deactivated,
                'duration_seconds': sync_duration
            }
        )

        return jsonify({
            'success': True,
            'data': {
                'provider': provider.get('name'),
                'models_added': models_added,
                'models_updated': models_updated,
                'models_deactivated': models_deactivated,
                'sync_duration_seconds': round(sync_duration, 2)
            },
            'message': f'Synced {models_added + models_updated} models from {provider.get("name")}'
        }), 200

    except Exception as e:
        logger.error(f"Error syncing models from provider {provider_id}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'SYNC_ERROR',
                'message': str(e)
            }
        }), 500


def _fetch_models_from_provider(provider: Dict[str, Any]) -> list:
    """
    Fetch models from provider API.

    TODO: Implement actual API calls for each provider.

    Args:
        provider: Provider configuration

    Returns:
        List of models from provider
    """
    # Mock implementation
    # In production, this would call OpenAI, Anthropic, Google APIs
    provider_name = provider.get('name', '').lower()

    if provider_name == 'openai':
        return [
            {
                'model_identifier': 'gpt-4-turbo',
                'model_name': 'GPT-4 Turbo',
                'category': 'chat',
                'input_cost_per_1k': 0.01,
                'output_cost_per_1k': 0.03,
                'context_window': 128000,
                'supports_streaming': True
            },
            {
                'model_identifier': 'gpt-3.5-turbo',
                'model_name': 'GPT-3.5 Turbo',
                'category': 'chat',
                'input_cost_per_1k': 0.0005,
                'output_cost_per_1k': 0.0015,
                'context_window': 16385,
                'supports_streaming': True
            }
        ]
    elif provider_name == 'anthropic':
        return [
            {
                'model_identifier': 'claude-opus-4-5',
                'model_name': 'Claude Opus 4.5',
                'category': 'chat',
                'input_cost_per_1k': 0.015,
                'output_cost_per_1k': 0.075,
                'context_window': 200000,
                'supports_streaming': True
            },
            {
                'model_identifier': 'claude-sonnet-4-5',
                'model_name': 'Claude Sonnet 4.5',
                'category': 'chat',
                'input_cost_per_1k': 0.003,
                'output_cost_per_1k': 0.015,
                'context_window': 200000,
                'supports_streaming': True
            }
        ]
    else:
        return []
