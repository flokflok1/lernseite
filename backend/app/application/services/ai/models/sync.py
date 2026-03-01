"""
LernsystemX AI Model Sync Service

Synchronizes AI models from provider APIs:
- OpenAI /v1/models endpoint
- Anthropic models (static list)
- Google Gemini models

Note: Prices are NOT available via API and must be maintained manually.

Phase KI-Architektur - Model Management
"""

import os
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from app.infrastructure.persistence.repositories.ai.config.providers import AIProviderRepository
from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
from app.application.services.ai.adapter import AIAdapter
from app.application.services.ai.models.sync_part2 import AIModelSyncHelpers


class AIModelSyncService(AIModelSyncHelpers):
    """
    Service for synchronizing AI models from provider APIs

    Features:
    - Fetches available models from OpenAI API
    - Merges with local price data (not available via API)
    - Updates ai_models table
    - Tracks sync history
    """

    # Static price data from ai_adapter.py (prices not available via API)
    OPENAI_PRICES = AIAdapter.PROVIDERS['openai']['models']
    ANTHROPIC_PRICES = AIAdapter.PROVIDERS['anthropic']['models']
    GOOGLE_PRICES = AIAdapter.PROVIDERS['google']['models']

    @classmethod
    def sync_all_providers(cls) -> Dict[str, Any]:
        """
        Sync models from all active providers

        Returns:
            Sync results for each provider
        """
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'providers': {},
            'total_synced': 0,
            'total_added': 0,
            'total_updated': 0,
            'errors': []
        }

        providers = AIProviderRepository.get_all(include_inactive=False)

        for provider in providers:
            provider_name = provider.get('name')

            try:
                if provider_name == 'openai':
                    result = cls.sync_openai_models()
                elif provider_name == 'anthropic':
                    result = cls.sync_anthropic_models()
                elif provider_name == 'google':
                    result = cls.sync_google_models()
                else:
                    result = {'skipped': True, 'reason': 'No sync implementation'}

                results['providers'][provider_name] = result
                results['total_synced'] += result.get('synced', 0)
                results['total_added'] += result.get('added', 0)
                results['total_updated'] += result.get('updated', 0)

            except Exception as e:
                results['errors'].append({
                    'provider': provider_name,
                    'error': str(e)
                })

        return results

    @classmethod
    def sync_openai_models(cls) -> Dict[str, Any]:
        """
        Sync models from OpenAI /v1/models API

        Returns:
            Sync result with stats
        """
        result = {
            'provider': 'openai',
            'synced': 0,
            'added': 0,
            'updated': 0,
            'api_models': 0,
            'errors': []
        }

        # Get API key
        api_key = AIProviderRepository.get_decrypted_api_key('openai')
        if not api_key:
            result['errors'].append('No API key configured for OpenAI')
            return result

        # Get provider ID
        provider = AIProviderRepository.get_by_name('openai')
        if not provider:
            result['errors'].append('OpenAI provider not found in database')
            return result

        provider_id = provider.get('provider_id')

        # Fetch models from OpenAI API
        try:
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=30
            )
            response.raise_for_status()
            api_data = response.json()
        except requests.RequestException as e:
            result['errors'].append(f'API request failed: {str(e)}')
            return result

        models = api_data.get('data', [])
        result['api_models'] = len(models)

        # Process each model
        for model in models:
            model_id = model.get('id')
            if not model_id:
                continue

            # Skip internal/system models
            if model_id.startswith('ft:'):  # Fine-tuned models
                continue
            if ':' in model_id and not model_id.startswith('gpt-'):  # Snapshot models
                continue

            try:
                model_data = cls._build_model_data(model_id, 'openai')
                existing = AIModelsRepository.get_by_name(model_id, 'openai')

                if existing:
                    # Update existing
                    AIModelsRepository.update(existing['model_id'], model_data)
                    result['updated'] += 1
                else:
                    # Create new
                    model_data['provider_id'] = provider_id
                    model_data['model_name'] = model_id
                    AIModelsRepository.upsert(provider_id, model_id, model_data)
                    result['added'] += 1

                result['synced'] += 1

            except Exception as e:
                result['errors'].append(f'Error processing {model_id}: {str(e)}')

        return result

    @classmethod
    def sync_anthropic_models(cls) -> Dict[str, Any]:
        """
        Sync Anthropic models (static list - no API for model listing)

        Returns:
            Sync result with stats
        """
        result = {
            'provider': 'anthropic',
            'synced': 0,
            'added': 0,
            'updated': 0,
            'errors': []
        }

        # Get provider ID
        provider = AIProviderRepository.get_by_name('anthropic')
        if not provider:
            result['errors'].append('Anthropic provider not found in database')
            return result

        provider_id = provider.get('provider_id')

        # Use static list from ai_adapter
        for model_id, pricing in cls.ANTHROPIC_PRICES.items():
            try:
                model_data = {
                    'display_name': cls._format_display_name(model_id),
                    'model_type': 'chat',
                    'category': 'chat',
                    'description': cls._get_model_description(model_id, 'anthropic'),
                    'cost_level': cls._get_cost_level(pricing.get('input_price', 0)),
                    'speed': 'fast' if 'haiku' in model_id.lower() else 'medium',
                    'context_window': pricing.get('context_window'),
                    'max_output_tokens': pricing.get('max_tokens'),
                    'supports_vision': True,  # Claude 3+ supports vision
                    'supports_functions': True,
                    'input_price_per_1k': pricing.get('input_price'),
                    'output_price_per_1k': pricing.get('output_price'),
                    'active': True,
                    'is_default': 'sonnet' in model_id.lower()
                }

                existing = AIModelsRepository.get_by_name(model_id, 'anthropic')

                if existing:
                    AIModelsRepository.update(existing['model_id'], model_data)
                    result['updated'] += 1
                else:
                    AIModelsRepository.upsert(provider_id, model_id, model_data)
                    result['added'] += 1

                result['synced'] += 1

            except Exception as e:
                result['errors'].append(f'Error processing {model_id}: {str(e)}')

        return result

    @classmethod
    def sync_google_models(cls) -> Dict[str, Any]:
        """
        Sync Google Gemini models (static list)

        Returns:
            Sync result with stats
        """
        result = {
            'provider': 'google',
            'synced': 0,
            'added': 0,
            'updated': 0,
            'errors': []
        }

        # Get provider ID
        provider = AIProviderRepository.get_by_name('google')
        if not provider:
            result['errors'].append('Google provider not found in database')
            return result

        provider_id = provider.get('provider_id')

        # Use static list from ai_adapter
        for model_id, pricing in cls.GOOGLE_PRICES.items():
            try:
                model_data = {
                    'display_name': cls._format_display_name(model_id),
                    'model_type': 'chat',
                    'category': 'chat',
                    'description': cls._get_model_description(model_id, 'google'),
                    'cost_level': cls._get_cost_level(pricing.get('input_price', 0)),
                    'speed': 'very_fast' if 'flash' in model_id.lower() else 'medium',
                    'context_window': pricing.get('context_window'),
                    'max_output_tokens': pricing.get('max_tokens'),
                    'supports_vision': True,
                    'supports_functions': True,
                    'input_price_per_1k': pricing.get('input_price'),
                    'output_price_per_1k': pricing.get('output_price'),
                    'active': True,
                    'is_default': model_id == 'gemini-2.0-flash'
                }

                existing = AIModelsRepository.get_by_name(model_id, 'google')

                if existing:
                    AIModelsRepository.update(existing['model_id'], model_data)
                    result['updated'] += 1
                else:
                    AIModelsRepository.upsert(provider_id, model_id, model_data)
                    result['added'] += 1

                result['synced'] += 1

            except Exception as e:
                result['errors'].append(f'Error processing {model_id}: {str(e)}')

        return result

    @classmethod
    def sync_from_adapter(cls) -> Dict[str, Any]:
        """
        Sync all models from ai_adapter.py static definitions

        This adds all models defined in AIAdapter.PROVIDERS to the database,
        including prices which are not available via API.

        Returns:
            Sync result with stats
        """
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'providers': {},
            'total_synced': 0,
            'total_added': 0,
            'total_updated': 0,
            'errors': []
        }

        for provider_name, provider_config in AIAdapter.PROVIDERS.items():
            provider = AIProviderRepository.get_by_name(provider_name)
            if not provider:
                result['errors'].append(f'Provider {provider_name} not found in database')
                continue

            provider_id = provider.get('provider_id')
            provider_result = {
                'synced': 0,
                'added': 0,
                'updated': 0,
                'errors': []
            }

            for model_id, pricing in provider_config.get('models', {}).items():
                try:
                    model_data = cls._build_model_data(model_id, provider_name)
                    existing = AIModelsRepository.get_by_name(model_id, provider_name)

                    if existing:
                        AIModelsRepository.update(existing['model_id'], model_data)
                        provider_result['updated'] += 1
                    else:
                        AIModelsRepository.upsert(provider_id, model_id, model_data)
                        provider_result['added'] += 1

                    provider_result['synced'] += 1

                except Exception as e:
                    provider_result['errors'].append(f'Error processing {model_id}: {str(e)}')

            result['providers'][provider_name] = provider_result
            result['total_synced'] += provider_result['synced']
            result['total_added'] += provider_result['added']
            result['total_updated'] += provider_result['updated']

        return result

    @classmethod
    def get_sync_status(cls) -> Dict[str, Any]:
        """
        Get current sync status and stats

        Returns:
            Sync status information
        """
        stats = AIModelsRepository.get_stats()
        categories = AIModelsRepository.get_categories()

        return {
            'stats': stats,
            'categories': categories,
            'adapter_models': {
                'openai': len(cls.OPENAI_PRICES),
                'anthropic': len(cls.ANTHROPIC_PRICES),
                'google': len(cls.GOOGLE_PRICES)
            }
        }
