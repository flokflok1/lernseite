"""
Course Enrollment and Progress Endpoints

Endpoints:
- GET    /courses/:id/progress - Get user's course progress
- POST   /courses/:id/enroll - Enroll in course
- GET    /courses/my-courses - Get user's created courses
- GET    /courses/enrolled - Get user's enrolled courses
"""

from flask import Blueprint, request, jsonify
from decimal import Decimal

from app.repositories.courses import CourseRepository
from app.repositories.courses.chapters import ChapterRepository
from app.repositories.courses.lessons import LessonRepository
from app.repositories.enrollments.core import EnrollmentRepository
from app.middleware.auth import token_required, get_current_user

# Blueprint for this module
enrollment_bp = Blueprint(
    'courses_enrollment',
    __name__,
    url_prefix='/courses'
)


@enrollment_bp.route('/<course_id>/progress', methods=['GET'])
@token_required
def get_course_progress(course_id):
    """
    Get user's progress for a course

    Response:
        200: Course progress data
        401: Unauthorized
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

        # Get enrollment, auto-enroll if not enrolled
        enrollment = EnrollmentRepository.find_by_user_and_course(user['user_id'], course_id)

        if not enrollment:
            # Auto-enroll the user (free enrollment)
            try:
                enrollment_data = {
                    'user_id': user['user_id'],
                    'course_id': course_id,
                    'price_paid': Decimal('0'),
                    'payment_method': 'free'
                }
                enrollment = EnrollmentRepository.create(enrollment_data)
                if not enrollment:
                    return jsonify({
                        'success': False,
                        'error': 'Auto-enrollment failed',
                        'message': 'Could not create enrollment record'
                    }), 500
            except Exception as enroll_err:
                return jsonify({
                    'success': False,
                    'error': 'Auto-enrollment failed',
                    'details': str(enroll_err)
                }), 500

        # Calculate actual progress
        progress_percentage = EnrollmentRepository.calculate_progress(user['user_id'], course_id)

        # Get chapter and lesson counts
        chapters = ChapterRepository.find_by_course(course_id)
        total_chapters = len(chapters)

        # Count completed chapters (all lessons in chapter completed)
        chapters_completed = 0
        total_lessons = 0
        lessons_completed = 0

        for chapter in chapters:
            lessons = LessonRepository.find_by_chapter(chapter['chapter_id'])
            chapter_lesson_count = len(lessons)
            total_lessons += chapter_lesson_count

            # Check how many lessons completed in this chapter
            chapter_completed_count = 0
            for lesson in lessons:
                progress = LessonRepository.get_user_progress(lesson['lesson_id'], user['user_id'])
                if progress and progress.get('completed_at'):
                    lessons_completed += 1
                    chapter_completed_count += 1

            # Chapter is completed if all its lessons are completed
            if chapter_lesson_count > 0 and chapter_completed_count == chapter_lesson_count:
                chapters_completed += 1

        progress_data = {
            'course_id': course_id,
            'user_id': user['user_id'],
            'enrollment_id': enrollment['enrollment_id'],
            'status': enrollment['status'],
            'progress_percentage': progress_percentage,
            'chapters_completed': chapters_completed,
            'total_chapters': total_chapters,
            'lessons_completed': lessons_completed,
            'total_lessons': total_lessons,
            'last_accessed_at': enrollment.get('last_accessed_at'),
            'enrolled_at': enrollment.get('enrolled_at'),
            'completed_at': enrollment.get('completed_at')
        }

        return jsonify({
            'success': True,
            'progress': progress_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get course progress',
            'details': str(e)
        }), 500


@enrollment_bp.route('/<course_id>/enroll', methods=['POST'])
@token_required
def enroll_in_course(course_id):
    """
    Enroll current user in course

    Request Body (optional):
        {
            "payment_method": "stripe",
            "payment_transaction_id": "txn_123"
        }

    Response:
        201: Enrollment successful
        400: Already enrolled or validation error
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

        # Check if course is published
        if not course['is_published']:
            return jsonify({
                'success': False,
                'error': 'Course not available',
                'message': 'This course is not currently published'
            }), 400

        # Check if already enrolled
        existing_enrollment = EnrollmentRepository.find_by_user_and_course(user['user_id'], course_id)

        if existing_enrollment:
            return jsonify({
                'success': False,
                'error': 'Already enrolled',
                'message': 'You are already enrolled in this course',
                'enrollment': existing_enrollment
            }), 400

        # Get payment data if provided
        data = request.get_json() or {}

        # Create enrollment
        enrollment_data = {
            'user_id': user['user_id'],
            'course_id': course_id,
            'price_paid': Decimal(str(course.get('price', 0))),
            'payment_method': data.get('payment_method'),
            'payment_transaction_id': data.get('payment_transaction_id')
        }

        enrollment = EnrollmentRepository.create(enrollment_data)

        return jsonify({
            'success': True,
            'message': 'Enrollment successful',
            'enrollment': enrollment
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Enrollment failed',
            'details': str(e)
        }), 500


@enrollment_bp.route('/my-courses', methods=['GET'])
@token_required
def get_my_courses():
    """
    Get courses created by current user

    Query Parameters:
        include_archived: Include archived courses (default: false)

    Response:
        200: List of created courses
    """
    try:
        user = get_current_user()
        include_archived = request.args.get('include_archived', 'false').lower() == 'true'

        courses = CourseRepository.find_by_creator(user['user_id'], include_archived)

        return jsonify({
            'success': True,
            'courses': courses,
            'total': len(courses)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get courses',
            'details': str(e)
        }), 500


@enrollment_bp.route('/enrolled', methods=['GET'])
@token_required
def get_enrolled_courses():
    """
    Get courses current user is enrolled in

    Query Parameters:
        status: Filter by status (active, completed, cancelled)
        page: Page number (default: 1)
        per_page: Items per page (default: 20)

    Response:
        200: List of enrolled courses
    """
    try:
        user = get_current_user()
        status = request.args.get('status')
        page = max(int(request.args.get('page', 1)), 1)
        per_page = min(int(request.args.get('per_page', 20)), 100)

        offset = (page - 1) * per_page

        result = EnrollmentRepository.find_by_user(
            user_id=user['user_id'],
            status=status,
            limit=per_page,
            offset=offset
        )

        total_pages = (result['total'] + per_page - 1) // per_page

        return jsonify({
            'success': True,
            'enrollments': result['items'],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': result['total'],
                'total_pages': total_pages
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get enrolled courses',
            'details': str(e)
        }), 500
