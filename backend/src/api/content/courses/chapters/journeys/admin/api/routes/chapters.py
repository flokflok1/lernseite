"""
Admin Chapter Routes (Journey-Based API)

Admin journey for chapter management within courses.
ALL data loaded dynamically from database - NO hardcoded values.

Endpoints:
- GET /api/v1/admin/courses/<course_id>/chapters - List course chapters
- GET /api/v1/admin/chapters/<id> - Get chapter details
- POST /api/v1/admin/courses/<course_id>/chapters - Create chapter
- PUT /api/v1/admin/chapters/<id> - Update chapter
- POST /api/v1/admin/chapters/<id>/publish - Publish chapter
- POST /api/v1/admin/chapters/<id>/unpublish - Unpublish chapter
- DELETE /api/v1/admin/chapters/<id> - Delete chapter
- POST /api/v1/admin/courses/<course_id>/chapters/reorder - Reorder chapters
- PATCH /api/v1/admin/chapters/<id>/content-flags - Update content flags
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
from src.core.auth.permissions import require_auth, require_role
from src.api.content.courses.chapters.application.services.chapter_service import ChapterService
from src.core.utils.validators import Validators, ValidationError


# Create blueprint
admin_chapters_bp = Blueprint('admin_chapters', __name__)


@admin_chapters_bp.route('/api/v1/admin/courses/<course_id>/chapters', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def list_course_chapters(course_id: str):
    """
    List chapters for a course.

    Args:
        course_id: Course UUID

    Query params:
    - published_only: Only published chapters (default: false)

    Returns:
        200: List of chapters
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(course_id)

        published_only = request.args.get('published_only', 'false').lower() == 'true'

        # Get chapters
        chapters = ChapterService.list_course_chapters(
            course_id=course_id,
            published_only=published_only
        )

        # Convert to dict
        chapters_data = [
            {
                'chapter_id': c.chapter_id,
                'course_id': c.course_id,
                'title': c.title,
                'slug': c.slug,
                'description': c.description,
                'order_index': c.order_index,
                'duration_minutes': c.duration_minutes,
                'prerequisite_chapter_id': c.prerequisite_chapter_id,
                'published': c.published,
                'has_video': c.has_video,
                'has_quiz': c.has_quiz,
                'has_exam': c.has_exam,
                'created_at': c.created_at.isoformat() if c.created_at else None,
                'updated_at': c.updated_at.isoformat() if c.updated_at else None
            }
            for c in chapters
        ]

        return jsonify({
            'success': True,
            'data': chapters_data,
            'meta': {
                'course_id': course_id,
                'count': len(chapters_data)
            }
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_UUID',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'LIST_CHAPTERS_ERROR',
                'message': str(e)
            }
        }), 500


@admin_chapters_bp.route('/api/v1/admin/chapters/<chapter_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_chapter(chapter_id: str):
    """
    Get chapter by ID.

    Args:
        chapter_id: Chapter UUID

    Returns:
        200: Chapter data
        404: Chapter not found
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(chapter_id)

        # Get chapter
        chapter = ChapterService.get_chapter_by_id(chapter_id)

        if not chapter:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CHAPTER_NOT_FOUND',
                    'message': f'Chapter {chapter_id} not found'
                }
            }), 404

        # Convert to dict
        chapter_data = {
            'chapter_id': chapter.chapter_id,
            'course_id': chapter.course_id,
            'title': chapter.title,
            'slug': chapter.slug,
            'description': chapter.description,
            'order_index': chapter.order_index,
            'duration_minutes': chapter.duration_minutes,
            'estimated_duration': chapter.estimated_duration,
            'prerequisite_chapter_id': chapter.prerequisite_chapter_id,
            'published': chapter.published,
            'has_video': chapter.has_video,
            'has_quiz': chapter.has_quiz,
            'has_exam': chapter.has_exam,
            'created_at': chapter.created_at.isoformat() if chapter.created_at else None,
            'updated_at': chapter.updated_at.isoformat() if chapter.updated_at else None
        }

        return jsonify({
            'success': True,
            'data': chapter_data
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_UUID',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_CHAPTER_ERROR',
                'message': str(e)
            }
        }), 500


@admin_chapters_bp.route('/api/v1/admin/courses/<course_id>/chapters', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def create_chapter(course_id: str):
    """
    Create new chapter in course.

    Args:
        course_id: Course UUID

    Request body:
    - title: Chapter title (required)
    - slug: URL slug (optional)
    - description: Description (optional)
    - duration_minutes: Duration (optional)
    - order_index: Order (optional, auto-calculated if omitted)
    - prerequisite_chapter_id: Prerequisite (optional)

    Returns:
        201: Created chapter
        400: Validation error
        403: Permission denied
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(course_id)

        data = request.get_json()

        # Validate required fields
        Validators.validate_json_keys(data, ['title'])

        # Get user info
        user_id = request.user_id
        user_role = request.user_role

        # Create chapter
        chapter = ChapterService.create_chapter(
            course_id=course_id,
            title=data['title'],
            user_id=user_id,
            user_role=user_role,
            slug=data.get('slug'),
            description=data.get('description'),
            duration_minutes=data.get('duration_minutes'),
            order_index=data.get('order_index'),
            prerequisite_chapter_id=data.get('prerequisite_chapter_id')
        )

        # Convert to dict
        chapter_data = {
            'chapter_id': chapter.chapter_id,
            'course_id': chapter.course_id,
            'title': chapter.title,
            'slug': chapter.slug,
            'description': chapter.description,
            'order_index': chapter.order_index,
            'duration_minutes': chapter.duration_minutes,
            'prerequisite_chapter_id': chapter.prerequisite_chapter_id,
            'published': chapter.published,
            'created_at': chapter.created_at.isoformat() if chapter.created_at else None
        }

        return jsonify({
            'success': True,
            'data': chapter_data
        }), 201

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': str(e)
            }
        }), 403

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_DATA',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATE_CHAPTER_ERROR',
                'message': str(e)
            }
        }), 500


@admin_chapters_bp.route('/api/v1/admin/chapters/<chapter_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'creator'])
def update_chapter(chapter_id: str):
    """
    Update chapter.

    Args:
        chapter_id: Chapter UUID

    Request body (all optional):
    - title: New title
    - slug: New slug
    - description: New description
    - duration_minutes: New duration
    - order_index: New order
    - prerequisite_chapter_id: New prerequisite

    Returns:
        200: Updated chapter
        403: Permission denied
        404: Chapter not found
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(chapter_id)

        data = request.get_json()

        # Get user info
        user_id = request.user_id
        user_role = request.user_role

        # Update chapter
        chapter = ChapterService.update_chapter(
            chapter_id=chapter_id,
            user_id=user_id,
            user_role=user_role,
            updates=data
        )

        # Convert to dict
        chapter_data = {
            'chapter_id': chapter.chapter_id,
            'course_id': chapter.course_id,
            'title': chapter.title,
            'slug': chapter.slug,
            'description': chapter.description,
            'order_index': chapter.order_index,
            'duration_minutes': chapter.duration_minutes,
            'prerequisite_chapter_id': chapter.prerequisite_chapter_id,
            'published': chapter.published,
            'updated_at': chapter.updated_at.isoformat() if chapter.updated_at else None
        }

        return jsonify({
            'success': True,
            'data': chapter_data
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': str(e)
            }
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'CHAPTER_NOT_FOUND',
                'message': str(e)
            }
        }), 404

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_UUID',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_CHAPTER_ERROR',
                'message': str(e)
            }
        }), 500


@admin_chapters_bp.route('/api/v1/admin/chapters/<chapter_id>/publish', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def publish_chapter(chapter_id: str):
    """
    Publish chapter.

    Args:
        chapter_id: Chapter UUID

    Returns:
        200: Published chapter
        403: Permission denied
        404: Chapter not found
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(chapter_id)

        # Get user info
        user_id = request.user_id
        user_role = request.user_role

        # Publish chapter
        chapter = ChapterService.publish_chapter(
            chapter_id=chapter_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {
                'chapter_id': chapter.chapter_id,
                'title': chapter.title,
                'published': chapter.published
            },
            'message': 'Chapter published successfully'
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': str(e)
            }
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'CHAPTER_NOT_FOUND',
                'message': str(e)
            }
        }), 404

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_UUID',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PUBLISH_CHAPTER_ERROR',
                'message': str(e)
            }
        }), 500


@admin_chapters_bp.route('/api/v1/admin/chapters/<chapter_id>/unpublish', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def unpublish_chapter(chapter_id: str):
    """Unpublish chapter."""
    try:
        Validators.validate_uuid(chapter_id)
        user_id = request.user_id
        user_role = request.user_role

        chapter = ChapterService.unpublish_chapter(
            chapter_id=chapter_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {
                'chapter_id': chapter.chapter_id,
                'title': chapter.title,
                'published': chapter.published
            },
            'message': 'Chapter unpublished successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'CHAPTER_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UNPUBLISH_CHAPTER_ERROR', 'message': str(e)}}), 500


@admin_chapters_bp.route('/api/v1/admin/chapters/<chapter_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_chapter(chapter_id: str):
    """Delete chapter (hard delete - cascade to lessons)."""
    try:
        Validators.validate_uuid(chapter_id)
        user_id = request.user_id
        user_role = request.user_role

        ChapterService.delete_chapter(
            chapter_id=chapter_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'message': 'Chapter deleted successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'CHAPTER_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'DELETE_CHAPTER_ERROR', 'message': str(e)}}), 500


@admin_chapters_bp.route('/api/v1/admin/courses/<course_id>/chapters/reorder', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def reorder_chapters(course_id: str):
    """
    Reorder chapters within a course.

    Request body:
    - chapters: Array of {chapter_id, order_index}
    """
    try:
        Validators.validate_uuid(course_id)
        data = request.get_json()
        Validators.validate_json_keys(data, ['chapters'])

        user_id = request.user_id
        user_role = request.user_role

        success = ChapterService.reorder_chapters(
            course_id=course_id,
            chapter_order=data['chapters'],
            user_id=user_id,
            user_role=user_role
        )

        if success:
            return jsonify({'success': True, 'message': 'Chapters reordered successfully'}), 200
        else:
            return jsonify({'success': False, 'error': {'code': 'REORDER_FAILED', 'message': 'Failed to reorder chapters'}}), 500

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'REORDER_CHAPTERS_ERROR', 'message': str(e)}}), 500


@admin_chapters_bp.route('/api/v1/admin/chapters/<chapter_id>/content-flags', methods=['PATCH'])
@require_auth
@require_role(['admin', 'creator'])
def update_content_flags(chapter_id: str):
    """
    Update chapter content type flags.

    Request body (all optional):
    - has_video: boolean
    - has_quiz: boolean
    - has_exam: boolean
    """
    try:
        Validators.validate_uuid(chapter_id)
        data = request.get_json()

        user_id = request.user_id
        user_role = request.user_role

        chapter = ChapterService.update_content_flags(
            chapter_id=chapter_id,
            user_id=user_id,
            user_role=user_role,
            has_video=data.get('has_video'),
            has_quiz=data.get('has_quiz'),
            has_exam=data.get('has_exam')
        )

        return jsonify({
            'success': True,
            'data': {
                'chapter_id': chapter.chapter_id,
                'has_video': chapter.has_video,
                'has_quiz': chapter.has_quiz,
                'has_exam': chapter.has_exam
            },
            'message': 'Content flags updated successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'CHAPTER_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UPDATE_FLAGS_ERROR', 'message': str(e)}}), 500
