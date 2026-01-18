"""
AI Models Default Management (DDD)

Endpoints for default model management:
- PUT /api/v1/admin/settings/ai/models/<id>/default - Set model as default
- PUT /api/v1/admin/settings/ai/models/<id>/active - Toggle model active status
- GET /api/v1/admin/settings/ai/models/default/<category> - Get default model for category

Uses:
- AIModelDefaultSetEvent - Published when default changes
- Repository Pattern for persistence
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
from datetime import datetime
import logging
import uuid

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.ai_models import AIModelsRepository
from app.services.audit_service import AuditService
from app.i18n.error_codes import ErrorCode
from app.i18n.error_codes import error_response

# DDD Core Domain
from .core.events import (
    AIModelDefaultSetEvent,
    EventPublisher,
    EventPriority
)

logger = logging.getLogger(__name__)

models_defaults_bp = Blueprint(
    'ai_models_defaults',
    __name__,
    url_prefix='/admin-panel/settings/ai/models'
)


@models_defaults_bp.route('/<int:model_id>/default', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def set_default_model(model_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Set model as default for its category.

    Business Rule: Only one default per category.
    Previous default is automatically unset.

    Args:
        model_id: The model's database ID

    Returns:
        JSON response with updated model

    DDD: Publishes AIModelDefaultSetEvent
    """
    try:
        # Get previous default for this category
        model = AIModelsRepository.get_by_id(model_id)
        if not model:
            return error_response(ErrorCode.AI_MODEL_NOT_FOUND, 404,
                details={'model_id': model_id})

        category = model.get('category')
        previous_default = AIModelsRepository.get_default_model(category)
        previous_default_id = previous_default.get('model_id') if previous_default else None

        # Set as default (repository handles unsetting previous default)
        updated_model = AIModelsRepository.set_default(model_id)

        # DDD: Publish Domain Event
        event = AIModelDefaultSetEvent(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=str(model_id),
            model_id=str(model_id),
            model_name=updated_model.get('model_name'),
            category=category,
            previous_default_id=str(previous_default_id) if previous_default_id else None,
            priority=EventPriority.MEDIUM
        )
        EventPublisher.publish(event)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='set_default_ai_model',
            resource_type='ai_model',
            resource_id=str(model_id),
            details={
                'category': category,
                'previous_default_id': previous_default_id
            }
        )

        return jsonify({
            'success': True,
            'data': updated_model,
            'message': f'{updated_model.get("model_name")} is now the default model for {category}'
        }), 200

    except Exception as e:
        logger.error(f"Error setting default model {model_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500,
            details={'error': str(e)})


@models_defaults_bp.route('/<int:model_id>/active', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def toggle_model_active(model_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Toggle model active status.

    Args:
        model_id: The model's database ID

    Request Body:
        active (bool): New active status

    Returns:
        JSON response with updated model
    """
    try:
        data = request.get_json()
        if data is None or 'active' not in data:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400,
                details={'field': 'active'})

        model = AIModelsRepository.set_active(model_id, data['active'])

        if not model:
            return error_response(ErrorCode.AI_MODEL_NOT_FOUND, 404,
                details={'model_id': model_id})

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action=f'{"activate" if data["active"] else "deactivate"}_ai_model',
            resource_type='ai_model',
            resource_id=str(model_id),
            details={'model_name': model.get('model_name')}
        )

        return jsonify({
            'success': True,
            'data': model,
            'message': f'Model {model.get("model_name")} {"activated" if data["active"] else "deactivated"}'
        }), 200

    except Exception as e:
        logger.error(f"Error toggling model active status {model_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500,
            details={'error': str(e)})


@models_defaults_bp.route('/default/<category>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_default_model_for_category(category: str) -> Tuple[Dict[str, Any], int]:
    """
    Get default model for a category.

    Args:
        category: Model category (chat, reasoning, audio, image, etc.)

    Returns:
        JSON response with default model for the category
    """
    try:
        model = AIModelsRepository.get_default_model(category)

        if not model:
            return error_response(ErrorCode.AI_MODEL_NOT_FOUND, 404,
                details={'category': category, 'message': 'No default model configured'})

        return jsonify({
            'success': True,
            'data': model
        }), 200

    except Exception as e:
        logger.error(f"Error getting default model for category {category}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500,
            details={'error': str(e)})
