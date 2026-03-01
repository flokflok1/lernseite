"""
LernsystemX Courses API - Enrollment & Progress

User course enrollment and progress tracking.

Enrollment & Progress Operations:
- POST /courses/:id/enroll - Enroll in course
- GET /courses/:id/progress - Get course progress
- GET /courses/my-courses - Get user's created courses
- GET /courses/enrolled - Get user's enrolled courses

All routes: /api/v1/courses/*
ISO 9001:2015 compliant - Course Management Layer
"""

from flask import Blueprint, request, jsonify
from decimal import Decimal
import logging

from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.infrastructure.persistence.repositories.courses.content.chapters import ChapterRepository
from app.infrastructure.persistence.repositories.courses.content.lessons import LessonRepository
from app.infrastructure.persistence.repositories.enrollments.core import EnrollmentRepository
from app.api.middleware.auth import token_required, get_current_user

logger = logging.getLogger(__name__)

enrollment_bp = Blueprint('courses_enrollment', __name__, url_prefix='/courses')

__all__ = ['enrollment_bp']


# =============================================================================
# COURSE ENROLLMENT & PROGRESS
# =============================================================================

@enrollment_bp.route('/<course_id>/progress', methods=['GET'])
@token_required
def get_course_progress(course_id: str):
    """
    Get user's progress for a course.

    Automatically enrolls user if not enrolled (free enrollment).

    Response:
        200: Course progress data
        404: Course not found
        500: Server error
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
                logger.error(f"Auto-enrollment error: {enroll_err}")
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
        logger.error(f"Error getting course progress: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get course progress',
            'details': str(e)
        }), 500


@enrollment_bp.route('/<course_id>/enroll', methods=['POST'])
@token_required
def enroll_in_course(course_id: str):
    """
    Enroll current user in course.

    Request Body (optional):
        {
            "payment_method": "stripe",
            "payment_transaction_id": "txn_123"
        }

    Response:
        201: Enrollment successful
        400: Already enrolled or validation error
        404: Course not found
        500: Server error
    """
    try:
        user = get_current_user()
        course = CourseRepository.find_by_id(course_id)

        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Check if already enrolled
        existing_enrollment = EnrollmentRepository.find_by_user_and_course(user['user_id'], course_id)

        if existing_enrollment:
            return jsonify({
                'success': False,
                'error': 'Already enrolled',
                'message': 'You are already enrolled in this course',
                'enrollment': existing_enrollment
            }), 400

        # Get payment data from request
        data = request.get_json() or {}
        payment_method = data.get('payment_method', 'free')
        payment_transaction_id = data.get('payment_transaction_id')

        # Determine price
        price_to_pay = Decimal(str(course.get('price', 0)))

        # Create enrollment
        enrollment_data = {
            'user_id': user['user_id'],
            'course_id': course_id,
            'price_paid': price_to_pay,
            'payment_method': payment_method,
            'payment_transaction_id': payment_transaction_id
        }

        enrollment = EnrollmentRepository.create(enrollment_data)

        if not enrollment:
            return jsonify({
                'success': False,
                'error': 'Enrollment failed',
                'message': 'Could not create enrollment record'
            }), 500

        return jsonify({
            'success': True,
            'message': 'Enrollment successful',
            'enrollment': enrollment
        }), 201

    except Exception as e:
        logger.error(f"Error enrolling in course: {e}")
        return jsonify({
            'success': False,
            'error': 'Enrollment failed',
            'details': str(e)
        }), 500


@enrollment_bp.route('/my-courses', methods=['GET'])
@token_required
def get_my_courses():
    """
    Get user's created courses.

    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20)

    Response:
        200: List of user's created courses
        500: Server error
    """
    try:
        user = get_current_user()
        page = max(int(request.args.get('page', 1)), 1)
        per_page = min(int(request.args.get('per_page', 20)), 100)
        offset = (page - 1) * per_page

        # Get user's courses (all types: academy + creator)
        include_archived = request.args.get('include_archived', 'false').lower() == 'true'
        courses = CourseRepository.find_by_creator(
            creator_id=user['user_id'],
            include_archived=include_archived,
            course_type=None,
            limit=per_page,
            offset=offset
        )

        # Get total count
        total = CourseRepository.count_by_creator(
            user['user_id'],
            include_archived=include_archived,
            course_type=None
        )
        total_pages = (total + per_page - 1) // per_page

        return jsonify({
            'success': True,
            'courses': courses,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting my courses: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get courses',
            'details': str(e)
        }), 500


@enrollment_bp.route('/enrolled', methods=['GET'])
@token_required
def get_enrolled_courses():
    """
    Get user's enrolled courses.

    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20)
        status (str): Filter by status (active, completed, archived)

    Response:
        200: List of user's enrolled courses
        500: Server error
    """
    try:
        user = get_current_user()
        page = max(int(request.args.get('page', 1)), 1)
        per_page = min(int(request.args.get('per_page', 20)), 100)
        status = request.args.get('status')
        offset = (page - 1) * per_page

        # Get user's enrollments (returns dict with 'items', 'total', 'limit', 'offset')
        enrollments_data = EnrollmentRepository.find_by_user(
            user_id=user['user_id'],
            status=status,
            limit=per_page,
            offset=offset
        )

        # Extract items and total
        total = enrollments_data.get('total', 0)
        total_pages = (total + per_page - 1) // per_page

        return jsonify({
            'success': True,
            'enrollments': enrollments_data.get('items', []),  # Return array, not object
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting enrolled courses: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get enrolled courses',
            'details': str(e)
        }), 500


@enrollment_bp.route('/<course_id>/chapters/<chapter_id>/progress', methods=['GET'])
@token_required
def get_chapter_progress(course_id: str, chapter_id: str):
    """
    Get user's progress for a specific chapter.

    Response:
        200: Chapter progress data
        500: Server error
    """
    try:
        user = get_current_user()
        progress_data = ChapterRepository.get_chapter_progress(
            chapter_id, user['user_id']
        )

        total = progress_data.get('total_lessons', 0)
        completed = progress_data.get('completed_lessons', 0)
        pct = progress_data.get('progress_percentage', 0)

        if total == 0:
            status = 'not_started'
        elif completed >= total:
            status = 'completed'
        elif completed > 0 or pct > 0:
            status = 'in_progress'
        else:
            status = 'not_started'

        progress = {
            'chapter_id': str(chapter_id),
            'user_id': user['user_id'],
            'status': status,
            'progress_percentage': pct,
            'lessons_completed': completed,
            'total_lessons': total,
            'started_at': None,
            'completed_at': None,
        }

        return jsonify({'success': True, 'progress': progress}), 200

    except Exception as e:
        logger.error(f"Error getting chapter progress: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500
