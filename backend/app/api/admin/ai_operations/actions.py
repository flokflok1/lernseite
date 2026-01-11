"""
AI Studio Actions - Quick Actions for Course Builder

Admin endpoints for managing quick actions in the AI Studio Kurs-Builder.
These are predefined AI-powered actions that can be executed on course content.

Endpoints:
- GET    /api/v1/admin/ai-studio/actions - List all actions
- GET    /api/v1/admin/ai-studio/actions/:category - Get actions by category
- GET    /api/v1/admin/ai-studio/actions/:actionId - Get action by ID
- GET    /api/v1/admin/ai-studio/actions/entity/:entityType - Get actions by entity type
- POST   /api/v1/admin/ai-studio/actions/execute - Execute an action
- GET    /api/v1/admin/ai-studio/actions/stats - Get usage statistics
- GET    /api/v1/admin/ai/usage-stats - Get AI usage statistics
- GET    /api/v1/admin/ai/profiles - List AI profiles

Phase B24-05 - AI Pipeline & Authoring System
ISO 27001:2013 compliant - Access control and audit logging
"""

from flask import request, jsonify, g
from typing import Dict, Any, List, Optional, Tuple
import logging

from app.api import api_v1
from app.middleware.auth import token_required, get_current_user
from app.security.permissions import require_permission, Permissions
from app.repositories.authoring_action import AuthoringActionRepository
from app.repositories.ai.usage import AIUsageRepository
from app.repositories.ai.profiles import AiModelProfilesRepository

logger = logging.getLogger(__name__)


# ============================================================================
# AI Studio Actions Endpoints
# ============================================================================

@api_v1.route('/admin/ai-studio/actions', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def list_ai_studio_actions() -> Tuple[Dict[str, Any], int]:
    """
    List all available AI Studio actions.

    Query params:
        - category: Filter by category (optional)
        - entity_type: Filter by entity type (optional)

    Returns:
        List of available actions with metadata
    """
    try:
        category = request.args.get('category')
        entity_type = request.args.get('entity_type')

        # Get user roles from JWT token
        current_user = get_current_user()
        user_roles = [current_user.get('role')] if current_user.get('role') else []

        # Fetch actions from database
        if category:
            actions = AuthoringActionRepository.get_by_category(category, roles=user_roles)
        elif entity_type:
            actions = AuthoringActionRepository.get_by_context_entity(entity_type)
        else:
            actions = AuthoringActionRepository.get_all_active(roles=user_roles)

        return jsonify({
            'success': True,
            'data': actions,
            'meta': {
                'total': len(actions),
                'category': category,
                'entity_type': entity_type
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing AI studio actions: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_STUDIO_ACTIONS_LIST_FAILED',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai-studio/actions/<category>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_actions_by_category(category: str) -> Tuple[Dict[str, Any], int]:
    """
    Get actions by category.

    Args:
        category: Action category (authoring, content, assessment, etc.)

    Returns:
        List of actions in the specified category
    """
    try:
        current_user = get_current_user()
        user_roles = [current_user.get('role')] if current_user.get('role') else []

        actions = AuthoringActionRepository.get_by_category(category, roles=user_roles)

        return jsonify({
            'success': True,
            'data': actions,
            'meta': {
                'total': len(actions),
                'category': category
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting actions by category '{category}': {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_STUDIO_ACTIONS_CATEGORY_FAILED',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai-studio/actions/<action_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_action_by_id(action_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get a specific action by ID.

    Args:
        action_id: Action ID (UUID)

    Returns:
        Action details
    """
    try:
        action = AuthoringActionRepository.find_by_id(action_id)

        if not action:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ACTION_NOT_FOUND',
                    'message': f'Action with ID {action_id} not found'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': action
        }), 200

    except Exception as e:
        logger.error(f"Error getting action {action_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_STUDIO_ACTION_GET_FAILED',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai-studio/actions/entity/<entity_type>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_actions_by_entity_type(entity_type: str) -> Tuple[Dict[str, Any], int]:
    """
    Get actions by entity type.

    Args:
        entity_type: Entity type (course, lesson, chapter, etc.)

    Returns:
        List of actions for the specified entity type
    """
    try:
        actions = AuthoringActionRepository.get_by_context_entity(entity_type)

        return jsonify({
            'success': True,
            'data': actions,
            'meta': {
                'total': len(actions),
                'entity_type': entity_type
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting actions by entity type '{entity_type}': {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_STUDIO_ACTIONS_ENTITY_FAILED',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai-studio/actions/execute', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def execute_ai_studio_action() -> Tuple[Dict[str, Any], int]:
    """
    Execute an AI Studio action.

    Request body:
        {
            "action_id": "uuid",
            "entity_id": "uuid",
            "entity_type": "course",
            "input_data": {...}
        }

    Returns:
        Execution result with generated content

    Note:
        This endpoint logs the action usage for analytics.
        Actual AI execution is handled by separate AI pipeline services.
    """
    try:
        data = request.get_json()
        action_id = data.get('action_id')
        entity_id = data.get('entity_id')
        entity_type = data.get('entity_type')
        input_data = data.get('input_data', {})

        if not action_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_ACTION_ID',
                    'message': 'action_id is required'
                }
            }), 400

        # Get current user
        current_user = get_current_user()
        user_id = current_user.get('user_id')

        # Verify action exists
        action = AuthoringActionRepository.find_by_id(action_id)
        if not action:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ACTION_NOT_FOUND',
                    'message': f'Action with ID {action_id} not found'
                }
            }), 404

        # Log action usage (before execution)
        AuthoringActionRepository.log_usage(
            action_id=action_id,
            user_id=user_id,
            context_data={
                'entity_id': entity_id,
                'entity_type': entity_type,
                'input_data': input_data
            },
            was_successful=True  # Will be updated after actual execution
        )

        # TODO: Implement actual AI execution via AI pipeline
        # For now, return placeholder indicating action was logged

        return jsonify({
            'success': True,
            'data': {
                'action_id': action_id,
                'entity_id': entity_id,
                'entity_type': entity_type,
                'status': 'queued',
                'message': 'Action execution queued. Implementation pending.',
                'result': None
            }
        }), 202  # Accepted for processing

    except Exception as e:
        logger.error(f"Error executing AI studio action: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_STUDIO_ACTION_EXECUTION_FAILED',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai-studio/actions/stats', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_ai_studio_actions_stats() -> Tuple[Dict[str, Any], int]:
    """
    Get usage statistics for AI Studio actions.

    Query params:
        - period: Time period in days (default: 30)
        - action_id: Filter by specific action (optional)

    Returns:
        Usage statistics including execution counts and popular actions
    """
    try:
        days = int(request.args.get('period', 30))
        action_id = request.args.get('action_id')

        # Get usage stats from repository
        stats = AuthoringActionRepository.get_usage_stats(action_id=action_id, days=days)

        # Get popular actions
        popular_actions = AuthoringActionRepository.get_popular_actions(limit=10, days=days)

        return jsonify({
            'success': True,
            'data': {
                **stats,
                'popular_actions': popular_actions
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting AI studio actions stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_STUDIO_ACTIONS_STATS_FAILED',
                'message': str(e)
            }
        }), 500


# ============================================================================
# AI Usage Statistics Endpoints
# ============================================================================

@api_v1.route('/admin/ai/usage-stats', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_ai_usage_stats() -> Tuple[Dict[str, Any], int]:
    """
    Get AI usage statistics for admin dashboard.

    Query params:
        - period: Time period (day, week, month, year) - default: month
        - user_id: Filter by user (optional)
        - organization_id: Filter by organization (optional)

    Returns:
        AI usage statistics including token usage, costs, provider breakdown
    """
    try:
        period = request.args.get('period', 'month')
        user_id = request.args.get('user_id')
        organization_id = request.args.get('organization_id')

        # Get usage stats from repository
        stats = AIUsageRepository.get_usage_stats(
            period=period,
            user_id=user_id,
            organization_id=organization_id
        )

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting AI usage stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_USAGE_STATS_FAILED',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/usage-stats/daily', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_ai_daily_usage() -> Tuple[Dict[str, Any], int]:
    """
    Get daily AI usage statistics.

    Query params:
        - days: Number of days (default: 30)
        - user_id: Filter by user (optional)
        - organization_id: Filter by organization (optional)

    Returns:
        Daily usage statistics
    """
    try:
        days = int(request.args.get('days', 30))
        user_id = request.args.get('user_id')
        organization_id = request.args.get('organization_id')

        daily_stats = AIUsageRepository.get_daily_usage(
            days=days,
            user_id=user_id,
            organization_id=organization_id
        )

        return jsonify({
            'success': True,
            'data': daily_stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting daily AI usage: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_DAILY_USAGE_FAILED',
                'message': str(e)
            }
        }), 500


# ============================================================================
# AI Profiles Endpoints
# ============================================================================

@api_v1.route('/admin/ai/profiles', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def list_ai_profiles() -> Tuple[Dict[str, Any], int]:
    """
    List all AI profiles.

    Query params:
        - active_only: Only return active profiles (default: true)

    Returns:
        List of AI profiles with their settings
    """
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        # Get profiles from repository
        if active_only:
            profiles = AiModelProfilesRepository.find_all_active()
        else:
            # Get all profiles (would need to implement in repository)
            profiles = AiModelProfilesRepository.find_all_active()

        return jsonify({
            'success': True,
            'data': profiles,
            'meta': {
                'total': len(profiles)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing AI profiles: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_PROFILES_LIST_FAILED',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/profiles/default', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_default_ai_profile() -> Tuple[Dict[str, Any], int]:
    """
    Get the default AI profile.

    Returns:
        Default AI profile settings
    """
    try:
        profile = AiModelProfilesRepository.find_default()

        if not profile:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_DEFAULT_PROFILE',
                    'message': 'No default AI profile configured'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': profile
        }), 200

    except Exception as e:
        logger.error(f"Error getting default AI profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_PROFILE_DEFAULT_FAILED',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/ai/profiles/<profile_key>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_ai_profile_by_key(profile_key: str) -> Tuple[Dict[str, Any], int]:
    """
    Get an AI profile by key.

    Args:
        profile_key: Profile key identifier

    Returns:
        AI profile settings
    """
    try:
        profile = AiModelProfilesRepository.find_by_key(profile_key)

        if not profile:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PROFILE_NOT_FOUND',
                    'message': f'AI profile with key {profile_key} not found'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': profile
        }), 200

    except Exception as e:
        logger.error(f"Error getting AI profile '{profile_key}': {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_PROFILE_GET_FAILED',
                'message': str(e)
            }
        }), 500
