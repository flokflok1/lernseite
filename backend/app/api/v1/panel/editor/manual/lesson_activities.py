"""
Course Editor - Lesson Activity Management (Learning Methods per Lesson)

CRUD endpoints for learning method instances assigned to specific lessons.

Endpoints:
- GET    /api/v1/course-editor/manual/lessons/{lesson_id}/activities - List activities
- POST   /api/v1/course-editor/manual/lessons/{lesson_id}/activities - Create activity
- PATCH  /api/v1/course-editor/manual/activities/{method_id} - Update activity
- DELETE /api/v1/course-editor/manual/activities/{method_id} - Delete activity
- POST   /api/v1/course-editor/manual/lessons/{lesson_id}/activities/reorder - Reorder
"""

from flask import request, jsonify, g
import logging

logger = logging.getLogger(__name__)

from app.api.v1.panel.editor.manual import manual_editor_bp
from app.api.v1.panel.editor.shared.permissions import check_course_permission
from app.infrastructure.persistence.repositories.courses.content.lessons import LessonRepository
from app.infrastructure.persistence.repositories.learning_method.execution.instances import LearningMethodInstanceRepository
from app.application.services.system.audit.service import AuditService
from app.api.middleware.auth import get_current_user
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response


@manual_editor_bp.route('/lessons/<lesson_id>/activities', methods=['GET'])
@check_course_permission('read')
def list_lesson_activities(lesson_id: str):
    """List all learning method activities for a lesson."""
    try:
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            return error_response(ErrorCode.LESSON_NOT_FOUND, 404)

        activities = LearningMethodInstanceRepository.find_by_lesson(lesson_id)

        return jsonify({'success': True, 'activities': activities}), 200

    except Exception as e:
        logger.error(f"ERROR in list_lesson_activities: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/lessons/<lesson_id>/activities', methods=['POST'])
@check_course_permission('write')
def create_lesson_activity(lesson_id: str):
    """Create a new learning method activity for a lesson."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            return error_response(ErrorCode.LESSON_NOT_FOUND, 404)

        method_type = data.get('method_type')
        if method_type is None:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, field='method_type')

        title = data.get('title', '').strip()
        if not title:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, field='title')

        instance_data = {
            'chapter_id': lesson['chapter_id'],
            'lesson_id': lesson_id,
            'method_type': int(method_type),
            'title': title,
            'data': data.get('data', {}),
            'published': False
        }

        activity = LearningMethodInstanceRepository.create(instance_data)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='editor.lesson_activity.create',
            resource_type='learning_method_instance',
            resource_id=str(activity['method_id']),
            details={
                'lesson_id': lesson_id,
                'method_type': method_type,
                'title': title
            },
            severity='info'
        )

        return jsonify({'success': True, 'activity': activity}), 201

    except ValueError as e:
        return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'message': str(e)})
    except Exception as e:
        logger.error(f"ERROR in create_lesson_activity: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/activities/<method_id>', methods=['PATCH'])
@check_course_permission('write')
def update_lesson_activity(method_id: str):
    """Update a learning method activity (title, data, difficulty, etc.)."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        existing = LearningMethodInstanceRepository.find_by_id(method_id)
        if not existing:
            return error_response(ErrorCode.RESOURCE_NOT_FOUND, 404)

        allowed = {'title', 'instructions', 'data', 'difficulty', 'duration_minutes', 'published'}
        updates = {k: v for k, v in data.items() if k in allowed}
        if not updates:
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'message': 'No valid fields to update'})

        updated = LearningMethodInstanceRepository.update(method_id, updates)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='editor.lesson_activity.update',
            resource_type='learning_method_instance',
            resource_id=str(method_id),
            details={'updated_fields': list(updates.keys())},
            severity='info'
        )

        return jsonify({'success': True, 'activity': updated}), 200

    except ValueError as e:
        return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'message': str(e)})
    except Exception as e:
        logger.error(f"ERROR in update_lesson_activity: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/activities/<method_id>', methods=['DELETE'])
@check_course_permission('delete')
def delete_lesson_activity(method_id: str):
    """Delete a learning method activity."""
    try:
        current_user = get_current_user()

        existing = LearningMethodInstanceRepository.find_by_id(method_id)
        if not existing:
            return error_response(ErrorCode.RESOURCE_NOT_FOUND, 404)

        LearningMethodInstanceRepository.delete(method_id)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='editor.lesson_activity.delete',
            resource_type='learning_method_instance',
            resource_id=str(method_id),
            details={
                'title': existing.get('title'),
                'method_type': existing.get('method_type')
            },
            severity='high'
        )

        return jsonify({'success': True, 'message': 'Activity deleted'}), 200

    except Exception as e:
        logger.error(f"ERROR in delete_lesson_activity: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/lessons/<lesson_id>/activities/reorder', methods=['POST'])
@check_course_permission('write')
def reorder_lesson_activities(lesson_id: str):
    """Reorder learning method activities in a lesson."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            return error_response(ErrorCode.LESSON_NOT_FOUND, 404)

        method_ids = data.get('method_ids', [])
        if not method_ids or not isinstance(method_ids, list):
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'field': 'method_ids', 'message': 'must be a non-empty array'})

        LearningMethodInstanceRepository.reorder_lesson_activities(lesson_id, method_ids)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='editor.lesson_activity.reorder',
            resource_type='lesson',
            resource_id=str(lesson_id),
            details={'new_order': method_ids},
            severity='info'
        )

        return jsonify({'success': True, 'message': 'Activities reordered'}), 200

    except Exception as e:
        logger.error(f"ERROR in reorder_lesson_activities: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})
