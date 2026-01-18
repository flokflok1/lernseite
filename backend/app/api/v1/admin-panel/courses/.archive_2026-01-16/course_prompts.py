"""
Admin Course Prompts API

Endpoints:
- GET    /api/v1/admin/courses/{course_id}/prompts - List course prompts
- GET    /api/v1/admin/courses/{course_id}/prompts/{scope} - Get prompt by scope
- PUT    /api/v1/admin/courses/{course_id}/prompts/{scope} - Upsert prompt
- DELETE /api/v1/admin/courses/{course_id}/prompts/{scope} - Delete prompt
- POST   /api/v1/admin/courses/{course_id}/prompts/reset - Bulk reset prompts
- POST   /api/v1/admin/courses/{course_id}/prompts/resolve - Resolve prompt
"""

from flask import request, jsonify
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

from app.api.v1 import api_v1
from app.domain.models.course_prompt import (
    CoursePromptResponse,
    CoursePromptUpdateRequest,
    CoursePromptResolveRequest,
    CoursePromptResolveResponse,
    BulkResetRequest
)
from app.repositories.courses import CourseRepository
from app.repositories.course_prompt import CoursePromptRepository
from app.services.audit_service import AuditService
from app.services.prompt_resolver import PromptResolver
from app.middleware.auth import get_current_user
from app.security.permissions import require_permission, Permissions


@api_v1.route('/admin/courses/<course_id>/prompts', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_list_course_prompts(course_id: str):
    """List all custom prompts for a specific course."""
    try:
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

        prompts = CoursePromptRepository.find_by_course(
            course_id=course_id,
            include_inactive=include_inactive
        )

        prompt_responses = [
            CoursePromptResponse(**prompt).model_dump(mode='json')
            for prompt in prompts
        ]

        return jsonify({'success': True, 'prompts': prompt_responses}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_list_course_prompts: {e}")
        return jsonify({'success': False, 'error': 'Failed to list course prompts', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>/prompts/<scope>', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_course_prompt(course_id: str, scope: str):
    """Get a specific prompt for a course and scope."""
    try:
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        language = request.args.get('language', None)

        course_prompt = CoursePromptRepository.find_by_course_and_scope(
            course_id=course_id,
            scope=scope,
            language=language
        )

        if course_prompt:
            prompt_response = CoursePromptResponse(**course_prompt).model_dump(mode='json')
            return jsonify({
                'success': True,
                'prompt': prompt_response,
                'source': 'course_specific'
            }), 200
        else:
            resolved = PromptResolver.resolve(
                course_id=course_id,
                scope=scope,
                language=language
            )
            return jsonify({
                'success': True,
                'prompt': None,
                'resolved': resolved,
                'source': resolved['source']
            }), 200

    except Exception as e:
        logger.error(f"ERROR in admin_get_course_prompt: {e}")
        return jsonify({'success': False, 'error': 'Failed to get course prompt', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>/prompts/<scope>', methods=['PUT'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_upsert_course_prompt(course_id: str, scope: str):
    """Create or update a course-specific prompt (UPSERT)."""
    try:
        current_user = get_current_user()

        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        try:
            update_request = CoursePromptUpdateRequest(**data)
        except ValidationError as ve:
            return jsonify({'success': False, 'error': 'Validation failed', 'details': ve.errors()}), 400

        existing_prompt = CoursePromptRepository.find_by_course_and_scope(
            course_id=course_id,
            scope=scope,
            language=data.get('language')
        )

        prompt = CoursePromptRepository.upsert(
            course_id=course_id,
            scope=scope,
            language=data.get('language'),
            prompt_system=data.get('prompt_system'),
            prompt_user_template=data.get('prompt_user_template'),
            metadata=data.get('metadata', {}),
            is_active=data.get('is_active', True),
            created_by=current_user['user_id']
        )

        if not prompt:
            return jsonify({'success': False, 'error': 'Failed to create/update prompt'}), 500

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_prompts.upsert',
            resource_type='course_prompt',
            resource_id=prompt['course_prompt_id'],
            details={
                'course_id': course_id,
                'scope': scope,
                'language': data.get('language'),
                'created': existing_prompt is None
            },
            severity='medium'
        )

        prompt_response = CoursePromptResponse(**prompt).model_dump(mode='json')

        return jsonify({
            'success': True,
            'prompt': prompt_response,
            'created': existing_prompt is None
        }), 200

    except Exception as e:
        logger.error(f"ERROR in admin_upsert_course_prompt: {e}")
        return jsonify({'success': False, 'error': 'Failed to upsert course prompt', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>/prompts/<scope>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_delete_course_prompt(course_id: str, scope: str):
    """Delete a course-specific prompt (reset to global default)."""
    try:
        current_user = get_current_user()

        language = request.args.get('language', None)

        existing_prompt = CoursePromptRepository.find_by_course_and_scope(
            course_id=course_id,
            scope=scope,
            language=language
        )

        if not existing_prompt:
            return jsonify({
                'success': False,
                'error': 'Course prompt not found (already using global default)'
            }), 404

        deleted = CoursePromptRepository.delete_by_course_and_scope(
            course_id=course_id,
            scope=scope,
            language=language
        )

        if not deleted:
            return jsonify({'success': False, 'error': 'Failed to delete prompt'}), 500

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_prompts.delete',
            resource_type='course_prompt',
            resource_id=existing_prompt['course_prompt_id'],
            details={
                'course_id': course_id,
                'scope': scope,
                'language': language
            },
            severity='medium'
        )

        return jsonify({'success': True, 'message': 'Prompt reset to global default'}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_delete_course_prompt: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete course prompt', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>/prompts/reset', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_bulk_reset_course_prompts(course_id: str):
    """Bulk reset course prompts to global defaults."""
    try:
        current_user = get_current_user()

        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        data = request.get_json() or {}

        try:
            reset_request = BulkResetRequest(**data)
        except ValidationError as ve:
            return jsonify({'success': False, 'error': 'Validation failed', 'details': ve.errors()}), 400

        deleted_count = CoursePromptRepository.bulk_reset_by_course(
            course_id=course_id,
            scopes=reset_request.scopes
        )

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_prompts.bulk_reset',
            resource_type='course',
            resource_id=course_id,
            details={
                'scopes': reset_request.scopes,
                'deleted_count': deleted_count
            },
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': f'{deleted_count} prompt(s) reset to global defaults'
        }), 200

    except Exception as e:
        logger.error(f"ERROR in admin_bulk_reset_course_prompts: {e}")
        return jsonify({'success': False, 'error': 'Failed to reset course prompts', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>/prompts/resolve', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_resolve_course_prompt(course_id: str):
    """Resolve a prompt for a specific course and scope (for testing/preview)."""
    try:
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        try:
            resolve_request = CoursePromptResolveRequest(
                course_id=course_id,
                **data
            )
        except ValidationError as ve:
            return jsonify({'success': False, 'error': 'Validation failed', 'details': ve.errors()}), 400

        resolved = PromptResolver.resolve(
            course_id=course_id,
            scope=resolve_request.scope.value,
            language=resolve_request.language
        )

        resolve_response = CoursePromptResolveResponse(**resolved).model_dump(mode='json')

        return jsonify({'success': True, 'resolved': resolve_response}), 200

    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        logger.error(f"ERROR in admin_resolve_course_prompt: {e}")
        return jsonify({'success': False, 'error': 'Failed to resolve course prompt', 'details': str(e)}), 500
