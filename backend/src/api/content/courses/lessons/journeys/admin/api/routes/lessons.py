"""
Admin Lesson Routes (Journey-Based API)

Admin journey for lesson management within chapters.
ALL data loaded dynamically from database - NO hardcoded values.

Endpoints:
- GET /api/v1/admin/chapters/<chapter_id>/lessons - List chapter lessons
- GET /api/v1/admin/lessons/<id> - Get lesson details
- POST /api/v1/admin/chapters/<chapter_id>/lessons - Create lesson
- PUT /api/v1/admin/lessons/<id> - Update lesson metadata
- PATCH /api/v1/admin/lessons/<id>/content - Update lesson content
- POST /api/v1/admin/lessons/<id>/publish - Publish lesson
- POST /api/v1/admin/lessons/<id>/unpublish - Unpublish lesson
- DELETE /api/v1/admin/lessons/<id> - Delete lesson
- POST /api/v1/admin/chapters/<chapter_id>/lessons/reorder - Reorder lessons
- PATCH /api/v1/admin/lessons/<id>/free-preview - Set free preview
- GET /api/v1/admin/lessons/types - Get available lesson types (from DB)
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
from src.core.auth.permissions import require_auth, require_role
from src.api.content.courses.lessons.application.services.lesson_service import LessonService
from src.core.utils.validators import Validators, ValidationError


# Create blueprint
admin_lessons_bp = Blueprint('admin_lessons', __name__)


@admin_lessons_bp.route('/api/v1/admin/chapters/<chapter_id>/lessons', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def list_chapter_lessons(chapter_id: str):
    """List lessons for a chapter."""
    try:
        Validators.validate_uuid(chapter_id)
        published_only = request.args.get('published_only', 'false').lower() == 'true'

        lessons = LessonService.list_chapter_lessons(
            chapter_id=chapter_id,
            published_only=published_only
        )

        lessons_data = [
            {
                'lesson_id': l.lesson_id,
                'chapter_id': l.chapter_id,
                'title': l.title,
                'slug': l.slug,
                'lesson_type': l.lesson_type,
                'duration_minutes': l.duration_minutes,
                'order_index': l.order_index,
                'published': l.published,
                'free_preview': l.free_preview,
                'created_at': l.created_at.isoformat() if l.created_at else None,
                'updated_at': l.updated_at.isoformat() if l.updated_at else None
            }
            for l in lessons
        ]

        return jsonify({
            'success': True,
            'data': lessons_data,
            'meta': {'chapter_id': chapter_id, 'count': len(lessons_data)}
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_LESSONS_ERROR', 'message': str(e)}}), 500


@admin_lessons_bp.route('/api/v1/admin/lessons/<lesson_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_lesson(lesson_id: str):
    """Get lesson by ID with full content."""
    try:
        Validators.validate_uuid(lesson_id)
        lesson = LessonService.get_lesson_by_id(lesson_id)

        if not lesson:
            return jsonify({'success': False, 'error': {'code': 'LESSON_NOT_FOUND', 'message': f'Lesson {lesson_id} not found'}}), 404

        lesson_data = {
            'lesson_id': lesson.lesson_id,
            'chapter_id': lesson.chapter_id,
            'title': lesson.title,
            'slug': lesson.slug,
            'lesson_type': lesson.lesson_type,
            'content': lesson.content,
            'duration_minutes': lesson.duration_minutes,
            'order_index': lesson.order_index,
            'published': lesson.published,
            'free_preview': lesson.free_preview,
            'created_at': lesson.created_at.isoformat() if lesson.created_at else None,
            'updated_at': lesson.updated_at.isoformat() if lesson.updated_at else None
        }

        return jsonify({'success': True, 'data': lesson_data}), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_LESSON_ERROR', 'message': str(e)}}), 500


@admin_lessons_bp.route('/api/v1/admin/chapters/<chapter_id>/lessons', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def create_lesson(chapter_id: str):
    """Create new lesson in chapter."""
    try:
        Validators.validate_uuid(chapter_id)
        data = request.get_json()
        Validators.validate_json_keys(data, ['title', 'lesson_type'])

        user_id = request.user_id
        user_role = request.user_role

        lesson = LessonService.create_lesson(
            chapter_id=chapter_id,
            title=data['title'],
            lesson_type=data['lesson_type'],
            user_id=user_id,
            user_role=user_role,
            slug=data.get('slug'),
            content=data.get('content', {}),
            duration_minutes=data.get('duration_minutes'),
            order_index=data.get('order_index'),
            free_preview=data.get('free_preview', False)
        )

        lesson_data = {
            'lesson_id': lesson.lesson_id,
            'chapter_id': lesson.chapter_id,
            'title': lesson.title,
            'slug': lesson.slug,
            'lesson_type': lesson.lesson_type,
            'order_index': lesson.order_index,
            'published': lesson.published,
            'free_preview': lesson.free_preview,
            'created_at': lesson.created_at.isoformat() if lesson.created_at else None
        }

        return jsonify({'success': True, 'data': lesson_data}), 201

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_DATA', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'CREATE_LESSON_ERROR', 'message': str(e)}}), 500


@admin_lessons_bp.route('/api/v1/admin/lessons/<lesson_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'creator'])
def update_lesson(lesson_id: str):
    """Update lesson metadata (not content)."""
    try:
        Validators.validate_uuid(lesson_id)
        data = request.get_json()

        user_id = request.user_id
        user_role = request.user_role

        lesson = LessonService.update_lesson(
            lesson_id=lesson_id,
            user_id=user_id,
            user_role=user_role,
            updates=data
        )

        lesson_data = {
            'lesson_id': lesson.lesson_id,
            'chapter_id': lesson.chapter_id,
            'title': lesson.title,
            'slug': lesson.slug,
            'lesson_type': lesson.lesson_type,
            'duration_minutes': lesson.duration_minutes,
            'order_index': lesson.order_index,
            'published': lesson.published,
            'free_preview': lesson.free_preview,
            'updated_at': lesson.updated_at.isoformat() if lesson.updated_at else None
        }

        return jsonify({'success': True, 'data': lesson_data}), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'LESSON_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UPDATE_LESSON_ERROR', 'message': str(e)}}), 500


@admin_lessons_bp.route('/api/v1/admin/lessons/<lesson_id>/content', methods=['PATCH'])
@require_auth
@require_role(['admin', 'creator'])
def update_lesson_content(lesson_id: str):
    """Update lesson content (JSONB)."""
    try:
        Validators.validate_uuid(lesson_id)
        data = request.get_json()
        Validators.validate_json_keys(data, ['content'])

        user_id = request.user_id
        user_role = request.user_role

        lesson = LessonService.update_lesson_content(
            lesson_id=lesson_id,
            content=data['content'],
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {
                'lesson_id': lesson.lesson_id,
                'content': lesson.content,
                'updated_at': lesson.updated_at.isoformat() if lesson.updated_at else None
            },
            'message': 'Lesson content updated successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'LESSON_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UPDATE_CONTENT_ERROR', 'message': str(e)}}), 500


@admin_lessons_bp.route('/api/v1/admin/lessons/<lesson_id>/publish', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def publish_lesson(lesson_id: str):
    """Publish lesson."""
    try:
        Validators.validate_uuid(lesson_id)
        user_id = request.user_id
        user_role = request.user_role

        lesson = LessonService.publish_lesson(
            lesson_id=lesson_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {'lesson_id': lesson.lesson_id, 'title': lesson.title, 'published': lesson.published},
            'message': 'Lesson published successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'LESSON_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'PUBLISH_LESSON_ERROR', 'message': str(e)}}), 500


@admin_lessons_bp.route('/api/v1/admin/lessons/<lesson_id>/unpublish', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def unpublish_lesson(lesson_id: str):
    """Unpublish lesson."""
    try:
        Validators.validate_uuid(lesson_id)
        user_id = request.user_id
        user_role = request.user_role

        lesson = LessonService.unpublish_lesson(
            lesson_id=lesson_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {'lesson_id': lesson.lesson_id, 'title': lesson.title, 'published': lesson.published},
            'message': 'Lesson unpublished successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'LESSON_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UNPUBLISH_LESSON_ERROR', 'message': str(e)}}), 500


@admin_lessons_bp.route('/api/v1/admin/lessons/<lesson_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_lesson(lesson_id: str):
    """Delete lesson (hard delete - cascade to completions)."""
    try:
        Validators.validate_uuid(lesson_id)
        user_id = request.user_id
        user_role = request.user_role

        LessonService.delete_lesson(
            lesson_id=lesson_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({'success': True, 'message': 'Lesson deleted successfully'}), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'LESSON_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'DELETE_LESSON_ERROR', 'message': str(e)}}), 500


@admin_lessons_bp.route('/api/v1/admin/chapters/<chapter_id>/lessons/reorder', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def reorder_lessons(chapter_id: str):
    """Reorder lessons within a chapter."""
    try:
        Validators.validate_uuid(chapter_id)
        data = request.get_json()
        Validators.validate_json_keys(data, ['lessons'])

        user_id = request.user_id
        user_role = request.user_role

        success = LessonService.reorder_lessons(
            chapter_id=chapter_id,
            lesson_order=data['lessons'],
            user_id=user_id,
            user_role=user_role
        )

        if success:
            return jsonify({'success': True, 'message': 'Lessons reordered successfully'}), 200
        else:
            return jsonify({'success': False, 'error': {'code': 'REORDER_FAILED', 'message': 'Failed to reorder lessons'}}), 500

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'REORDER_LESSONS_ERROR', 'message': str(e)}}), 500


@admin_lessons_bp.route('/api/v1/admin/lessons/<lesson_id>/free-preview', methods=['PATCH'])
@require_auth
@require_role(['admin', 'creator'])
def set_free_preview(lesson_id: str):
    """Set lesson free preview status."""
    try:
        Validators.validate_uuid(lesson_id)
        data = request.get_json()
        Validators.validate_json_keys(data, ['free_preview'])

        user_id = request.user_id
        user_role = request.user_role

        lesson = LessonService.set_free_preview(
            lesson_id=lesson_id,
            is_free=data['free_preview'],
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {'lesson_id': lesson.lesson_id, 'free_preview': lesson.free_preview},
            'message': 'Free preview status updated successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'LESSON_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'SET_FREE_PREVIEW_ERROR', 'message': str(e)}}), 500


@admin_lessons_bp.route('/api/v1/admin/lessons/types', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_lesson_types():
    """
    Get available lesson types from database.

    Returns valid lesson types loaded dynamically from DB constraint.
    NO hardcoded lesson type lists.
    """
    try:
        lesson_types = LessonService.get_available_lesson_types()

        return jsonify({
            'success': True,
            'data': lesson_types,
            'meta': {'count': len(lesson_types)}
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_LESSON_TYPES_ERROR', 'message': str(e)}}), 500
