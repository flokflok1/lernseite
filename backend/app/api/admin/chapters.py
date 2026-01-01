"""
Admin Chapter Management API

Endpoints:
- GET    /api/v1/admin/courses/{course_id}/chapters - List chapters
- POST   /api/v1/admin/courses/{course_id}/chapters - Create chapter
- PATCH  /api/v1/admin/chapters/{chapter_id} - Update chapter
- DELETE /api/v1/admin/chapters/{chapter_id} - Delete chapter
- POST   /api/v1/admin/courses/{course_id}/chapters/reorder - Reorder chapters
"""

from flask import request, jsonify, g
import logging

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.repositories.course_repository import CourseRepository
from app.repositories.chapter_repository import ChapterRepository
from app.services.audit_service import AuditService
from app.middleware.auth import get_current_user
from app.security.permissions import require_permission, Permissions


@api_v1.route('/admin/courses/<course_id>/chapters', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_list_course_chapters(course_id: str):
    """List all chapters for a course."""
    try:
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        chapters = ChapterRepository.find_by_course(course_id)

        return jsonify({'success': True, 'chapters': chapters}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_list_course_chapters: {e}")
        return jsonify({'success': False, 'error': 'Failed to load chapters', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>/chapters', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_create_chapter(course_id: str):
    """Create a new chapter for a course."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        if not data.get('title'):
            return jsonify({'success': False, 'error': 'Title is required'}), 400

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
        return jsonify({'success': False, 'error': 'Failed to create chapter', 'details': str(e)}), 500


@api_v1.route('/admin/chapters/<chapter_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_update_chapter(chapter_id: str):
    """Update a chapter."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        existing_chapter = ChapterRepository.find_by_id(chapter_id)
        if not existing_chapter:
            return jsonify({'success': False, 'error': 'Module not found'}), 404

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
        return jsonify({'success': False, 'error': 'Failed to update chapter', 'details': str(e)}), 500


@api_v1.route('/admin/chapters/<chapter_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_DELETE)
def admin_delete_chapter(chapter_id: str):
    """Delete a chapter."""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        reason = data.get('reason', 'Deleted by admin')

        existing_chapter = ChapterRepository.find_by_id(chapter_id)
        if not existing_chapter:
            return jsonify({'success': False, 'error': 'Module not found'}), 404

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
        return jsonify({'success': False, 'error': 'Failed to delete chapter', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>/chapters/reorder', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_reorder_chapters(course_id: str):
    """Reorder chapters in a course."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        chapter_ids = data.get('chapter_ids', [])
        if not chapter_ids or not isinstance(chapter_ids, list):
            return jsonify({'success': False, 'error': 'chapter_ids must be a non-empty array'}), 400

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
        return jsonify({'success': False, 'error': 'Failed to reorder chapters', 'details': str(e)}), 500
