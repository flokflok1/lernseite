"""
Feature Configuration Admin API - Rollout Management

Admin endpoints for managing progressive feature rollouts:
- Create rollout plans
- Manage rollout phases (5% → 25% → 50% → 100%)
- Pause/resume rollouts
- Rollback deployments

All endpoints require admin authentication.
"""

from flask import Blueprint, jsonify, request, g
from typing import Dict, Any, Tuple, Optional
import logging
from datetime import datetime

from app.database import get_db_connection
from app.repositories.feature_configuration_part2 import FeatureRolloutPlanRepository
from app.services.feature_configuration_rollout import FeatureConfigurationRolloutService
from app.services.feature_flags.cache import FeatureConfigurationCacheService
from app.utils.exceptions import (
    ValidationError,
    NotFoundError,
    ForbiddenError
)
from app.middleware.auth import token_required, admin_required

logger = logging.getLogger(__name__)

bp = Blueprint(
    'admin_feature_rollout',
    __name__,
    url_prefix='/admin/feature-configuration/rollout'
)


# ============================================================================
# ROLLOUT PLAN MANAGEMENT
# ============================================================================

@bp.route('/plans', methods=['GET'])
@token_required
@admin_required
def list_rollout_plans() -> Tuple[Dict[str, Any], int]:
    """
    List all rollout plans.

    Query Parameters:
        - feature_name: Filter by feature
        - status: Filter by status (planned, active, paused, completed, rolled_back)
        - limit: Max results (default 50)
        - offset: Skip N results

    Returns:
        200: List of rollout plans
        401: Unauthorized
        403: Forbidden

    Example:
        GET /api/v1/admin/feature-configuration/rollout/plans?status=active
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))

        with get_db_connection() as conn:
            repo = FeatureRolloutPlanRepository()

            filters = {}
            if request.args.get('feature_name'):
                filters['feature_name'] = request.args.get('feature_name')
            if request.args.get('status'):
                filters['status'] = request.args.get('status')

            plans = repo.find_all(filters=filters, limit=limit, offset=offset)
            total = repo.count(filters=filters)

        return jsonify({
            'success': True,
            'data': [p.to_dict() if hasattr(p, 'to_dict') else p for p in plans],
            'meta': {
                'total': total,
                'limit': limit,
                'offset': offset
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing rollout plans: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'LIST_PLANS_FAILED', 'message': 'Failed to list rollout plans'}
        }), 500


@bp.route('/plans', methods=['POST'])
@token_required
@admin_required
def create_rollout_plan() -> Tuple[Dict[str, Any], int]:
    """
    Create new rollout plan.

    Request Body:
        - feature_name: Feature to rollout (required)
        - plan_name: Human-readable name (required)
        - phase_1_percentage: Phase 1 rollout % (default 5)
        - phase_1_duration_hours: Phase 1 duration (default 12)
        - phase_2_percentage: Phase 2 rollout % (default 25)
        - phase_2_duration_hours: Phase 2 duration (default 24)
        - phase_3_percentage: Phase 3 rollout % (default 50)
        - phase_3_duration_hours: Phase 3 duration (default 48)
        - target_roles: Optional list of roles
        - target_tiers: Optional list of tiers
        - reason: Rollout reason

    Returns:
        201: Created rollout plan
        400: Validation error
        409: Plan already exists

    Example:
        POST /api/v1/admin/feature-configuration/rollout/plans
        {
            "feature_name": "ai_editor",
            "plan_name": "AI Editor Beta Rollout",
            "reason": "Beta testing with early adopters"
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required = ['feature_name', 'plan_name']
        missing = [f for f in required if f not in data]
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")

        # Create rollout plan
        plan = FeatureConfigurationRolloutService.create_rollout_plan(
            feature_name=data['feature_name'],
            plan_name=data['plan_name'],
            phase_1_percentage=data.get('phase_1_percentage', 5),
            phase_1_duration_hours=data.get('phase_1_duration_hours', 12),
            phase_2_percentage=data.get('phase_2_percentage', 25),
            phase_2_duration_hours=data.get('phase_2_duration_hours', 24),
            phase_3_percentage=data.get('phase_3_percentage', 50),
            phase_3_duration_hours=data.get('phase_3_duration_hours', 48),
            target_roles=data.get('target_roles'),
            target_tiers=data.get('target_tiers'),
            reason=data.get('reason')
        )

        logger.info(
            f"Rollout plan created: {data['feature_name']}",
            extra={'user_id': g.user_id, 'feature_name': data['feature_name']}
        )

        return jsonify({
            'success': True,
            'data': plan
        }), 201

    except ValidationError as e:
        logger.warning(f"Validation error: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 400

    except Exception as e:
        logger.error(f"Error creating rollout plan: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'CREATE_PLAN_FAILED', 'message': 'Failed to create rollout plan'}
        }), 500


@bp.route('/plans/<feature_name>/start', methods=['POST'])
@token_required
@admin_required
def start_rollout(feature_name: str) -> Tuple[Dict[str, Any], int]:
    """
    Start rollout (begin Phase 1).

    Returns:
        200: Updated rollout plan
        404: Plan not found
        409: Plan already active

    Example:
        POST /api/v1/admin/feature-configuration/rollout/plans/{feature_name}/start
    """
    try:
        plan = FeatureConfigurationRolloutService.start_rollout(feature_name)

        # Invalidate cache
        FeatureConfigurationCacheService.invalidate_feature(feature_name)

        logger.info(
            f"Rollout started: {feature_name}",
            extra={'user_id': g.user_id, 'feature_name': feature_name}
        )

        return jsonify({
            'success': True,
            'data': plan
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'PLAN_NOT_FOUND', 'message': str(e)}
        }), 404

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 409

    except Exception as e:
        logger.error(f"Error starting rollout: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'START_ROLLOUT_FAILED', 'message': 'Failed to start rollout'}
        }), 500


@bp.route('/plans/<feature_name>/advance', methods=['POST'])
@token_required
@admin_required
def advance_rollout_phase(feature_name: str) -> Tuple[Dict[str, Any], int]:
    """
    Advance rollout to next phase.

    Request Body:
        - new_phase: Target phase (1, 2, 3, or 4)

    Returns:
        200: Updated rollout plan
        400: Invalid phase
        404: Plan not found

    Example:
        POST /api/v1/admin/feature-configuration/rollout/plans/{feature_name}/advance
        {"new_phase": 2}
    """
    try:
        data = request.get_json()

        if 'new_phase' not in data:
            raise ValidationError("Missing required field: new_phase")

        new_phase = int(data['new_phase'])

        plan = FeatureConfigurationRolloutService.advance_phase(feature_name, new_phase)

        # Invalidate cache
        FeatureConfigurationCacheService.invalidate_feature(feature_name)

        logger.info(
            f"Rollout advanced: {feature_name} to phase {new_phase}",
            extra={'user_id': g.user_id, 'feature_name': feature_name, 'phase': new_phase}
        )

        return jsonify({
            'success': True,
            'data': plan
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 400

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'PLAN_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error advancing rollout: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'ADVANCE_FAILED', 'message': 'Failed to advance rollout'}
        }), 500


@bp.route('/plans/<feature_name>/pause', methods=['POST'])
@token_required
@admin_required
def pause_rollout(feature_name: str) -> Tuple[Dict[str, Any], int]:
    """
    Pause rollout (temporary stop).

    Request Body (optional):
        - reason: Reason for pausing

    Returns:
        200: Updated rollout plan
        404: Plan not found

    Example:
        POST /api/v1/admin/feature-configuration/rollout/plans/{feature_name}/pause
        {"reason": "High error rate detected"}
    """
    try:
        data = request.get_json() or {}

        plan = FeatureConfigurationRolloutService.pause_rollout(
            feature_name,
            reason=data.get('reason')
        )

        logger.info(
            f"Rollout paused: {feature_name}",
            extra={'user_id': g.user_id, 'feature_name': feature_name}
        )

        return jsonify({
            'success': True,
            'data': plan
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'PLAN_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error pausing rollout: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'PAUSE_FAILED', 'message': 'Failed to pause rollout'}
        }), 500


@bp.route('/plans/<feature_name>/resume', methods=['POST'])
@token_required
@admin_required
def resume_rollout(feature_name: str) -> Tuple[Dict[str, Any], int]:
    """
    Resume paused rollout.

    Returns:
        200: Updated rollout plan
        404: Plan not found

    Example:
        POST /api/v1/admin/feature-configuration/rollout/plans/{feature_name}/resume
    """
    try:
        plan = FeatureConfigurationRolloutService.resume_rollout(feature_name)

        # Invalidate cache
        FeatureConfigurationCacheService.invalidate_feature(feature_name)

        logger.info(
            f"Rollout resumed: {feature_name}",
            extra={'user_id': g.user_id, 'feature_name': feature_name}
        )

        return jsonify({
            'success': True,
            'data': plan
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'PLAN_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error resuming rollout: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'RESUME_FAILED', 'message': 'Failed to resume rollout'}
        }), 500


@bp.route('/plans/<feature_name>/rollback', methods=['POST'])
@token_required
@admin_required
def rollback_rollout(feature_name: str) -> Tuple[Dict[str, Any], int]:
    """
    Rollback rollout to previous state.

    Request Body:
        - reason: Reason for rollback (required)

    Returns:
        200: Updated rollout plan
        400: Validation error (missing reason)
        404: Plan not found

    Example:
        POST /api/v1/admin/feature-configuration/rollout/plans/{feature_name}/rollback
        {"reason": "Critical bug discovered in feature"}
    """
    try:
        data = request.get_json() or {}

        if 'reason' not in data:
            raise ValidationError("Missing required field: reason")

        plan = FeatureConfigurationRolloutService.rollback_rollout(
            feature_name,
            reason=data['reason']
        )

        # Invalidate cache
        FeatureConfigurationCacheService.invalidate_feature(feature_name)

        logger.warning(
            f"Rollout rolled back: {feature_name}",
            extra={'user_id': g.user_id, 'feature_name': feature_name, 'reason': data['reason']}
        )

        return jsonify({
            'success': True,
            'data': plan
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 400

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'PLAN_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error rolling back rollout: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'ROLLBACK_FAILED', 'message': 'Failed to rollback rollout'}
        }), 500


@bp.route('/plans/<feature_name>/stats', methods=['GET'])
@token_required
@admin_required
def get_rollout_stats(feature_name: str) -> Tuple[Dict[str, Any], int]:
    """
    Get rollout statistics.

    Returns:
        200: Rollout statistics
        404: Plan not found

    Example:
        GET /api/v1/admin/feature-configuration/rollout/plans/{feature_name}/stats
    """
    try:
        stats = FeatureConfigurationRolloutService.get_rollout_stats(feature_name)

        if stats.get('status') == 'not_found':
            raise NotFoundError(f"Rollout plan not found for feature {feature_name}")

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'PLAN_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error getting rollout stats: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'STATS_FAILED', 'message': 'Failed to get rollout statistics'}
        }), 500
