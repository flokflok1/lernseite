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

from app.api.middleware.auth import permission_required
from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
from app.infrastructure.persistence.repositories.ai.config.providers import AIProviderRepository
from app.application.services.system.audit.service import AuditService
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

# DDD Core Domain
from ..core.factory import AIModelFactory
from ..core.services import AISyncService
from ..core.events import (
    AIModelSyncedEvent,
    EventPublisher,
    EventPriority
)

logger = logging.getLogger(__name__)

models_sync_bp = Blueprint(
    'ai_models_sync',
    __name__,
    url_prefix='/panel/settings/ai/models'
)


@models_sync_bp.route('/sync/<int:provider_id>', methods=['POST'])
@permission_required('admin.system:write')
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
            return error_response(ErrorCode.AI_PROVIDER_NOT_FOUND, 404,
                details={'provider_id': provider_id})

        if not provider.get('has_api_key'):
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400,
                details={'message': 'Provider has no API key configured'})

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
                    supports_streaming=provider_model.get('supports_streaming', True),
                    display_name=provider_model.get('display_name'),
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
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500,
            details={'error': str(e)})


def _fetch_models_from_provider(provider: Dict[str, Any]) -> list:
    """
    Fetch models from provider API using the stored (decrypted) API key.

    Calls the real provider API to get available models, then enriches
    with known pricing data and category classification.

    Args:
        provider: Provider configuration

    Returns:
        List of models with model_identifier, model_name, category,
        input_cost_per_1k, output_cost_per_1k, context_window, supports_streaming
    """
    import requests

    provider_name = (provider.get('name') or '').lower()
    api_key = AIProviderRepository.get_decrypted_api_key(provider_name)

    if not api_key:
        logger.error(f"No decrypted API key for provider {provider_name}")
        return []

    try:
        # Dynamic dispatch: look up _fetch_{name}_models in this module
        fetcher_name = f'_fetch_{provider_name}_models'
        fetcher = globals().get(fetcher_name)
        if fetcher:
            return fetcher(api_key)
        logger.warning(f"No sync fetcher for provider: {provider_name}")
        return []
    except Exception as e:
        logger.error(f"Error fetching models from {provider_name}: {e}")
        return []


# ============================================================================
# Provider-specific model fetchers
# ============================================================================



def _classify_openai_model(model_id: str) -> str:
    """Classify an OpenAI model into a category based on its ID prefix.

    Uses the same pattern mapping as AIModelSyncHelpers.CATEGORY_PATTERNS
    from application/services/ai/models/sync_part2.py.
    """
    from app.application.services.ai.models.sync_part2 import AIModelSyncHelpers
    return AIModelSyncHelpers._get_category(model_id)


def _fetch_openai_models(api_key: str) -> list:
    """Fetch models from OpenAI API and classify them.

    Pricing is $0.00 — admin sets prices in the panel after sync.
    """
    import requests

    resp = requests.get(
        'https://api.openai.com/v1/models',
        headers={'Authorization': f'Bearer {api_key}'},
        timeout=15,
    )
    resp.raise_for_status()

    raw_models = resp.json().get('data', [])
    results = []

    for m in raw_models:
        model_id = m.get('id', '')
        if ':' in model_id or model_id.startswith('ft:'):
            continue

        category = _classify_openai_model(model_id)

        results.append({
            'model_identifier': model_id,
            'model_name': model_id,
            'category': category,
            'input_cost_per_1k': 0.0,
            'output_cost_per_1k': 0.0,
            'context_window': 0,
            'supports_streaming': category in ('chat', 'reasoning'),
        })

    return results


def _fetch_anthropic_models(api_key: str) -> list:
    """Fetch models from Anthropic API.

    Pricing is $0.00 — admin sets prices in the panel after sync.
    """
    import requests

    resp = requests.get(
        'https://api.anthropic.com/v1/models',
        headers={
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
        },
        timeout=15,
    )
    resp.raise_for_status()

    raw_models = resp.json().get('data', [])
    results = []

    for m in raw_models:
        model_id = m.get('id', '')

        results.append({
            'model_identifier': model_id,
            'model_name': model_id,
            'display_name': m.get('display_name', model_id),
            'category': 'chat',
            'input_cost_per_1k': 0.0,
            'output_cost_per_1k': 0.0,
            'context_window': 200000,
            'supports_streaming': True,
        })

    return results


def _fetch_google_models(api_key: str) -> list:
    """Fetch models from Google Generative AI API."""
    import requests

    resp = requests.get(
        f'https://generativelanguage.googleapis.com/v1/models?key={api_key}',
        timeout=15,
    )
    resp.raise_for_status()

    raw_models = resp.json().get('models', [])
    results = []

    for m in raw_models:
        model_name = m.get('name', '').replace('models/', '')
        display_name = m.get('displayName', model_name)

        # Google models are generally chat/reasoning
        category = 'chat'
        if 'embedding' in model_name.lower():
            category = 'embedding'
        elif 'vision' in model_name.lower():
            category = 'vision'

        results.append({
            'model_identifier': model_name,
            'model_name': model_name,
            'display_name': display_name,
            'category': category,
            'input_cost_per_1k': 0.0,
            'output_cost_per_1k': 0.0,
            'context_window': m.get('inputTokenLimit', 0),
            'supports_streaming': True,
        })

    return results


def _fetch_cohere_models(api_key: str) -> list:
    """Fetch models from Cohere API.

    Pricing is $0.00 — admin sets prices in the panel after sync.
    """
    import requests

    resp = requests.get(
        'https://api.cohere.com/v2/models',
        headers={'Authorization': f'Bearer {api_key}'},
        timeout=15,
    )
    resp.raise_for_status()

    results = []
    for m in resp.json().get('models', []):
        model_name = m.get('name', '')
        results.append({
            'model_identifier': model_name,
            'model_name': m.get('display_name', model_name),
            'category': 'chat',
            'input_cost_per_1k': 0.0,
            'output_cost_per_1k': 0.0,
            'context_window': m.get('context_length', 0),
            'supports_streaming': True,
        })
    return results


def _fetch_huggingface_models(api_key: str) -> list:
    """HuggingFace has no models list API — return empty for manual entry."""
    return []
