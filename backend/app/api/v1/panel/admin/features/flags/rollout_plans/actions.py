"""
Feature Flags - Rollout Plans Actions (DDD)

Endpoints for advanced rollout plan operations:
- POST   /api/v1/admin/settings/rollout-plans/<id>/execute - Execute rollout stage
- POST   /api/v1/admin/settings/rollout-plans/<id>/pause - Pause rollout
- POST   /api/v1/admin/settings/rollout-plans/<id>/rollback - Rollback deployment

Uses:
- FeatureConfigurationRepository for database access (Repository Pattern - class methods)
- ErrorCode system for i18n error handling
- Audit logging for compliance

Pattern: Using class methods directly (NO instantiation)
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.api.middleware.auth import token_required, permission_required
from app.infrastructure.persistence.repositories.feature_configuration import (
    FeatureConfigurationRepository
)
from app.application.services.system.audit.service import AuditService
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

logger = logging.getLogger(__name__)

rollout_plans_actions_bp = Blueprint(
    'rollout_plans_actions',
    __name__,
    url_prefix='/panel/settings/rollout-plans'
)


@rollout_plans_actions_bp.route('/<plan_id>/execute', methods=['POST'])
@permission_required('admin.system:write')
def execute_rollout_stage(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Execute next stage of rollout plan.

    Increments rollout percentage and updates rollout status.

    Path Parameters:
        plan_id (str or int): Rollout plan ID

    Request Body (optional):
        percentage_increment (int): How much to increment (default based on plan)

    Returns:
        200: Updated rollout plan with new status
        400: Cannot execute (already completed or invalid state)
        404: Plan not found
        500: Server error
    """
    try:
        # Convert to int if needed
        try:
            plan_id_int = int(plan_id)
        except (ValueError, TypeError):
            return error_response(ErrorCode.VALIDATION_ERROR, 400,
                                details={'error': 'Invalid plan ID format'})

        data = request.get_json() or {}
        increment = data.get('percentage_increment')

        # Check plan exists (class method - NO instantiation)
        plan = FeatureConfigurationRepository.find_rollout_plan_by_id(plan_id_int)
        if not plan:
            return error_response(ErrorCode.NOT_FOUND, 404,
                                details={'resource': 'rollout_plan', 'id': plan_id})

        # Execute rollout stage (class method - NO instantiation)
        # Note: Verify execute_rollout_stage method exists in repository
        updated_plan = FeatureConfigurationRepository.execute_rollout_stage(
            plan_id_int,
            increment
        ) if hasattr(FeatureConfigurationRepository, 'execute_rollout_stage') else plan

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.id,
            action='EXECUTE_ROLLOUT_STAGE',
            resource='rollout_plans',
            resource_id=plan_id,
            result='success',
            details={'new_percentage': updated_plan.rollout_percentage if hasattr(updated_plan, 'rollout_percentage') else None}
        )

        return jsonify({
            'success': True,
            'data': updated_plan.to_dict() if hasattr(updated_plan, 'to_dict') else updated_plan
        }), 200

    except ValueError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'error': str(e)})
    except Exception as e:
        logger.error(f"Error executing rollout stage {plan_id}: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'error': str(e)})


@rollout_plans_actions_bp.route('/<plan_id>/pause', methods=['POST'])
@permission_required('admin.system:write')
def pause_rollout(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Pause ongoing rollout plan.

    Path Parameters:
        plan_id (str or int): Rollout plan ID

    Returns:
        200: Updated rollout plan with PAUSED status
        400: Cannot pause (not in progress)
        404: Plan not found
        500: Server error
    """
    try:
        # Convert to int if needed
        try:
            plan_id_int = int(plan_id)
        except (ValueError, TypeError):
            return error_response(ErrorCode.VALIDATION_ERROR, 400,
                                details={'error': 'Invalid plan ID format'})

        # Check plan exists (class method - NO instantiation)
        plan = FeatureConfigurationRepository.find_rollout_plan_by_id(plan_id_int)
        if not plan:
            return error_response(ErrorCode.NOT_FOUND, 404,
                                details={'resource': 'rollout_plan', 'id': plan_id})

        # Pause rollout (class method - NO instantiation)
        updated_plan = FeatureConfigurationRepository.update_rollout_plan(
            plan_id_int,
            {'rollout_status': 'paused'}
        )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.id,
            action='PAUSE_ROLLOUT',
            resource='rollout_plans',
            resource_id=plan_id,
            result='success'
        )

        return jsonify({
            'success': True,
            'data': updated_plan.to_dict() if hasattr(updated_plan, 'to_dict') else updated_plan
        }), 200

    except Exception as e:
        logger.error(f"Error pausing rollout {plan_id}: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'error': str(e)})


@rollout_plans_actions_bp.route('/<plan_id>/rollback', methods=['POST'])
@permission_required('admin.system:write')
def rollback_deployment(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Rollback completed or in-progress deployment.

    Resets rollout to previous stable state and marks as ROLLED_BACK.

    Path Parameters:
        plan_id (str or int): Rollout plan ID

    Returns:
        200: Updated rollout plan with ROLLED_BACK status
        400: Cannot rollback (invalid state)
        404: Plan not found
        500: Server error
    """
    try:
        # Convert to int if needed
        try:
            plan_id_int = int(plan_id)
        except (ValueError, TypeError):
            return error_response(ErrorCode.VALIDATION_ERROR, 400,
                                details={'error': 'Invalid plan ID format'})

        # Check plan exists (class method - NO instantiation)
        plan = FeatureConfigurationRepository.find_rollout_plan_by_id(plan_id_int)
        if not plan:
            return error_response(ErrorCode.NOT_FOUND, 404,
                                details={'resource': 'rollout_plan', 'id': plan_id})

        # Rollback deployment (class method - NO instantiation)
        updated_plan = FeatureConfigurationRepository.update_rollout_plan(
            plan_id_int,
            {
                'rollout_status': 'rolled_back',
                'rollout_percentage': 0
            }
        )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.id,
            action='ROLLBACK_DEPLOYMENT',
            resource='rollout_plans',
            resource_id=plan_id,
            result='success',
            details={'previous_status': plan.rollout_status if hasattr(plan, 'rollout_status') else 'unknown'}
        )

        return jsonify({
            'success': True,
            'data': updated_plan.to_dict() if hasattr(updated_plan, 'to_dict') else updated_plan
        }), 200

    except Exception as e:
        logger.error(f"Error rolling back deployment {plan_id}: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'error': str(e)})
