"""
AI Models CRUD Operations (DDD)

Endpoints for AI model management with Domain-Driven Design:
- GET    /api/v1/admin/settings/ai/models - List all AI models
- GET    /api/v1/admin/settings/ai/models/<id> - Get model by ID
- PUT    /api/v1/admin/settings/ai/models/<id> - Update model
- POST   /api/v1/admin/settings/ai/models - Create custom model (uses Factory)
- DELETE /api/v1/admin/settings/ai/models/<id> - Delete model

Uses:
- AIModelFactory for creation with business rules
- AIModelSelectionService for queries
- Repository Pattern for persistence
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.api.middleware.auth import token_required
from app.infrastructure.security.permissions import require_permission, Permissions
from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
from app.infrastructure.persistence.repositories.ai.providers import AIProviderRepository
from app.services.audit_service import AuditService
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

# DDD Core Domain
from .core.factory import AIModelFactory
from .core.services import AIModelSelectionService
from .core.value_objects import ModelCategoryEnum

logger = logging.getLogger(__name__)

models_crud_bp = Blueprint(
    'ai_models_crud',
    __name__,
    url_prefix='/admin-panel/settings/ai/models'
)


@models_crud_bp.route('', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def list_ai_models() -> Tuple[Dict[str, Any], int]:
    """
    List all AI models.

    Query Parameters:
        include_inactive (bool): Include inactive models (default: false)
        provider (string): Filter by provider name (openai, anthropic, etc.)
        category (string): Filter by category (chat, reasoning, etc.)

    Returns:
        JSON response with models list, count, and available categories

    DDD: Uses AIModelSelectionService for filtering
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

        # Get models from repository
        if category:
            models = AIModelsRepository.get_by_category(
                category,
                active_only=not include_inactive
            )
        else:
            models = AIModelsRepository.get_all(
                include_inactive=include_inactive,
                provider_id=provider_id
            )

        # Get available categories
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
        logger.error(f"Error listing AI models: {e}")
        return error_response(ErrorCode.LIST_PLANS_ERROR, 500, details={'error': str(e)})


@models_crud_bp.route('/<int:model_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_model(model_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get AI model by ID.

    Args:
        model_id: The model's database ID

    Returns:
        JSON response with model details
    """
    try:
        model = AIModelsRepository.get_by_id(model_id)

        if not model:
            return error_response(ErrorCode.AI_MODEL_NOT_FOUND, 404, details={'model_id': model_id})

        return jsonify({
            'success': True,
            'data': model
        }), 200

    except Exception as e:
        logger.error(f"Error getting AI model {model_id}: {e}")
        return error_response(ErrorCode.AI_MODEL_NOT_FOUND, 500, details={'error': str(e)})


@models_crud_bp.route('', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def create_custom_model() -> Tuple[Dict[str, Any], int]:
    """
    Create a custom AI model.

    Request Body:
        provider_id (str): Provider identifier
        model_name (str): Model name
        category (str): Model category (chat, reasoning, etc.)
        input_cost_per_1k (float): Input cost per 1K tokens
        output_cost_per_1k (float): Output cost per 1K tokens
        margin_percent (float): Margin percentage (0-100)
        description (str, optional): Model description
        context_window (int, optional): Context window size

    Returns:
        JSON response with created model

    DDD: Uses AIModelFactory to enforce business rules
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(ErrorCode.VALIDATION_REQUEST_BODY_REQUIRED, 400)

        # Validate required fields
        required_fields = [
            'provider_id', 'model_name', 'category',
            'input_cost_per_1k', 'output_cost_per_1k', 'margin_percent'
        ]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, details={'missing_fields': missing_fields})

        # DDD: Use Factory to create model with business rules
        try:
            model_data = AIModelFactory.create_custom_model(
                provider_id=data['provider_id'],
                model_name=data['model_name'],
                category=data['category'],
                input_cost_per_1k=float(data['input_cost_per_1k']),
                output_cost_per_1k=float(data['output_cost_per_1k']),
                margin_percent=float(data['margin_percent']),
                description=data.get('description'),
                context_window=data.get('context_window')
            )
        except ValueError as ve:
            # Business rule violation (invalid category, margin out of range, etc.)
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400, details={'message': str(ve)})

        # Persist to repository
        created_model = AIModelsRepository.create(model_data)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='create_custom_ai_model',
            resource_type='ai_model',
            resource_id=created_model.get('model_id'),
            details={
                'model_name': created_model.get('model_name'),
                'category': created_model.get('category'),
                'margin_percent': data['margin_percent']
            }
        )

        return jsonify({
            'success': True,
            'data': created_model,
            'message': f'Custom model {created_model.get("model_name")} created'
        }), 201

    except Exception as e:
        logger.error(f"Error creating custom AI model: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


@models_crud_bp.route('/<int:model_id>', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_ai_model(model_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Update AI model.

    Args:
        model_id: The model's database ID

    Request Body:
        display_name (str, optional): Display name for the model
        description (str, optional): Model description
        active (bool, optional): Active status
        input_price_per_1k (float, optional): Input token price per 1K
        output_price_per_1k (float, optional): Output token price per 1K

    Returns:
        JSON response with updated model
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(ErrorCode.VALIDATION_REQUEST_BODY_REQUIRED, 400)

        # Check if model exists
        existing = AIModelsRepository.get_by_id(model_id)
        if not existing:
            return error_response(ErrorCode.AI_MODEL_NOT_FOUND, 404, details={'model_id': model_id})

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
        logger.error(f"Error updating AI model {model_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


@models_crud_bp.route('/<int:model_id>', methods=['DELETE'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def delete_ai_model(model_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Delete AI model.

    Business Rule: Only custom models can be deleted.
    Synced models from providers are deactivated instead.

    Args:
        model_id: The model's database ID

    Returns:
        JSON response with confirmation
    """
    try:
        model = AIModelsRepository.get_by_id(model_id)

        if not model:
            return error_response(ErrorCode.AI_MODEL_NOT_FOUND, 404, details={'model_id': model_id})

        # Business Rule: Only delete custom models, deactivate synced ones
        if model.get('synced_from_provider'):
            # Deactivate instead of delete
            AIModelsRepository.set_active(model_id, False)
            action = 'deactivated'
        else:
            # Delete custom model
            AIModelsRepository.delete(model_id)
            action = 'deleted'

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action=f'{action}_ai_model',
            resource_type='ai_model',
            resource_id=str(model_id),
            details={'model_name': model.get('model_name')}
        )

        return jsonify({
            'success': True,
            'message': f'Model {model.get("model_name")} {action}'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting AI model {model_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})
