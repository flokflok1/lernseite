"""
Course Editor - Lesson Management

Feature-based lesson management with permission-aware access.
Admin: Full access to all lessons
User: Only access to lessons in own courses

Endpoints:
- GET    /api/v1/course-editor/manual/chapters/{chapter_id}/lessons - List lessons
- POST   /api/v1/course-editor/manual/chapters/{chapter_id}/lessons - Create lesson
- PATCH  /api/v1/course-editor/manual/lessons/{lesson_id} - Update lesson
- DELETE /api/v1/course-editor/manual/lessons/{lesson_id} - Delete lesson
- POST   /api/v1/course-editor/manual/chapters/{chapter_id}/lessons/reorder - Reorder lessons
"""

from flask import request, jsonify, g
import logging

logger = logging.getLogger(__name__)

from app.api.v1.panel.editor.manual import manual_editor_bp
from app.api.v1.panel.editor.shared.permissions import check_course_permission
from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository
from app.application.services.system.audit.service import AuditService
from app.api.middleware.auth import get_current_user
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response


@manual_editor_bp.route('/chapters/<chapter_id>/lessons', methods=['GET'])
@check_course_permission('read')
def list_lessons(chapter_id: str):
    """List all lessons for a chapter."""
    try:
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return error_response(ErrorCode.CHAPTER_NOT_FOUND, 404)

        lessons = LessonRepository.find_by_chapter(chapter_id)

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.lessons.list',
            resource_type='chapter',
            resource_id=str(chapter_id),
            details={
                'lesson_count': len(lessons),
                'chapter_title': chapter['title']
            }
        )

        return jsonify({'success': True, 'lessons': lessons}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_list_lessons: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/chapters/<chapter_id>/lessons', methods=['POST'])
@check_course_permission('write')
def create_lesson(chapter_id: str):
    """Create a new lesson for a chapter."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return error_response(ErrorCode.CHAPTER_NOT_FOUND, 404)

        if not data.get('title'):
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, field='title')

        valid_types = ['text', 'video', 'quiz', 'interactive', 'assignment', 'discussion']
        lesson_type = data.get('lesson_type', 'text')
        if lesson_type not in valid_types:
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'field': 'lesson_type', 'message': f'Must be one of: {", ".join(valid_types)}'})

        lesson_data = {
            'chapter_id': chapter_id,
            'title': data['title'],
            'lesson_type': lesson_type,
            'content': data.get('content'),
            'duration_minutes': data.get('duration_minutes', 0),
            'published': data.get('published', False),
            'free_preview': data.get('free_preview', False)
        }

        lesson = LessonRepository.create(lesson_data)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.lessons.create',
            resource_type='lesson',
            resource_id=str(lesson['lesson_id']),
            details={
                'chapter_id': chapter_id,
                'lesson_title': lesson['title'],
                'lesson_type': lesson_type,
                'chapter_title': chapter['title']
            },
            severity='info'
        )

        return jsonify({'success': True, 'lesson': lesson}), 201

    except Exception as e:
        logger.error(f"ERROR in admin_create_lesson: {e}")
        return error_response(ErrorCode.LESSON_CREATE_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/lessons/<lesson_id>', methods=['PATCH'])
@check_course_permission('write')
def update_lesson(lesson_id: str):
    """Update a lesson."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        existing_lesson = LessonRepository.find_by_id(lesson_id)
        if not existing_lesson:
            return error_response(ErrorCode.LESSON_NOT_FOUND, 404)

        if 'lesson_type' in data:
            valid_types = ['text', 'video', 'quiz', 'interactive', 'assignment', 'discussion']
            if data['lesson_type'] not in valid_types:
                return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'field': 'lesson_type', 'message': f'Must be one of: {", ".join(valid_types)}'})

        updated_lesson = LessonRepository.update(lesson_id, data)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.lessons.update',
            resource_type='lesson',
            resource_id=str(lesson_id),
            details={
                'lesson_title': updated_lesson['title'],
                'chapter_id': updated_lesson['chapter_id'],
                'changes': list(data.keys())
            },
            severity='info'
        )

        return jsonify({'success': True, 'lesson': updated_lesson}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_update_lesson: {e}")
        return error_response(ErrorCode.LESSON_UPDATE_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/lessons/<lesson_id>', methods=['DELETE'])
@check_course_permission('delete')
def delete_lesson(lesson_id: str):
    """Delete a lesson."""
    try:
        current_user = get_current_user()
        data = request.get_json(silent=True) or {}
        reason = data.get('reason', 'Deleted by admin')

        existing_lesson = LessonRepository.find_by_id(lesson_id)
        if not existing_lesson:
            return error_response(ErrorCode.LESSON_NOT_FOUND, 404)

        LessonRepository.delete(lesson_id)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.lessons.delete',
            resource_type='lesson',
            resource_id=str(lesson_id),
            details={
                'reason': reason,
                'lesson_title': existing_lesson['title'],
                'chapter_id': existing_lesson['chapter_id']
            },
            severity='high'
        )

        return jsonify({'success': True, 'message': 'Lesson deleted successfully'}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_delete_lesson: {e}")
        return error_response(ErrorCode.LESSON_DELETE_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/chapters/<chapter_id>/lessons/reorder', methods=['POST'])
@check_course_permission('write')
def reorder_lessons(chapter_id: str):
    """Reorder lessons in a chapter."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return error_response(ErrorCode.CHAPTER_NOT_FOUND, 404)

        lesson_ids = data.get('lesson_ids', [])
        if not lesson_ids or not isinstance(lesson_ids, list):
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'field': 'lesson_ids', 'message': 'must be a non-empty array'})

        lesson_orders = []
        for index, lesson_id in enumerate(lesson_ids, start=1):
            lesson_orders.append({
                'lesson_id': lesson_id,
                'order_index': index
            })

        LessonRepository.reorder(chapter_id, lesson_orders)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.lessons.reorder',
            resource_type='chapter',
            resource_id=str(chapter_id),
            details={
                'chapter_title': chapter['title'],
                'new_order': lesson_ids
            },
            severity='info'
        )

        return jsonify({'success': True, 'message': 'Lessons reordered successfully'}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_reorder_lessons: {e}")
        return error_response(ErrorCode.LESSON_REORDER_FAILED, 500, details={'details': str(e)})
