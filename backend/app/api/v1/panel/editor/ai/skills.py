"""
AI Skills Endpoints

REST endpoints for AI skill catalog and execution.
All routes: /api/v1/course-editor/ai/skills/*
"""

from flask import Blueprint, request, g
from typing import Dict, Any, Tuple
import logging

from app.api.middleware.auth import permission_required

logger = logging.getLogger(__name__)

skills_bp = Blueprint('ai_skills', __name__, url_prefix='/skills')


@skills_bp.route('', methods=['GET'])
@permission_required('content.courses:write')
def get_catalog() -> Tuple[Dict[str, Any], int]:
    """Get the full skill catalog."""
    from app.application.services.ai.skill_service import SkillExecutionService

    try:
        category = request.args.get('category')
        if category:
            skills = SkillExecutionService.get_catalog_by_category(category)
        else:
            skills = SkillExecutionService.get_catalog()
        return {'success': True, 'data': skills}, 200

    except Exception as e:
        logger.error(f"Get skill catalog failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to get catalog'}}, 500


@skills_bp.route('/<code>', methods=['GET'])
@permission_required('content.courses:write')
def get_skill(code: str) -> Tuple[Dict[str, Any], int]:
    """Get a single skill definition."""
    from app.application.services.ai.skill_service import SkillExecutionService

    try:
        skill = SkillExecutionService.get_skill_detail(code)
        if not skill:
            return {'success': False, 'error': {'code': 'NOT_FOUND', 'message': f'Skill not found: {code}'}}, 404
        return {'success': True, 'data': skill}, 200

    except Exception as e:
        logger.error(f"Get skill failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to get skill'}}, 500


@skills_bp.route('/execute', methods=['POST'])
@permission_required('content.courses:write')
def execute_skill() -> Tuple[Dict[str, Any], int]:
    """Execute a single skill."""
    from app.application.services.ai.skill_service import SkillExecutionService

    try:
        data = request.get_json() or {}
        skill_code = data.get('skill_code')
        course_id = data.get('course_id')

        if not skill_code or not course_id:
            return {
                'success': False,
                'error': {'code': 'MISSING_PARAMS', 'message': 'skill_code and course_id are required'},
            }, 400

        user_id = g.current_user['user_id']
        result = SkillExecutionService.execute(
            skill_code=skill_code,
            course_id=course_id,
            user_id=user_id,
            target_type=data.get('target_type'),
            target_id=data.get('target_id'),
            parameters=data.get('parameters'),
            prompt_override=data.get('prompt_override'),
        )

        return {'success': True, 'data': result}, 200

    except ValueError as e:
        return {'success': False, 'error': {'code': 'SKILL_ERROR', 'message': str(e)}}, 400
    except Exception as e:
        logger.error(f"Execute skill failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to execute skill'}}, 500


@skills_bp.route('/batch', methods=['POST'])
@permission_required('content.courses:write')
def execute_batch() -> Tuple[Dict[str, Any], int]:
    """Execute multiple skills (batch from plan)."""
    from app.application.services.ai.skill_service import SkillExecutionService

    try:
        data = request.get_json() or {}
        plan_id = data.get('plan_id')
        steps = data.get('steps', [])

        if not plan_id or not steps:
            return {
                'success': False,
                'error': {'code': 'MISSING_PARAMS', 'message': 'plan_id and steps are required'},
            }, 400

        user_id = g.current_user['user_id']
        results = SkillExecutionService.execute_batch(plan_id, steps, user_id)
        return {'success': True, 'data': results}, 200

    except Exception as e:
        logger.error(f"Batch execution failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to execute batch'}}, 500


@skills_bp.route('/history', methods=['GET'])
@permission_required('content.courses:write')
def get_history() -> Tuple[Dict[str, Any], int]:
    """Get generation history for a course."""
    from app.infrastructure.persistence.repositories.ai.generation_log import GenerationLogRepository

    try:
        course_id = request.args.get('course_id')
        if not course_id:
            return {'success': False, 'error': {'code': 'MISSING_COURSE_ID', 'message': 'course_id is required'}}, 400

        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        history = GenerationLogRepository.find_by_course(course_id, limit, offset)
        return {'success': True, 'data': history}, 200

    except Exception as e:
        logger.error(f"Get history failed: {e}")
        return {'success': False, 'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to get history'}}, 500
