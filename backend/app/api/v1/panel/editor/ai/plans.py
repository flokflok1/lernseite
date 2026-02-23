"""
AI Content Plans Endpoints

REST endpoints for managing AI-generated content plans.
All routes: /api/v1/course-editor/ai/plans/*
"""

from flask import Blueprint, request, g
from typing import Dict, Any, Tuple
import logging

from app.api.middleware.auth import permission_required

logger = logging.getLogger(__name__)

plans_bp = Blueprint('ai_plans', __name__, url_prefix='/plans')


@plans_bp.route('', methods=['POST'])
@permission_required('admin.system:read')
def create_plan() -> Tuple[Dict[str, Any], int]:
    """Create a new content plan (manual or from file)."""
    from app.application.services.ai.plan_service import PlanService

    try:
        data = request.get_json() or {}
        course_id = data.get('course_id')
        if not course_id:
            return {'success': False, 'error': {'code': 'MISSING_COURSE_ID', 'message': 'course_id is required'}}, 400

        user_id = g.get('user_id', 'system')
        source = data.get('source')

        if source == 'file':
            file_id = data.get('file_id')
            if not file_id:
                return {'success': False, 'error': {'code': 'MISSING_FILE_ID', 'message': 'file_id is required'}}, 400
            plan = PlanService.create_plan_from_file(course_id, file_id, user_id)
        else:
            plan = PlanService.create_plan(
                course_id=course_id,
                user_id=user_id,
                scope=data.get('scope', 'course'),
                scope_id=data.get('scope_id'),
            )

        return {'success': True, 'data': plan}, 201

    except ValueError as e:
        return {'success': False, 'error': {'code': 'PLAN_ERROR', 'message': str(e)}}, 400
    except Exception as e:
        logger.error(f"Create plan failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to create plan'}}, 500


@plans_bp.route('', methods=['GET'])
@permission_required('admin.system:read')
def list_plans() -> Tuple[Dict[str, Any], int]:
    """List plans for a course."""
    from app.application.services.ai.plan_service import PlanService

    try:
        course_id = request.args.get('course_id')
        if not course_id:
            return {'success': False, 'error': {'code': 'MISSING_COURSE_ID', 'message': 'course_id is required'}}, 400

        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        plans = PlanService.list_plans(course_id, limit, offset)
        return {'success': True, 'data': plans}, 200

    except Exception as e:
        logger.error(f"List plans failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to list plans'}}, 500


@plans_bp.route('/<plan_id>', methods=['GET'])
@permission_required('admin.system:read')
def get_plan(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """Get a specific plan."""
    from app.application.services.ai.plan_service import PlanService

    try:
        plan = PlanService.get_plan(plan_id)
        if not plan:
            return {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Plan not found'}}, 404
        return {'success': True, 'data': plan}, 200

    except Exception as e:
        logger.error(f"Get plan failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to get plan'}}, 500


@plans_bp.route('/<plan_id>', methods=['PATCH'])
@permission_required('admin.system:read')
def update_plan(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """Update plan data (reorder steps, change parameters)."""
    from app.application.services.ai.plan_service import PlanService

    try:
        data = request.get_json() or {}
        plan_data = data.get('plan_data')
        if not plan_data:
            return {'success': False, 'error': {'code': 'MISSING_DATA', 'message': 'plan_data is required'}}, 400

        plan = PlanService.update_plan(plan_id, plan_data)
        if not plan:
            return {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Plan not found'}}, 404
        return {'success': True, 'data': plan}, 200

    except Exception as e:
        logger.error(f"Update plan failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to update plan'}}, 500


@plans_bp.route('/<plan_id>/approve', methods=['POST'])
@permission_required('admin.system:read')
def approve_plan(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """Approve a plan for execution."""
    from app.application.services.ai.plan_service import PlanService

    try:
        plan = PlanService.approve_plan(plan_id)
        if not plan:
            return {'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Plan not found'}}, 404
        return {'success': True, 'data': plan}, 200

    except Exception as e:
        logger.error(f"Approve plan failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to approve plan'}}, 500


@plans_bp.route('/<plan_id>/execute', methods=['POST'])
@permission_required('admin.system:read')
def execute_plan(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """Execute an approved plan."""
    from app.application.services.ai.plan_service import PlanService

    try:
        user_id = g.get('user_id', 'system')
        result = PlanService.execute_plan(plan_id, user_id)
        return {'success': True, 'data': result}, 200

    except ValueError as e:
        return {'success': False, 'error': {'code': 'PLAN_ERROR', 'message': str(e)}}, 400
    except Exception as e:
        logger.error(f"Execute plan failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to execute plan'}}, 500
