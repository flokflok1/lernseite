"""
AI Providers CRUD Operations (DDD)

Endpoints for AI provider management:
- GET    /api/v1/admin/settings/ai/providers - List all providers
- GET    /api/v1/admin/settings/ai/providers/<id> - Get provider by ID
- POST   /api/v1/admin/settings/ai/providers - Create provider (uses Factory)
- PUT    /api/v1/admin/settings/ai/providers/<id> - Update provider
- DELETE /api/v1/admin/settings/ai/providers/<id> - Delete provider

Uses:
- AIProviderFactory for creation with business rules
- Repository Pattern for persistence
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.api.middleware.auth import permission_required
from app.infrastructure.persistence.repositories.ai.providers import AIProviderRepository
from app.application.services.system.audit.service import AuditService
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

# DDD Core Domain
from .core.factory import AIProviderFactory

logger = logging.getLogger(__name__)

providers_crud_bp = Blueprint(
    'ai_providers_crud',
    __name__,
    url_prefix='/admin-panel/settings/ai/providers'
)


@providers_crud_bp.route('', methods=['GET'])
@permission_required('admin.system:read')
def list_providers() -> Tuple[Dict[str, Any], int]:
    """
    List all AI providers.

    Query Parameters:
        include_inactive (bool): Include inactive providers (default: false)

    Returns:
        JSON response with providers list
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

        providers = AIProviderRepository.get_all(include_inactive=include_inactive)

        # Don't expose encrypted API keys
        for provider in providers:
            provider.pop('api_key_encrypted', None)

        return jsonify({
            'success': True,
            'data': {
                'providers': providers,
                'count': len(providers)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing providers: {e}")
        return error_response(ErrorCode.LIST_PLANS_ERROR, 500, details={'error': str(e)})


@providers_crud_bp.route('/<int:provider_id>', methods=['GET'])
@permission_required('admin.system:read')
def get_provider(provider_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get AI provider by ID.

    Args:
        provider_id: The provider's database ID

    Returns:
        JSON response with provider details
    """
    try:
        provider = AIProviderRepository.get_by_id(provider_id)

        if not provider:
            return error_response(ErrorCode.AI_PROVIDER_NOT_FOUND, 404, details={'provider_id': provider_id})

        # Don't expose encrypted API key
        provider.pop('api_key_encrypted', None)

        return jsonify({
            'success': True,
            'data': provider
        }), 200

    except Exception as e:
        logger.error(f"Error getting provider {provider_id}: {e}")
        return error_response(ErrorCode.AI_PROVIDER_NOT_FOUND, 500, details={'error': str(e)})


@providers_crud_bp.route('', methods=['POST'])
@permission_required('admin.system:write')
def create_provider() -> Tuple[Dict[str, Any], int]:
    """
    Create a new AI provider.

    Request Body:
        name (str): Internal provider name (e.g., 'openai')
        display_name (str): User-facing name (e.g., 'OpenAI')
        description (str, optional): Provider description
        base_url (str, optional): API base URL

    Returns:
        JSON response with created provider

    DDD: Uses AIProviderFactory to enforce business rules
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(ErrorCode.VALIDATION_REQUEST_BODY_REQUIRED, 400)

        # Validate required fields
        required_fields = ['name', 'display_name']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, details={'missing_fields': missing_fields})

        # Check if provider with this name already exists
        existing = AIProviderRepository.get_by_name(data['name'])
        if existing:
            return error_response(ErrorCode.CONFLICT, 409, details={'name': data['name']})

        # DDD: Use Factory to create provider with business rules
        provider_data = AIProviderFactory.create_provider(
            name=data['name'],
            display_name=data['display_name'],
            description=data.get('description'),
            base_url=data.get('base_url')
        )

        # Persist to repository
        created_provider = AIProviderRepository.create(provider_data)

        # Don't expose encrypted API key
        created_provider.pop('api_key_encrypted', None)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='create_ai_provider',
            resource_type='ai_provider',
            resource_id=created_provider.get('provider_id'),
            details={
                'name': created_provider.get('name'),
                'display_name': created_provider.get('display_name')
            }
        )

        return jsonify({
            'success': True,
            'data': created_provider,
            'message': f'Provider {created_provider.get("display_name")} created'
        }), 201

    except Exception as e:
        logger.error(f"Error creating provider: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


@providers_crud_bp.route('/<int:provider_id>', methods=['PUT'])
@permission_required('admin.system:write')
def update_provider(provider_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Update AI provider.

    Args:
        provider_id: The provider's database ID

    Request Body:
        display_name (str, optional): User-facing name
        description (str, optional): Provider description
        base_url (str, optional): API base URL
        active (bool, optional): Active status

    Returns:
        JSON response with updated provider
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(ErrorCode.VALIDATION_REQUEST_BODY_REQUIRED, 400)

        # Check if provider exists
        existing = AIProviderRepository.get_by_id(provider_id)
        if not existing:
            return error_response(ErrorCode.AI_PROVIDER_NOT_FOUND, 404, details={'provider_id': provider_id})

        # Update provider
        updated_provider = AIProviderRepository.update(provider_id, data)

        # Don't expose encrypted API key
        updated_provider.pop('api_key_encrypted', None)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='update_ai_provider',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            details={'changes': data}
        )

        return jsonify({
            'success': True,
            'data': updated_provider,
            'message': f'Provider {updated_provider.get("display_name")} updated'
        }), 200

    except Exception as e:
        logger.error(f"Error updating provider {provider_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


@providers_crud_bp.route('/<int:provider_id>', methods=['DELETE'])
@permission_required('admin.system:write')
def delete_provider(provider_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Delete AI provider.

    Business Rule: Provider can only be deleted if it has no active models.
    Otherwise, deactivate the provider instead.

    Args:
        provider_id: The provider's database ID

    Returns:
        JSON response with confirmation
    """
    try:
        provider = AIProviderRepository.get_by_id(provider_id)

        if not provider:
            return error_response(ErrorCode.AI_PROVIDER_NOT_FOUND, 404, details={'provider_id': provider_id})

        # Business Rule: Check if provider has active models
        from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
        active_models = AIModelsRepository.get_by_provider(provider_id, active_only=True)

        if active_models:
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400, details={'message': f'Provider has {len(active_models)} active models. Deactivate them first or set provider as inactive.', 'active_model_count': len(active_models)})

        # Delete provider
        AIProviderRepository.delete(provider_id)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='delete_ai_provider',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            details={'name': provider.get('name')}
        )

        return jsonify({
            'success': True,
            'message': f'Provider {provider.get("display_name")} deleted'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting provider {provider_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})
