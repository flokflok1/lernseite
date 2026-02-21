"""
Course Editor - Chapter Management

Feature-based chapter management with permission-aware access.
Admin: Full access to all chapters
User: Only access to chapters in own courses

Endpoints:
- GET    /api/v1/course-editor/manual/courses/{course_id}/chapters - List chapters
- POST   /api/v1/course-editor/manual/courses/{course_id}/chapters - Create chapter
- PATCH  /api/v1/course-editor/manual/chapters/{chapter_id} - Update chapter
- DELETE /api/v1/course-editor/manual/chapters/{chapter_id} - Delete chapter
- POST   /api/v1/course-editor/manual/courses/{course_id}/chapters/reorder - Reorder chapters
"""

from flask import request, jsonify, g
import logging

logger = logging.getLogger(__name__)

from app.api.v1.panel.editor.manual import manual_editor_bp
from app.api.v1.panel.editor.shared.permissions import check_course_permission
from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
from app.application.services.system.audit.service import AuditService
from app.api.middleware.auth import get_current_user
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response


@manual_editor_bp.route('/courses/<course_id>/chapters', methods=['GET'])
@check_course_permission('read')
def list_course_chapters(course_id: str):
    """List all chapters for a course."""
    try:
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        chapters = ChapterRepository.find_by_course(course_id)

        return jsonify({'success': True, 'chapters': chapters}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_list_course_chapters: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/courses/<course_id>/chapters', methods=['POST'])
@check_course_permission('write')
def create_chapter(course_id: str):
    """Create a new chapter for a course."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        if not data.get('title'):
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, field='title')

        chapter_data = {
            'course_id': course_id,
            'title': data['title'],
            'description': data.get('description'),
            'duration_minutes': data.get('duration_minutes', 0),
            'has_video': data.get('has_video', False),
            'has_quiz': data.get('has_quiz', False),
            'has_exam': data.get('has_exam', False)
        }

        chapter = ChapterRepository.create(chapter_data)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.chapters.create',
            resource_type='chapter',
            resource_id=str(chapter['chapter_id']),
            details={
                'course_id': course_id,
                'chapter_title': chapter['title'],
                'course_title': course['title']
            },
            severity='info'
        )

        return jsonify({'success': True, 'chapter': chapter}), 201

    except Exception as e:
        logger.error(f"ERROR in admin_create_chapter: {e}")
        return error_response(ErrorCode.CHAPTER_CREATE_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/chapters/<chapter_id>', methods=['PATCH'])
@check_course_permission('write')
def update_chapter(chapter_id: str):
    """Update a chapter."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        existing_chapter = ChapterRepository.find_by_id(chapter_id)
        if not existing_chapter:
            return error_response(ErrorCode.CHAPTER_NOT_FOUND, 404)

        updated_chapter = ChapterRepository.update(chapter_id, data)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.chapters.update',
            resource_type='chapter',
            resource_id=str(chapter_id),
            details={
                'chapter_title': updated_chapter['title'],
                'course_id': updated_chapter['course_id'],
                'changes': data
            },
            severity='info'
        )

        return jsonify({'success': True, 'chapter': updated_chapter}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_update_chapter: {e}")
        return error_response(ErrorCode.CHAPTER_UPDATE_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/chapters/<chapter_id>', methods=['DELETE'])
@check_course_permission('delete')
def delete_chapter(chapter_id: str):
    """Delete a chapter."""
    try:
        current_user = get_current_user()
        data = request.get_json(silent=True) or {}
        reason = data.get('reason', 'Deleted by admin')

        existing_chapter = ChapterRepository.find_by_id(chapter_id)
        if not existing_chapter:
            return error_response(ErrorCode.CHAPTER_NOT_FOUND, 404)

        ChapterRepository.delete(chapter_id)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.chapters.delete',
            resource_type='chapter',
            resource_id=str(chapter_id),
            details={
                'reason': reason,
                'chapter_title': existing_chapter['title'],
                'course_id': existing_chapter['course_id']
            },
            severity='high'
        )

        return jsonify({'success': True, 'message': 'Module deleted successfully'}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_delete_chapter: {e}")
        return error_response(ErrorCode.CHAPTER_DELETE_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/courses/<course_id>/chapters/reorder', methods=['POST'])
@check_course_permission('write')
def reorder_chapters(course_id: str):
    """Reorder chapters in a course."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        chapter_ids = data.get('chapter_ids', [])
        if not chapter_ids or not isinstance(chapter_ids, list):
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'field': 'chapter_ids', 'message': 'must be a non-empty array'})

        chapter_orders = []
        for index, chapter_id in enumerate(chapter_ids, start=1):
            chapter_orders.append({
                'chapter_id': chapter_id,
                'order_index': index
            })

        ChapterRepository.reorder(course_id, chapter_orders)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.chapters.reorder',
            resource_type='course',
            resource_id=str(course_id),
            details={
                'course_title': course['title'],
                'new_order': chapter_ids
            },
            severity='info'
        )

        return jsonify({'success': True, 'message': 'Modules reordered successfully'}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_reorder_chapters: {e}")
        return error_response(ErrorCode.CHAPTER_REORDER_FAILED, 500, details={'details': str(e)})
