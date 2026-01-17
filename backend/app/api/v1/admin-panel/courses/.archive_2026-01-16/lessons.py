"""
Admin Lesson Management API

Endpoints:
- GET    /api/v1/admin/chapters/{chapter_id}/lessons - List lessons
- POST   /api/v1/admin/chapters/{chapter_id}/lessons - Create lesson
- PATCH  /api/v1/admin/lessons/{lesson_id} - Update lesson
- DELETE /api/v1/admin/lessons/{lesson_id} - Delete lesson
- POST   /api/v1/admin/chapters/{chapter_id}/lessons/reorder - Reorder lessons
"""

from flask import request, jsonify, g
import logging

logger = logging.getLogger(__name__)

from app.api.v1 import api_v1
from app.repositories.courses.chapters import ChapterRepository
from app.repositories.courses.lessons import LessonRepository
from app.services.audit_service import AuditService
from app.middleware.auth import get_current_user
from app.security.permissions import require_permission, Permissions


@api_v1.route('/admin/chapters/<chapter_id>/lessons', methods=['GET'])
@require_permission(Permissions.ADMIN_LESSON_READ)
def admin_list_lessons(chapter_id: str):
    """List all lessons for a chapter."""
    try:
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({'success': False, 'error': 'Module not found'}), 404

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
        return jsonify({'success': False, 'error': 'Failed to load lessons', 'details': str(e)}), 500


@api_v1.route('/admin/chapters/<chapter_id>/lessons', methods=['POST'])
@require_permission(Permissions.ADMIN_LESSON_WRITE)
def admin_create_lesson(chapter_id: str):
    """Create a new lesson for a chapter."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({'success': False, 'error': 'Module not found'}), 404

        if not data.get('title'):
            return jsonify({'success': False, 'error': 'Title is required'}), 400

        valid_types = ['text', 'video', 'quiz', 'interactive', 'assignment', 'discussion']
        lesson_type = data.get('lesson_type', 'text')
        if lesson_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid lesson_type. Must be one of: {", ".join(valid_types)}'
            }), 400

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
        return jsonify({'success': False, 'error': 'Failed to create lesson', 'details': str(e)}), 500


@api_v1.route('/admin/lessons/<lesson_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_LESSON_WRITE)
def admin_update_lesson(lesson_id: str):
    """Update a lesson."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        existing_lesson = LessonRepository.find_by_id(lesson_id)
        if not existing_lesson:
            return jsonify({'success': False, 'error': 'Lesson not found'}), 404

        if 'lesson_type' in data:
            valid_types = ['text', 'video', 'quiz', 'interactive', 'assignment', 'discussion']
            if data['lesson_type'] not in valid_types:
                return jsonify({
                    'success': False,
                    'error': f'Invalid lesson_type. Must be one of: {", ".join(valid_types)}'
                }), 400

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
        return jsonify({'success': False, 'error': 'Failed to update lesson', 'details': str(e)}), 500


@api_v1.route('/admin/lessons/<lesson_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_LESSON_DELETE)
def admin_delete_lesson(lesson_id: str):
    """Delete a lesson."""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        reason = data.get('reason', 'Deleted by admin')

        existing_lesson = LessonRepository.find_by_id(lesson_id)
        if not existing_lesson:
            return jsonify({'success': False, 'error': 'Lesson not found'}), 404

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
        return jsonify({'success': False, 'error': 'Failed to delete lesson', 'details': str(e)}), 500


@api_v1.route('/admin/chapters/<chapter_id>/lessons/reorder', methods=['POST'])
@require_permission(Permissions.ADMIN_LESSON_WRITE)
def admin_reorder_lessons(chapter_id: str):
    """Reorder lessons in a chapter."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({'success': False, 'error': 'Module not found'}), 404

        lesson_ids = data.get('lesson_ids', [])
        if not lesson_ids or not isinstance(lesson_ids, list):
            return jsonify({'success': False, 'error': 'lesson_ids must be a non-empty array'}), 400

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
        return jsonify({'success': False, 'error': 'Failed to reorder lessons', 'details': str(e)}), 500
