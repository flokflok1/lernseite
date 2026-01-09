"""
Lesson Management Endpoints

Endpoints:
- GET    /lessons/:id - Get lesson details
- PUT    /lessons/:id - Update lesson
- DELETE /lessons/:id - Delete lesson
- POST   /lessons/:id/complete - Mark lesson as completed
- POST   /lessons/:id/start - Mark lesson as started
- GET    /lessons/:id/progress - Get lesson progress
- PATCH  /lessons/:id/progress - Update lesson progress
- GET    /lessons/:id/methods - Get learning methods for lesson
"""

from flask import Blueprint, request, jsonify
from decimal import Decimal
from pydantic import ValidationError

from app.models.course import LessonUpdate
from app.repositories.courses import CourseRepository
from app.repositories.courses.lessons import LessonRepository
from app.repositories.enrollments.core import EnrollmentRepository
from app.middleware.auth import token_required, get_current_user

# Blueprint for this module
lessons_bp = Blueprint(
    'lessons_management',
    __name__,
    url_prefix='/lessons'
)


@lessons_bp.route('/<lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """
    Get lesson details

    Response:
        200: Lesson details
        404: Lesson not found
    """
    try:
        lesson = LessonRepository.find_by_id(lesson_id)

        if not lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        return jsonify({
            'success': True,
            'lesson': lesson
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get lesson',
            'details': str(e)
        }), 500


@lessons_bp.route('/<lesson_id>', methods=['PUT'])
@token_required
def update_lesson(lesson_id):
    """
    Update lesson (creator only)

    Request Body: Partial lesson data to update

    Response:
        200: Lesson updated successfully
        403: Access denied
        404: Lesson not found
    """
    try:
        user = get_current_user()
        lesson = LessonRepository.find_by_id(lesson_id)

        if not lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        # Get course to check permissions
        course = CourseRepository.find_by_id(lesson['course_id'])

        is_creator = user['user_id'] == course['creator_id']
        is_admin = user['role'] in ['admin', 'superadmin']

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json()

        # Validate with Pydantic
        lesson_data = LessonUpdate(**data)

        # Update lesson
        updated_lesson = LessonRepository.update(lesson_id, lesson_data.model_dump(exclude_none=True))

        return jsonify({
            'success': True,
            'message': 'Lesson updated successfully',
            'lesson': updated_lesson
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
            'error': 'Lesson update failed',
            'details': str(e)
        }), 500


@lessons_bp.route('/<lesson_id>', methods=['DELETE'])
@token_required
def delete_lesson(lesson_id):
    """
    Delete lesson (creator only)

    Response:
        200: Lesson deleted successfully
        403: Access denied
        404: Lesson not found
    """
    try:
        user = get_current_user()
        lesson = LessonRepository.find_by_id(lesson_id)

        if not lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        # Get course to check permissions
        course = CourseRepository.find_by_id(lesson['course_id'])

        is_creator = user['user_id'] == course['creator_id']
        is_admin = user['role'] in ['admin', 'superadmin']

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Delete lesson
        LessonRepository.delete(lesson_id)

        return jsonify({
            'success': True,
            'message': 'Lesson deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Lesson deletion failed',
            'details': str(e)
        }), 500


@lessons_bp.route('/<lesson_id>/complete', methods=['POST'])
@token_required
def complete_lesson(lesson_id):
    """
    Mark lesson as completed for current user

    Response:
        200: Lesson marked as complete
        404: Lesson not found
    """
    try:
        user = get_current_user()
        lesson = LessonRepository.find_by_id(lesson_id)

        if not lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        # Auto-enroll if not enrolled
        if not EnrollmentRepository.is_user_enrolled(user['user_id'], lesson['course_id']):
            enrollment_data = {
                'user_id': user['user_id'],
                'course_id': lesson['course_id'],
                'price_paid': Decimal('0'),
                'payment_method': 'free',
                'status': 'active'
            }
            EnrollmentRepository.create(enrollment_data)

        # Mark lesson as completed
        progress = LessonRepository.mark_completed(lesson_id, user['user_id'])

        # Update enrollment progress
        enrollment = EnrollmentRepository.find_by_user_and_course(user['user_id'], lesson['course_id'])
        if enrollment:
            new_progress = EnrollmentRepository.calculate_progress(user['user_id'], lesson['course_id'])
            EnrollmentRepository.update_progress(enrollment['enrollment_id'], new_progress)

        return jsonify({
            'success': True,
            'message': 'Lesson completed',
            'progress': progress
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to complete lesson',
            'details': str(e)
        }), 500


@lessons_bp.route('/<lesson_id>/start', methods=['POST'])
@token_required
def start_lesson(lesson_id):
    """
    Mark lesson as started for current user

    Response:
        200: Lesson marked as started
        404: Lesson not found
    """
    try:
        user = get_current_user()
        lesson = LessonRepository.find_by_id(lesson_id)

        if not lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        # Auto-enroll if not enrolled
        if not EnrollmentRepository.is_user_enrolled(user['user_id'], lesson['course_id']):
            enrollment_data = {
                'user_id': user['user_id'],
                'course_id': lesson['course_id'],
                'price_paid': Decimal('0'),
                'payment_method': 'free',
                'status': 'active'
            }
            EnrollmentRepository.create(enrollment_data)

        # Mark lesson as started
        progress = LessonRepository.mark_started(lesson_id, user['user_id'])

        return jsonify({
            'success': True,
            'message': 'Lesson started',
            'progress': progress
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to start lesson',
            'details': str(e)
        }), 500


@lessons_bp.route('/<lesson_id>/progress', methods=['GET'])
@token_required
def get_lesson_progress(lesson_id):
    """
    Get progress for a specific lesson

    Response:
        200: Lesson progress
        404: Lesson not found or no progress
    """
    try:
        user = get_current_user()
        lesson = LessonRepository.find_by_id(lesson_id)

        if not lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        progress = LessonRepository.get_user_progress(lesson_id, user['user_id'])

        if not progress:
            # Return default progress if none exists
            progress = {
                'lesson_id': lesson_id,
                'user_id': user['user_id'],
                'status': 'not_started',
                'progress_percentage': 0,
                'time_spent_minutes': 0
            }

        return jsonify({
            'success': True,
            'progress': progress
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get lesson progress',
            'details': str(e)
        }), 500


@lessons_bp.route('/<lesson_id>/progress', methods=['PATCH'])
@token_required
def update_lesson_progress(lesson_id):
    """
    Update progress for a specific lesson

    Request Body:
        {
            "progress_percentage": 50,
            "time_spent_minutes": 10
        }

    Response:
        200: Progress updated
        404: Lesson not found
    """
    try:
        user = get_current_user()
        lesson = LessonRepository.find_by_id(lesson_id)

        if not lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        data = request.get_json()
        progress_percentage = data.get('progress_percentage', 0)
        time_spent_minutes = data.get('time_spent_minutes')

        progress = LessonRepository.update_progress(
            lesson_id,
            user['user_id'],
            progress_percentage,
            time_spent_minutes
        )

        return jsonify({
            'success': True,
            'message': 'Progress updated',
            'progress': progress
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update lesson progress',
            'details': str(e)
        }), 500


@lessons_bp.route('/<lesson_id>/methods', methods=['GET'])
def get_lesson_methods(lesson_id):
    """
    Get learning methods for a specific lesson

    Response:
        200: List of learning methods for this lesson
        404: Lesson not found
    """
    from app.database.connection import fetch_all

    try:
        lesson = LessonRepository.find_by_id(lesson_id)

        if not lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        # Get learning methods for this lesson
        query = """
            SELECT
                method_id,
                method_type,
                title as method_name,
                instructions as description,
                tier as category,
                data as config,
                duration_minutes,
                difficulty,
                order_index,
                published
            FROM learning_methods
            WHERE lesson_id = %s
            ORDER BY order_index ASC
        """
        methods = fetch_all(query, (lesson_id,))

        # Transform to API format
        methods_list = []
        for m in methods:
            methods_list.append({
                'method_id': str(m['method_id']),
                'method_type': m['method_type'],
                'method_name': m['method_name'],
                'description': m['description'],
                'category': m['category'],
                'config': m['config'],
                'duration_minutes': m['duration_minutes'],
                'difficulty': m['difficulty'],
                'requires_ai': m['config'].get('requires_ai', False) if m['config'] else False,
                'token_cost': m['config'].get('token_cost', 0) if m['config'] else 0,
                'is_premium': m['category'] in ['premium', 'pro'],
                'icon': m['config'].get('icon', '') if m['config'] else ''
            })

        return jsonify({
            'success': True,
            'methods': methods_list,
            'total': len(methods_list)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get lesson methods',
            'details': str(e)
        }), 500
