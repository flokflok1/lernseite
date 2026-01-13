"""
LernsystemX Courses API - Consolidated

User-facing course operations, enrollment, and progress tracking.

Course Operations:
- GET /courses - List/search public courses
- GET /courses/:id - Get course details
- POST /courses - Create course (creators+)
- PUT /courses/:id - Update course
- DELETE /courses/:id - Archive course
- POST /courses/:id/publish - Publish course
- POST /courses/:id/unpublish - Unpublish course

Enrollment & Progress:
- POST /courses/:id/enroll - Enroll in course
- GET /courses/:id/progress - Get course progress
- GET /courses/my-courses - Get user's created courses
- GET /courses/enrolled - Get user's enrolled courses

Statistics:
- GET /courses/:id/stats - Get course statistics

All routes: /api/v1/courses/*
ISO 9001:2015 compliant - Course Management Layer
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from decimal import Decimal
from typing import Dict, Any, Tuple
import logging

from app.models.course import CourseCreate, CourseUpdate
from app.repositories.courses import CourseRepository
from app.repositories.courses.chapters import ChapterRepository
from app.repositories.courses.lessons import LessonRepository
from app.repositories.enrollments.core import EnrollmentRepository
from app.middleware.auth import token_required, role_required, get_current_user

# Blueprints
courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

__all__ = ['courses_bp']

logger = logging.getLogger(__name__)


# =============================================================================
# COURSE CRUD - READ OPERATIONS
# =============================================================================

@courses_bp.route('', methods=['GET'])
def list_courses():
    """
    List and search public published courses.

    Query Parameters:
        search (str): Search term for title/description
        category (str): Filter by category
        level (str): Filter by level (beginner, intermediate, advanced, expert)
        language (str): Filter by language (de, en, etc.)
        min_price (float): Minimum price
        max_price (float): Maximum price
        tags (str): Comma-separated tags
        course_type (str): Filter by type (academy, creator)
        include_drafts (bool): Include draft courses (admin only)
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20, max: 100)

    Response:
        200: List of courses with pagination
        500: Server error
    """
    try:
        # Get query parameters
        search_term = request.args.get('search')
        category = request.args.get('category')
        level = request.args.get('level')
        language = request.args.get('language')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        tags_str = request.args.get('tags')
        course_type = request.args.get('course_type')
        include_drafts_param = request.args.get('include_drafts', 'false').lower() == 'true'
        page = max(int(request.args.get('page', 1)), 1)
        per_page = min(int(request.args.get('per_page', 20)), 100)

        # Parse tags
        tags = tags_str.split(',') if tags_str else None

        # Only allow include_drafts for moderator+ (RBAC 2.0: dynamic from DB)
        include_drafts = False
        if include_drafts_param:
            try:
                user = get_current_user()
                from app.services.permission_service import PermissionService
                if user and PermissionService.check_threshold(user, 'courses.view_drafts'):
                    include_drafts = True
            except:
                pass

        # Calculate offset
        offset = (page - 1) * per_page

        # Search courses
        result = CourseRepository.search_public_courses(
            search_term=search_term,
            category=category,
            level=level,
            language=language,
            min_price=min_price,
            max_price=max_price,
            tags=tags,
            course_type=course_type,
            include_drafts=include_drafts,
            limit=per_page,
            offset=offset
        )

        total_pages = (result['total'] + per_page - 1) // per_page

        return jsonify({
            'success': True,
            'courses': result['items'],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': result['total'],
                'total_pages': total_pages
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing courses: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list courses',
            'details': str(e)
        }), 500


@courses_bp.route('/<course_id>', methods=['GET'])
def get_course(course_id: str):
    """
    Get course details.

    For public published courses: Anyone can view
    For unpublished courses: Only creator, org members, or admins

    Response:
        200: Course details
        401: Authentication required
        403: Access denied
        404: Course not found
    """
    try:
        course = CourseRepository.find_by_id(course_id)

        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found',
                'message': 'The requested course does not exist'
            }), 404

        # Check access permissions
        user = get_current_user()

        # Public published courses are accessible to everyone
        if course['is_public'] and course['is_published']:
            return jsonify({
                'success': True,
                'course': course
            }), 200

        # For non-public courses, check permissions
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'message': 'This course requires authentication to view'
            }), 401

        # Course creator can always view
        if user['user_id'] == course['creator_id']:
            return jsonify({
                'success': True,
                'course': course
            }), 200

        # Organisation members can view org courses
        if course.get('organization_id') and user.get('organization_id') == course['organization_id']:
            return jsonify({
                'success': True,
                'course': course
            }), 200

        # Admins can view any course (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        if PermissionService.check_threshold(user, 'courses.view_any'):
            return jsonify({
                'success': True,
                'course': course
            }), 200

        # Check if user is enrolled
        if EnrollmentRepository.is_user_enrolled(user['user_id'], course_id):
            return jsonify({
                'success': True,
                'course': course
            }), 200

        return jsonify({
            'success': False,
            'error': 'Access denied',
            'message': 'You do not have permission to view this course'
        }), 403

    except Exception as e:
        logger.error(f"Error getting course: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get course',
            'details': str(e)
        }), 500


# =============================================================================
# COURSE CRUD - WRITE OPERATIONS
# =============================================================================

@courses_bp.route('', methods=['POST'])
@role_required('creator', 'teacher', 'school_admin', 'company_admin', 'admin', 'superadmin')
def create_course():
    """
    Create a new course (creators and above).

    Request Body:
        {
            "title": "Python Grundlagen",
            "description": "Lerne Python von Grund auf",
            "category": "Programming",
            "level": "beginner",
            "language": "de",
            "price": 99.99,
            "is_public": false,
            "tags": ["python", "programming", "beginner"]
        }

    Response:
        201: Course created successfully
        400: Validation error
        403: Insufficient permissions
        500: Server error
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate with Pydantic
        course_data = CourseCreate(**data)

        # Add creator_id
        course_dict = course_data.model_dump()
        course_dict['creator_id'] = user['user_id']

        # Add organization_id if user belongs to one
        if user.get('organization_id'):
            course_dict['organization_id'] = user['organization_id']

        # Create course
        course = CourseRepository.create(course_dict)

        return jsonify({
            'success': True,
            'message': 'Course created successfully',
            'course': course
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        logger.error(f"Error creating course: {e}")
        return jsonify({
            'success': False,
            'error': 'Course creation failed',
            'details': str(e)
        }), 500


@courses_bp.route('/<course_id>', methods=['PUT'])
@token_required
def update_course(course_id: str):
    """
    Update course (creator or admin only).

    Request Body: Partial course data to update

    Response:
        200: Course updated successfully
        403: Access denied
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

        # Check permissions: creator, org admin, or admin+ (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        is_creator = user['user_id'] == course['creator_id']
        # hierarchy_level 5 = school_admin, company_admin
        is_org_admin = (
            user.get('hierarchy_level', 0) == 5 and
            user.get('organization_id') == course.get('organization_id')
        )
        is_admin = PermissionService.check_threshold(user, 'courses.edit_any')

        if not (is_creator or is_org_admin or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied',
                'message': 'You can only update your own courses'
            }), 403

        data = request.get_json()

        # Validate with Pydantic
        course_data = CourseUpdate(**data)

        # Update course
        updated_course = CourseRepository.update(course_id, course_data.model_dump(exclude_none=True))

        return jsonify({
            'success': True,
            'message': 'Course updated successfully',
            'course': updated_course
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        logger.error(f"Error updating course: {e}")
        return jsonify({
            'success': False,
            'error': 'Course update failed',
            'details': str(e)
        }), 500


@courses_bp.route('/<course_id>', methods=['DELETE'])
@token_required
def archive_course(course_id: str):
    """
    Archive course (soft delete).

    Response:
        200: Course archived successfully
        403: Access denied
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

        # Check permissions (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        is_creator = user['user_id'] == course['creator_id']
        is_admin = PermissionService.check_threshold(user, 'courses.edit_any')

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied',
                'message': 'You can only archive your own courses'
            }), 403

        # Archive course
        CourseRepository.archive(course_id)

        return jsonify({
            'success': True,
            'message': 'Course archived successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error archiving course: {e}")
        return jsonify({
            'success': False,
            'error': 'Course archiving failed',
            'details': str(e)
        }), 500


@courses_bp.route('/<course_id>/publish', methods=['POST'])
@token_required
def publish_course(course_id: str):
    """
    Publish course (make it available for enrollment).

    Response:
        200: Course published successfully
        400: Course already published or cannot be published
        403: Access denied
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

        # Check permissions (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        is_creator = user['user_id'] == course['creator_id']
        is_admin = PermissionService.check_threshold(user, 'courses.edit_any')

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Publish course
        published_course = CourseRepository.publish(course_id)

        if not published_course:
            return jsonify({
                'success': False,
                'error': 'Course already published or cannot be published'
            }), 400

        return jsonify({
            'success': True,
            'message': 'Course published successfully',
            'course': published_course
        }), 200

    except Exception as e:
        logger.error(f"Error publishing course: {e}")
        return jsonify({
            'success': False,
            'error': 'Course publishing failed',
            'details': str(e)
        }), 500


@courses_bp.route('/<course_id>/unpublish', methods=['POST'])
@token_required
def unpublish_course(course_id: str):
    """
    Unpublish course.

    Response:
        200: Course unpublished successfully
        403: Access denied
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

        # Check permissions (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        is_creator = user['user_id'] == course['creator_id']
        is_admin = PermissionService.check_threshold(user, 'courses.edit_any')

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Unpublish course
        unpublished_course = CourseRepository.unpublish(course_id)

        return jsonify({
            'success': True,
            'message': 'Course unpublished successfully',
            'course': unpublished_course
        }), 200

    except Exception as e:
        logger.error(f"Error unpublishing course: {e}")
        return jsonify({
            'success': False,
            'error': 'Course unpublishing failed',
            'details': str(e)
        }), 500


# =============================================================================
# COURSE STATISTICS
# =============================================================================

@courses_bp.route('/<course_id>/stats', methods=['GET'])
@token_required
def get_course_stats(course_id: str):
    """
    Get course statistics (creator or admin only).

    Response:
        200: Course statistics
        403: Access denied
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

        # Check permissions (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        is_creator = user['user_id'] == course['creator_id']
        is_admin = PermissionService.check_threshold(user, 'courses.edit_any')

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied',
                'message': 'You can only view stats for your own courses'
            }), 403

        # Get statistics
        stats = CourseRepository.get_statistics(course_id)

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting course stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get course statistics',
            'details': str(e)
        }), 500


# =============================================================================
# COURSE ENROLLMENT & PROGRESS
# =============================================================================

@courses_bp.route('/<course_id>/progress', methods=['GET'])
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


@courses_bp.route('/<course_id>/enroll', methods=['POST'])
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


@courses_bp.route('/my-courses', methods=['GET'])
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

        # Get user's courses
        courses = CourseRepository.find_by_creator(
            creator_id=user['user_id'],
            limit=per_page,
            offset=offset
        )

        # Get total count
        total = CourseRepository.count_by_creator(user['user_id'])
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


@courses_bp.route('/enrolled', methods=['GET'])
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
