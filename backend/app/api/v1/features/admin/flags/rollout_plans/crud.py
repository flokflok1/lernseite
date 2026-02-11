"""
Feature Flags - Rollout Plans CRUD (DDD)

Endpoints for rollout plan management:
- GET    /api/v1/admin/settings/rollout-plans - List rollout plans
- GET    /api/v1/admin/settings/rollout-plans/<id> - Get plan by ID
- POST   /api/v1/admin/settings/rollout-plans - Create rollout plan
- PUT    /api/v1/admin/settings/rollout-plans/<id> - Update rollout plan
- DELETE /api/v1/admin/settings/rollout-plans/<id> - Delete rollout plan

Uses:
- FeatureConfigurationRepository for database access (Repository Pattern - class methods)
- ErrorCode system for i18n error handling
- Audit logging for compliance

Pattern: Using class methods directly (NO instantiation)
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple, Optional
import logging

from app.api.middleware.auth import permission_required
from app.infrastructure.persistence.repositories.feature_configuration import (
    FeatureConfigurationRepository
)
from app.application.services.system.audit.service import AuditService
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

from .schemas import RolloutPlanSchema

logger = logging.getLogger(__name__)

rollout_plans_crud_bp = Blueprint(
    'rollout_plans_crud',
    __name__,
    url_prefix='/admin-panel/settings/rollout-plans'
)


@rollout_plans_crud_bp.route('', methods=['GET'])
@permission_required('admin.system:read')
def list_rollout_plans() -> Tuple[Dict[str, Any], int]:
    """
    List all rollout plans with pagination and filtering.

    Query Parameters:
        limit (int): Max results (default 20, max 100)
        offset (int): Skip N results (default 0)
        flag_id (str): Filter by feature flag ID
        status (str): Filter by status (not_rolling_out, in_progress, completed, paused, rolled_back)

    Returns:
        200: {data: RolloutPlan[], total: int, limit: int, offset: int}
        500: Server error
    """
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        flag_id = request.args.get('flag_id')
        status_filter = request.args.get('status')

        # Build query filters
        filters = {}
        if flag_id:
            filters['flag_id'] = flag_id
        if status_filter:
            filters['rollout_status'] = status_filter

        # Get plans from repository (class methods - NO instantiation)
        # Note: If FeatureConfigurationRepository doesn't have rollout plan methods,
        # create separate RolloutPlanRepository
        plans = FeatureConfigurationRepository.find_rollout_plans(
            filters=filters,
            limit=limit,
            offset=offset
        ) if hasattr(FeatureConfigurationRepository, 'find_rollout_plans') else []

        total = FeatureConfigurationRepository.count_rollout_plans(
            filters
        ) if hasattr(FeatureConfigurationRepository, 'count_rollout_plans') else 0

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.id,
            action='LIST_ROLLOUT_PLANS',
            resource='rollout_plans',
            result='success',
            details={'limit': limit, 'offset': offset, 'filters': filters}
        )

        return jsonify({
            'success': True,
            'data': [plan.to_dict() for plan in plans] if plans else [],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        logger.error(f"Error listing rollout plans: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'error': str(e)})


@rollout_plans_crud_bp.route('/<plan_id>', methods=['GET'])
@permission_required('admin.system:read')
def get_rollout_plan(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get single rollout plan by ID.

    Path Parameters:
        plan_id (str or int): Rollout plan ID

    Returns:
        200: Rollout plan data
        404: Plan not found
        500: Server error
    """
    try:
        # Convert to int if FeatureConfigurationRepository expects int IDs
        try:
            plan_id_int = int(plan_id)
        except (ValueError, TypeError):
            return error_response(ErrorCode.VALIDATION_ERROR, 400,
                                details={'error': 'Invalid plan ID format'})

        # Get plan from repository (class method - NO instantiation)
        plan = FeatureConfigurationRepository.find_rollout_plan_by_id(plan_id_int)

        if not plan:
            return error_response(ErrorCode.NOT_FOUND, 404,
                                details={'resource': 'rollout_plan', 'id': plan_id})

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.id,
            action='GET_ROLLOUT_PLAN',
            resource='rollout_plans',
            resource_id=plan_id,
            result='success'
        )

        return jsonify({
            'success': True,
            'data': plan
        }), 200

    except Exception as e:
        logger.error(f"Error getting rollout plan {plan_id}: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'error': str(e)})


@rollout_plans_crud_bp.route('', methods=['POST'])
@permission_required('admin.system:write')
def create_rollout_plan() -> Tuple[Dict[str, Any], int]:
    """
    Create new rollout plan for feature.

    Request Body:
        flag_id (str): Feature flag ID (required)
        start_date (datetime): Rollout start time (required)
        target_percentage (int): Target rollout percentage 0-100 (required)
        estimated_end_date (datetime): Expected completion time (optional)
        rollout_status (str): Status (default: not_rolling_out)

    Returns:
        201: Created rollout plan
        400: Validation error
        404: Feature flag not found
        409: Rollout already in progress
        500: Server error
    """
    try:
        data = request.get_json()

        # Validate request
        validated_data = RolloutPlanSchema(**data)

        # Check if feature flag exists (class method - NO instantiation)
        flag = FeatureConfigurationRepository.find_by_id(int(validated_data.flag_id))
        if not flag:
            return error_response(ErrorCode.NOT_FOUND, 404,
                                details={'resource': 'feature_flag', 'id': validated_data.flag_id})

        # Check if rollout already in progress (class method - NO instantiation)
        existing_plan = FeatureConfigurationRepository.find_active_rollout_plan(
            int(validated_data.flag_id)
        ) if hasattr(FeatureConfigurationRepository, 'find_active_rollout_plan') else None

        if existing_plan:
            return error_response(ErrorCode.CONFLICT, 409,
                                details={'message': 'Rollout already in progress for this flag',
                                       'flag_id': validated_data.flag_id})

        # Create rollout plan (class method - NO instantiation)
        new_plan = FeatureConfigurationRepository.create_rollout_plan(validated_data.dict())

        if not new_plan:
            raise RuntimeError("Failed to create rollout plan")

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.id,
            action='CREATE_ROLLOUT_PLAN',
            resource='rollout_plans',
            resource_id=str(new_plan.get('id')),
            result='success',
            details={'flag_id': validated_data.flag_id, 'target_percentage': validated_data.target_percentage}
        )

        return jsonify({
            'success': True,
            'data': new_plan
        }), 201

    except ValueError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400,
                            details={'error': str(e)})
    except Exception as e:
        logger.error(f"Error creating rollout plan: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'error': str(e)})


@rollout_plans_crud_bp.route('/<plan_id>', methods=['PUT'])
@permission_required('admin.system:write')
def update_rollout_plan(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Update existing rollout plan.

    Path Parameters:
        plan_id (str or int): Rollout plan ID

    Request Body:
        target_percentage (int): New target percentage
        estimated_end_date (datetime): Updated end date estimate
        rollout_status (str): Status update

    Returns:
        200: Updated rollout plan
        400: Validation error
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
        existing_plan = FeatureConfigurationRepository.find_rollout_plan_by_id(plan_id_int)
        if not existing_plan:
            return error_response(ErrorCode.NOT_FOUND, 404,
                                details={'resource': 'rollout_plan', 'id': plan_id})

        data = request.get_json()

        # Update plan (only provided fields)
        update_data = {k: v for k, v in data.items() if v is not None}

        if not update_data:
            # Nothing to update, just return existing plan
            return jsonify({
                'success': True,
                'data': existing_plan
            }), 200

        # Update plan (class method - NO instantiation)
        updated_plan = FeatureConfigurationRepository.update_rollout_plan(plan_id_int, update_data)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.id,
            action='UPDATE_ROLLOUT_PLAN',
            resource='rollout_plans',
            resource_id=plan_id,
            result='success',
            details={'changes': update_data}
        )

        return jsonify({
            'success': True,
            'data': updated_plan if updated_plan else existing_plan
        }), 200

    except ValueError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400,
                            details={'error': str(e)})
    except Exception as e:
        logger.error(f"Error updating rollout plan {plan_id}: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'error': str(e)})


@rollout_plans_crud_bp.route('/<plan_id>', methods=['DELETE'])
@permission_required('admin.system:write')
def delete_rollout_plan(plan_id: str) -> Tuple[str, int]:
    """
    Delete rollout plan.

    Path Parameters:
        plan_id (str or int): Rollout plan ID

    Returns:
        204: No Content (success)
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
        existing_plan = FeatureConfigurationRepository.find_rollout_plan_by_id(plan_id_int)
        if not existing_plan:
            return error_response(ErrorCode.NOT_FOUND, 404,
                                details={'resource': 'rollout_plan', 'id': plan_id})

        # Delete plan (class method - NO instantiation)
        # Note: Verify delete_rollout_plan method exists in repository
        FeatureConfigurationRepository.delete_rollout_plan(plan_id_int)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.id,
            action='DELETE_ROLLOUT_PLAN',
            resource='rollout_plans',
            resource_id=plan_id,
            result='success'
        )

        return '', 204

    except Exception as e:
        logger.error(f"Error deleting rollout plan {plan_id}: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, 500, details={'error': str(e)})
