"""
Nested Chapter Endpoints (under /courses/:course_id/chapters)

Endpoints:
- GET    /courses/:course_id/chapters - Get all chapters for a course
- POST   /courses/:course_id/chapters - Create chapter in course
- GET    /courses/:course_id/chapters/:chapter_id - Get specific chapter
- GET    /courses/:course_id/chapters/:chapter_id/progress - Get chapter progress
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.course import ModuleCreate
from app.repositories.courses import CourseRepository
from app.repositories.courses.chapters import ChapterRepository
from app.repositories.courses.lessons import LessonRepository
from app.middleware.auth import token_required, get_current_user

# Blueprint for this module - no url_prefix since we have mixed routes
chapters_bp = Blueprint(
    'chapters_management',
    __name__
)


@chapters_bp.route('/courses/<course_id>/chapters', methods=['GET'])
def get_course_chapters(course_id):
    """
    Get all chapters for a course

    Query Parameters:
        include_lessons: Include lessons in each chapter (default: true)

    Response:
        200: List of chapters with lessons
        404: Course not found
    """
    try:
        course = CourseRepository.find_by_id(course_id)

        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        chapters = ChapterRepository.find_by_course(course_id)

        # Include lessons by default for frontend player navigation
        include_lessons = request.args.get('include_lessons', 'true').lower() != 'false'

        if include_lessons:
            for chapter in chapters:
                lessons = LessonRepository.find_by_chapter(chapter['chapter_id'])
                chapter['lessons'] = lessons

        return jsonify({
            'success': True,
            'chapters': chapters,
            'total': len(chapters)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get chapters',
            'details': str(e)
        }), 500


@chapters_bp.route('/courses/<course_id>/chapters', methods=['POST'])
@token_required
def create_chapter(course_id):
    """
    Create a new chapter in a course (creator only)

    Request Body:
        {
            "title": "Kapitel 1: Einführung",
            "description": "Grundlagen und erste Schritte",
            "duration_minutes": 120,
            "order_index": 1
        }

    Response:
        201: Chapter created successfully
        403: Access denied
        404: Course not found
    """
    try:
        user = get_current_user()
        course = CourseRepository.find_by_id(course_id)

        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Check permissions
        is_creator = user['user_id'] == course['creator_id']
        is_admin = user['role'] in ['admin', 'superadmin']

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json()

        # Validate with Pydantic
        chapter_data = ModuleCreate(**data)

        # Add course_id
        chapter_dict = chapter_data.model_dump()
        chapter_dict['course_id'] = course_id

        # Create chapter
        chapter = ChapterRepository.create(chapter_dict)

        return jsonify({
            'success': True,
            'message': 'Chapter created successfully',
            'chapter': chapter
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
            'error': 'Chapter creation failed',
            'details': str(e)
        }), 500


@chapters_bp.route('/courses/<course_id>/chapters/<chapter_id>', methods=['GET'])
@token_required
def get_course_chapter(course_id, chapter_id):
    """
    Get a specific chapter within a course context

    Response:
        200: Chapter details with lessons
        404: Chapter or course not found
    """
    try:
        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get chapter
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Chapter not found'
            }), 404

        # Verify chapter belongs to course
        if str(chapter.get('course_id')) != str(course_id):
            return jsonify({
                'success': False,
                'error': 'Chapter does not belong to this course'
            }), 404

        # Include lessons
        lessons = LessonRepository.find_by_chapter(chapter_id)
        chapter['lessons'] = lessons

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


@chapters_bp.route('/courses/<course_id>/chapters/<chapter_id>/progress', methods=['GET'])
@token_required
def get_chapter_progress(course_id, chapter_id):
    """
    Get user's progress for a specific chapter

    Response:
        200: Chapter progress data
        404: Chapter not found or not enrolled
    """
    try:
        user = get_current_user()

        # Verify chapter exists
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Chapter not found'
            }), 404

        # Get lessons for this chapter
        lessons = LessonRepository.find_by_chapter(chapter_id)
        total_lessons = len(lessons)
        lessons_completed = 0

        for lesson in lessons:
            progress = LessonRepository.get_user_progress(lesson['lesson_id'], user['user_id'])
            if progress and progress.get('completed_at'):
                lessons_completed += 1

        progress_percentage = (lessons_completed / total_lessons * 100) if total_lessons > 0 else 0
        is_completed = lessons_completed == total_lessons and total_lessons > 0

        progress_data = {
            'chapter_id': chapter_id,
            'course_id': course_id,
            'user_id': user['user_id'],
            'total_lessons': total_lessons,
            'lessons_completed': lessons_completed,
            'progress_percentage': round(progress_percentage, 1),
            'is_completed': is_completed,
            'status': 'completed' if is_completed else ('in_progress' if lessons_completed > 0 else 'not_started')
        }

        return jsonify({
            'success': True,
            'progress': progress_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get chapter progress',
            'details': str(e)
        }), 500
