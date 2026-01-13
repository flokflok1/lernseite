"""
Direct Chapter Endpoints (under /chapters/:id)

Endpoints:
- GET    /chapters/:id - Get chapter details
- PUT    /chapters/:id - Update chapter
- DELETE /chapters/:id - Delete chapter
- GET    /chapters/:id/lessons - Get chapter lessons
- POST   /chapters/:id/lessons - Create lesson in chapter
"""

from flask import request, jsonify
from pydantic import ValidationError

from app.models.course import ModuleUpdate, LessonCreate
from app.repositories.courses import CourseRepository
from app.repositories.courses.chapters import ChapterRepository
from app.repositories.courses.lessons import LessonRepository
from app.middleware.auth import token_required, get_current_user

# Import blueprint from nested.py and register direct endpoints
from .nested import chapters_bp


@chapters_bp.route('/chapters/<int:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    """
    Get chapter details

    Response:
        200: Chapter details
        404: Chapter not found
    """
    try:
        chapter = ChapterRepository.find_by_id(chapter_id)

        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Chapter not found'
            }), 404

        return jsonify({
            'success': True,
            'chapter': chapter
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get chapter',
            'details': str(e)
        }), 500


@chapters_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
@token_required
def update_chapter(chapter_id):
    """
    Update chapter (creator only)

    Request Body: Partial chapter data to update

    Response:
        200: Chapter updated successfully
        403: Access denied
        404: Chapter not found
    """
    try:
        user = get_current_user()
        chapter = ChapterRepository.find_by_id(chapter_id)

        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Chapter not found'
            }), 404

        # Get course to check permissions
        course = CourseRepository.find_by_id(chapter['course_id'])

        is_creator = user['user_id'] == course['creator_id']
        is_admin = user['role'] in ['admin', 'superadmin']

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json()

        # Validate with Pydantic
        chapter_data = ModuleUpdate(**data)

        # Update chapter
        updated_chapter = ChapterRepository.update(chapter_id, chapter_data.model_dump(exclude_none=True))

        return jsonify({
            'success': True,
            'message': 'Chapter updated successfully',
            'chapter': updated_chapter
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Chapter update failed',
            'details': str(e)
        }), 500


@chapters_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@token_required
def delete_chapter(chapter_id):
    """
    Delete chapter (creator only)

    WARNING: This will cascade delete all lessons in the chapter!

    Response:
        200: Chapter deleted successfully
        403: Access denied
        404: Chapter not found
    """
    try:
        user = get_current_user()
        chapter = ChapterRepository.find_by_id(chapter_id)

        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Chapter not found'
            }), 404

        # Get course to check permissions
        course = CourseRepository.find_by_id(chapter['course_id'])

        is_creator = user['user_id'] == course['creator_id']
        is_admin = user['role'] in ['admin', 'superadmin']

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Delete chapter
        ChapterRepository.delete(chapter_id)

        return jsonify({
            'success': True,
            'message': 'Chapter deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Chapter deletion failed',
            'details': str(e)
        }), 500


@chapters_bp.route('/chapters/<chapter_id>/lessons', methods=['GET'])
def get_chapter_lessons(chapter_id):
    """
    Get all lessons for a chapter

    Response:
        200: List of lessons
        404: Chapter not found
    """
    try:
        chapter = ChapterRepository.find_by_id(chapter_id)

        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Chapter not found'
            }), 404

        lessons = LessonRepository.find_by_chapter(chapter_id)

        return jsonify({
            'success': True,
            'lessons': lessons,
            'total': len(lessons)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get lessons',
            'details': str(e)
        }), 500


@chapters_bp.route('/chapters/<chapter_id>/lessons', methods=['POST'])
@token_required
def create_lesson(chapter_id):
    """
    Create a new lesson in a chapter (creator only)

    Request Body:
        {
            "title": "Was ist Python?",
            "content_type": "video",
            "content_url": "https://...",
            "duration_minutes": 15,
            "is_preview": false
        }

    Response:
        201: Lesson created successfully
        403: Access denied
        404: Chapter not found
    """
    try:
        user = get_current_user()
        chapter = ChapterRepository.find_by_id(chapter_id)

        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Chapter not found'
            }), 404

        # Get course to check permissions
        course = CourseRepository.find_by_id(chapter['course_id'])

        is_creator = user['user_id'] == course['creator_id']
        is_admin = user['role'] in ['admin', 'superadmin']

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json()

        # Validate with Pydantic
        lesson_data = LessonCreate(**data)

        # Add chapter_id
        lesson_dict = lesson_data.model_dump()
        lesson_dict['chapter_id'] = chapter_id

        # Create lesson
        lesson = LessonRepository.create(lesson_dict)

        return jsonify({
            'success': True,
            'message': 'Lesson created successfully',
            'lesson': lesson
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Lesson creation failed',
            'details': str(e)
        }), 500
