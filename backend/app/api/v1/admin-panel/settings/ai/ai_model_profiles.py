"""
AI Profiles CRUD Operations (DDD)

Endpoints for AI profile management:
- GET /api/v1/admin/settings/ai/profiles - List all profiles
- GET /api/v1/admin/settings/ai/profiles/<id> - Get profile by ID
- POST /api/v1/admin/settings/ai/profiles - Create profile
- PUT /api/v1/admin/settings/ai/profiles/<id> - Update profile
- DELETE /api/v1/admin/settings/ai/profiles/<id> - Delete profile

Uses:
- AIProfileFactory for creation with business rules
- Repository Pattern for persistence
- Publishes AIProfileUpdatedEvent on changes

Profile Types:
    - global: System-wide default
    - organisation: Organisation-specific override
    - user: User-specific preference
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
from datetime import datetime
import logging
import uuid

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.ai.profiles import AiModelProfilesRepository as AIProfileRepository
from app.services.audit_service import AuditService
from app.i18n.error_codes import ErrorCode, error_response
from app.utils.exceptions import NotFoundError, ValidationError

# DDD Core Domain
from .core.factory import AIProfileFactory
from .core.events import (
    AIProfileUpdatedEvent,
    EventPublisher,
    EventPriority
)

logger = logging.getLogger(__name__)

profiles_crud_bp = Blueprint(
    'ai_profiles_crud',
    __name__,
    url_prefix='/admin-panel/settings/ai/profiles'
)


# Valid profile types
VALID_PROFILE_TYPES = {'global', 'organisation', 'user'}


@profiles_crud_bp.route('', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def list_profiles() -> Tuple[Dict[str, Any], int]:
    """
    List all AI profiles.

    Query Parameters:
        profile_type (str): Filter by type (global, organisation, user)
        organisation_id (str): Filter by organisation
        user_id (str): Filter by user
        include_inactive (bool): Include inactive profiles (default: false)

    Returns:
        JSON response with profiles list
    """
    try:
        # Get profiles - use find_all_active for now (filters not yet implemented)
        profiles = AIProfileRepository.find_all_active()

        return jsonify({
            'success': True,
            'data': {
                'profiles': profiles or [],
                'count': len(profiles) if profiles else 0
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing AI profiles: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


@profiles_crud_bp.route('/<profile_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_profile(profile_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get AI profile by ID.

    Args:
        profile_id: The profile's UUID

    Returns:
        JSON response with profile details
    """
    try:
        profile = AIProfileRepository.find_by_id(profile_id)

        if not profile:
            return error_response(ErrorCode.AI_PROFILE_NOT_FOUND, 404, details={'profile_id': profile_id})

        return jsonify({
            'success': True,
            'data': profile
        }), 200

    except Exception as e:
        logger.error(f"Error getting profile {profile_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


@profiles_crud_bp.route('', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def create_profile() -> Tuple[Dict[str, Any], int]:
    """
    Create a new AI profile.

    Request Body:
        name (str): Profile name
        profile_type (str): Type (global, organisation, user)
        description (str, optional): Profile description
        organisation_id (str, optional): Organisation ID (required for organisation type)
        user_id (str, optional): User ID (required for user type)
        model_preferences (dict): Model preferences per category
        routing_rules (dict, optional): Learning method routing rules

    Returns:
        JSON response with created profile

    DDD: Uses AIProfileFactory to enforce business rules
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(ErrorCode.VALIDATION_REQUEST_BODY_REQUIRED, 400, details={})

        # Validate required fields
        required_fields = ['name', 'profile_type', 'model_preferences']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400,
                details={'missing_fields': missing_fields})

        # Validate profile type
        if data['profile_type'] not in VALID_PROFILE_TYPES:
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400,
                details={'field': 'profile_type', 'valid_values': list(VALID_PROFILE_TYPES)})

        # Business Rule: organisation profiles need organisation_id
        if data['profile_type'] == 'organisation' and not data.get('organisation_id'):
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400,
                details={'field': 'organisation_id', 'reason': 'required for organisation profiles'})

        # Business Rule: user profiles need user_id
        if data['profile_type'] == 'user' and not data.get('user_id'):
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400,
                details={'field': 'user_id', 'reason': 'required for user profiles'})

        # DDD: Use Factory to create profile with business rules
        try:
            profile_data = AIProfileFactory.create_profile(
                name=data['name'],
                profile_type=data['profile_type'],
                model_preferences=data['model_preferences'],
                description=data.get('description'),
                organisation_id=data.get('organisation_id'),
                user_id=data.get('user_id'),
                routing_rules=data.get('routing_rules')
            )
        except ValueError as ve:
            # Business rule violation
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400,
                details={'message': str(ve)})

        # Persist to repository
        created_profile = AIProfileRepository.create(profile_data)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='create_ai_profile',
            resource_type='ai_profile',
            resource_id=created_profile.get('profile_id'),
            details={
                'name': created_profile.get('name'),
                'profile_type': created_profile.get('profile_type')
            }
        )

        return jsonify({
            'success': True,
            'data': created_profile,
            'message': f'AI profile "{created_profile.get("name")}" created'
        }), 201

    except Exception as e:
        logger.error(f"Error creating AI profile: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


@profiles_crud_bp.route('/<profile_id>', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_profile(profile_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Update AI profile.

    Args:
        profile_id: The profile's UUID

    Request Body:
        name (str, optional): Profile name
        description (str, optional): Profile description
        model_preferences (dict, optional): Model preferences
        routing_rules (dict, optional): Routing rules
        active (bool, optional): Active status

    Returns:
        JSON response with updated profile

    DDD: Publishes AIProfileUpdatedEvent
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(ErrorCode.VALIDATION_REQUEST_BODY_REQUIRED, 400, details={})

        # Get existing profile
        existing_profile = AIProfileRepository.find_by_id(profile_id)
        if not existing_profile:
            return error_response(ErrorCode.AI_PROFILE_NOT_FOUND, 404,
                details={'profile_id': profile_id})

        # Update profile
        updated_profile = AIProfileRepository.update(profile_id, data)

        # DDD: Publish Domain Event
        event = AIProfileUpdatedEvent(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=profile_id,
            profile_id=profile_id,
            profile_name=updated_profile.get('name'),
            profile_type=updated_profile.get('profile_type'),
            changes=list(data.keys()),
            priority=EventPriority.MEDIUM
        )
        EventPublisher.publish(event)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='update_ai_profile',
            resource_type='ai_profile',
            resource_id=profile_id,
            details={'changes': data}
        )

        return jsonify({
            'success': True,
            'data': updated_profile,
            'message': f'Profile "{updated_profile.get("name")}" updated'
        }), 200

    except Exception as e:
        logger.error(f"Error updating AI profile {profile_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


@profiles_crud_bp.route('/<profile_id>', methods=['DELETE'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def delete_profile(profile_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Delete AI profile.

    Business Rule: Global profiles cannot be deleted (deactivate instead).

    Args:
        profile_id: The profile's UUID

    Returns:
        JSON response confirming deletion
    """
    try:
        # Get profile
        profile = AIProfileRepository.find_by_id(profile_id)
        if not profile:
            return error_response(ErrorCode.AI_PROFILE_NOT_FOUND, 404,
                details={'profile_id': profile_id})

        # Business Rule: Cannot delete global profiles
        if profile.get('profile_type') == 'global':
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400,
                details={'message': 'Global profiles cannot be deleted. Set active=false instead.'})

        # Delete profile
        AIProfileRepository.delete(profile_id)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='delete_ai_profile',
            resource_type='ai_profile',
            resource_id=profile_id,
            details={
                'name': profile.get('name'),
                'profile_type': profile.get('profile_type')
            }
        )

        return jsonify({
            'success': True,
            'message': f'Profile "{profile.get("name")}" deleted'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting AI profile {profile_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})
