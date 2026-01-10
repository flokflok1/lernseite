"""
AI Profiles CRUD Operations (DDD)

Endpoints for AI profile management:
- GET /api/v1/admin/ai/profiles - List all profiles
- GET /api/v1/admin/ai/profiles/<id> - Get profile by ID
- POST /api/v1/admin/ai/profiles - Create profile
- PUT /api/v1/admin/ai/profiles/<id> - Update profile
- DELETE /api/v1/admin/ai/profiles/<id> - Delete profile

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
from app.repositories.ai_models.profiles import AIProfileRepository
from app.services.audit_service import AuditService

# DDD Core Domain
from src.api.ai.core import AIProfileFactory
from src.api.ai.core import (
    AIProfileUpdatedEvent,
    EventPublisher,
    EventPriority
)

logger = logging.getLogger(__name__)

profiles_crud_bp = Blueprint(
    'ai_profiles_crud',
    __name__,
    url_prefix='/api/v1/admin/ai/profiles'
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
        # Get filters
        filters = {}

        profile_type = request.args.get('profile_type')
        if profile_type:
            if profile_type not in VALID_PROFILE_TYPES:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_PROFILE_TYPE',
                        'message': f'Invalid profile type. Must be one of: {", ".join(VALID_PROFILE_TYPES)}'
                    }
                }), 400
            filters['profile_type'] = profile_type

        if request.args.get('organisation_id'):
            filters['organisation_id'] = request.args.get('organisation_id')

        if request.args.get('user_id'):
            filters['user_id'] = request.args.get('user_id')

        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

        # Get profiles
        profiles = AIProfileRepository.get_all(
            filters=filters,
            include_inactive=include_inactive
        )

        return jsonify({
            'success': True,
            'data': {
                'profiles': profiles,
                'count': len(profiles)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing AI profiles: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'LIST_PROFILES_ERROR',
                'message': str(e)
            }
        }), 500


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
        profile = AIProfileRepository.get_by_id(profile_id)

        if not profile:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PROFILE_NOT_FOUND',
                    'message': f'Profile {profile_id} not found'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': profile
        }), 200

    except Exception as e:
        logger.error(f"Error getting profile {profile_id}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_PROFILE_ERROR',
                'message': str(e)
            }
        }), 500


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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Request body required'
                }
            }), 400

        # Validate required fields
        required_fields = ['name', 'profile_type', 'model_preferences']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }
            }), 400

        # Validate profile type
        if data['profile_type'] not in VALID_PROFILE_TYPES:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PROFILE_TYPE',
                    'message': f'Invalid profile type. Must be one of: {", ".join(VALID_PROFILE_TYPES)}'
                }
            }), 400

        # Business Rule: organisation profiles need organisation_id
        if data['profile_type'] == 'organisation' and not data.get('organisation_id'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_ORGANISATION_ID',
                    'message': 'organisation_id required for organisation profiles'
                }
            }), 400

        # Business Rule: user profiles need user_id
        if data['profile_type'] == 'user' and not data.get('user_id'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_USER_ID',
                    'message': 'user_id required for user profiles'
                }
            }), 400

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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BUSINESS_RULE_VIOLATION',
                    'message': str(ve)
                }
            }), 400

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
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATE_PROFILE_ERROR',
                'message': str(e)
            }
        }), 500


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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Request body required'
                }
            }), 400

        # Get existing profile
        existing_profile = AIProfileRepository.get_by_id(profile_id)
        if not existing_profile:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PROFILE_NOT_FOUND',
                    'message': f'Profile {profile_id} not found'
                }
            }), 404

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
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_PROFILE_ERROR',
                'message': str(e)
            }
        }), 500


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
        profile = AIProfileRepository.get_by_id(profile_id)
        if not profile:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PROFILE_NOT_FOUND',
                    'message': f'Profile {profile_id} not found'
                }
            }), 404

        # Business Rule: Cannot delete global profiles
        if profile.get('profile_type') == 'global':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CANNOT_DELETE_GLOBAL',
                    'message': 'Global profiles cannot be deleted. Set active=false instead.'
                }
            }), 400

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
        return jsonify({
            'success': False,
            'error': {
                'code': 'DELETE_PROFILE_ERROR',
                'message': str(e)
            }
        }), 500
