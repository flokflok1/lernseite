"""
LernsystemX Course API

Course management endpoints:
- GET    /api/v1/courses - List/search public courses
- POST   /api/v1/courses - Create course (creator)
- GET    /api/v1/courses/:id - Get course details
- PUT    /api/v1/courses/:id - Update course
- DELETE /api/v1/courses/:id - Archive course
- POST   /api/v1/courses/:id/publish - Publish course
- POST   /api/v1/courses/:id/unpublish - Unpublish course
- GET    /api/v1/courses/:id/stats - Get course statistics
- POST   /api/v1/courses/:id/enroll - Enroll in course
- GET    /api/v1/courses/:id/chapters - Get course modules
- POST   /api/v1/courses/:id/chapters - Create module
- GET    /api/v1/courses/my-courses - Get user's created courses
- GET    /api/v1/courses/enrolled - Get user's enrolled courses

Module endpoints:
- GET    /api/v1/chapters/:id - Get module
- PUT    /api/v1/chapters/:id - Update module
- DELETE /api/v1/chapters/:id - Delete module
- POST   /api/v1/chapters/:id/reorder - Reorder modules
- GET    /api/v1/chapters/:id/lessons - Get module lessons
- POST   /api/v1/chapters/:id/lessons - Create lesson

Lesson endpoints:
- GET    /api/v1/lessons/:id - Get lesson
- PUT    /api/v1/lessons/:id - Update lesson
- DELETE /api/v1/lessons/:id - Delete lesson
- POST   /api/v1/lessons/:id/complete - Mark lesson complete
- POST   /api/v1/lessons/:id/reorder - Reorder lessons

ISO 27001:2013 compliant - Course and content management
"""

from flask import request, jsonify, g
from pydantic import ValidationError
from decimal import Decimal

from app.api import api_v1
from app.models.course import (
    CourseCreate,
    CourseUpdate,
    ModuleCreate,
    ModuleUpdate,
    LessonCreate,
    LessonUpdate
)
from app.repositories.course_repository import CourseRepository
from app.repositories.chapter_repository import ChapterRepository
from app.repositories.lesson_repository import LessonRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.middleware.auth import token_required, role_required, get_current_user


# ============================================================================
# COURSE ENDPOINTS
# ============================================================================

@api_v1.route('/courses', methods=['GET'])
def list_courses():
    """
    List and search public published courses

    Query Parameters:
        search: Search term for title/description
        category: Filter by category
        level: Filter by level (beginner, intermediate, advanced, expert)
        language: Filter by language (de, en, etc.)
        min_price: Minimum price
        max_price: Maximum price
        tags: Comma-separated tags
        course_type: Filter by type (academy, creator)
        include_drafts: Include draft courses (admin only)
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)

    Response:
        200: List of courses with pagination
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

        # Only allow include_drafts for admins
        include_drafts = False
        if include_drafts_param:
            try:
                user = get_current_user()
                if user and user.get('role') in ['admin', 'superadmin', 'moderator']:
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
        return jsonify({
            'success': False,
            'error': 'Failed to list courses',
            'details': str(e)
        }), 500


@api_v1.route('/courses', methods=['POST'])
@role_required('creator', 'teacher', 'school_admin', 'company_admin', 'admin', 'superadmin')
def create_course():
    """
    Create a new course (creators and above)

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
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate with Pydantic
        course_data = CourseCreate(**data)

        # Add creator_id
        course_dict = course_data.model_dump()
        course_dict['creator_id'] = user['user_id']

        # Add organisation_id if user belongs to one
        if user.get('organisation_id'):
            course_dict['organisation_id'] = user['organisation_id']

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
        return jsonify({
            'success': False,
            'error': 'Course creation failed',
            'details': str(e)
        }), 500


@api_v1.route('/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    """
    Get course details

    For public published courses: Anyone can view
    For unpublished courses: Only creator, org members, or admins

    Response:
        200: Course details
        404: Course not found
        403: Access denied
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
        if course.get('organisation_id') and user.get('organisation_id') == course['organisation_id']:
            return jsonify({
                'success': True,
                'course': course
            }), 200

        # Admins can view any course
        if user['role'] in ['admin', 'superadmin']:
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
        return jsonify({
            'success': False,
            'error': 'Failed to get course',
            'details': str(e)
        }), 500


@api_v1.route('/courses/<course_id>', methods=['PUT'])
@token_required
def update_course(course_id):
    """
    Update course (creator or admin only)

    Request Body: Partial course data to update

    Response:
        200: Course updated successfully
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

        # Check permissions: creator, org admin, or superadmin
        is_creator = user['user_id'] == course['creator_id']
        is_org_admin = (
            user['role'] in ['school_admin', 'company_admin'] and
            user.get('organisation_id') == course.get('organisation_id')
        )
        is_admin = user['role'] in ['admin', 'superadmin']

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
        return jsonify({
            'success': False,
            'error': 'Course update failed',
            'details': str(e)
        }), 500


@api_v1.route('/courses/<course_id>', methods=['DELETE'])
@token_required
def archive_course(course_id):
    """
    Archive course (soft delete)

    Response:
        200: Course archived successfully
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
        return jsonify({
            'success': False,
            'error': 'Course archiving failed',
            'details': str(e)
        }), 500


@api_v1.route('/courses/<course_id>/publish', methods=['POST'])
@token_required
def publish_course(course_id):
    """
    Publish course (make it available for enrollment)

    Response:
        200: Course published successfully
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
        return jsonify({
            'success': False,
            'error': 'Course publishing failed',
            'details': str(e)
        }), 500


@api_v1.route('/courses/<course_id>/unpublish', methods=['POST'])
@token_required
def unpublish_course(course_id):
    """
    Unpublish course

    Response:
        200: Course unpublished successfully
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

        # Unpublish course
        unpublished_course = CourseRepository.unpublish(course_id)

        return jsonify({
            'success': True,
            'message': 'Course unpublished successfully',
            'course': unpublished_course
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Course unpublishing failed',
            'details': str(e)
        }), 500


@api_v1.route('/courses/<course_id>/stats', methods=['GET'])
@token_required
def get_course_stats(course_id):
    """
    Get course statistics (creator or admin only)

    Response:
        200: Course statistics
        403: Access denied
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

        # Get statistics
        stats = CourseRepository.get_statistics(course_id)
        enrollment_stats = EnrollmentRepository.get_enrollment_stats(course_id)

        return jsonify({
            'success': True,
            'stats': {
                **stats,
                **enrollment_stats
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get statistics',
            'details': str(e)
        }), 500


@api_v1.route('/courses/<course_id>/progress', methods=['GET'])
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


@api_v1.route('/courses/<course_id>/enroll', methods=['POST'])
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


@api_v1.route('/courses/my-courses', methods=['GET'])
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


@api_v1.route('/courses/enrolled', methods=['GET'])
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


# ============================================================================
# MODULE ENDPOINTS
# ============================================================================

@api_v1.route('/courses/<course_id>/chapters', methods=['GET'])
def get_course_chapters(course_id):
    """
    Get all modules for a course

    Query Parameters:
        include_lessons: Include lessons in each chapter (default: true)

    Response:
        200: List of modules with lessons
        404: Course not found
    """
    try:
        course = CourseRepository.find_by_id(course_id)

        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        modules = ChapterRepository.find_by_course(course_id)

        # Include lessons by default for frontend player navigation
        include_lessons = request.args.get('include_lessons', 'true').lower() != 'false'

        if include_lessons:
            for module in modules:
                lessons = LessonRepository.find_by_chapter(module['chapter_id'])
                module['lessons'] = lessons

        return jsonify({
            'success': True,
            'chapters': modules,
            'total': len(modules)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get modules',
            'details': str(e)
        }), 500


@api_v1.route('/courses/<course_id>/chapters', methods=['POST'])
@token_required
def create_chapter(course_id):
    """
    Create a new module in a course (creator only)

    Request Body:
        {
            "title": "Modul 1: Einführung",
            "description": "Grundlagen und erste Schritte",
            "duration_minutes": 120,
            "order_index": 1
        }

    Response:
        201: Module created successfully
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

        # Create module
        module = ChapterRepository.create(chapter_dict)

        return jsonify({
            'success': True,
            'message': 'Module created successfully',
            'chapter': module
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
            'error': 'Module creation failed',
            'details': str(e)
        }), 500


@api_v1.route('/courses/<course_id>/chapters/<chapter_id>', methods=['GET'])
@token_required
def get_course_chapter(course_id, chapter_id):
    """
    Get a specific chapter within a course context

    Response:
        200: Chapter details with lessons
        404: Chapter or course not found
    """
    try:
        user = get_current_user()

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


@api_v1.route('/courses/<course_id>/chapters/<chapter_id>/progress', methods=['GET'])
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


@api_v1.route('/chapters/<int:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    """
    Get module details

    Response:
        200: Module details
        404: Module not found
    """
    try:
        module = ChapterRepository.find_by_id(chapter_id)

        if not module:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404

        return jsonify({
            'success': True,
            'chapter': module
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get module',
            'details': str(e)
        }), 500


@api_v1.route('/chapters/<int:chapter_id>', methods=['PUT'])
@token_required
def update_chapter(chapter_id):
    """
    Update module (creator only)

    Request Body: Partial module data to update

    Response:
        200: Module updated successfully
        403: Access denied
        404: Module not found
    """
    try:
        user = get_current_user()
        module = ChapterRepository.find_by_id(chapter_id)

        if not module:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404

        # Get course to check permissions
        course = CourseRepository.find_by_id(module['course_id'])

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

        # Update module
        updated_module = ChapterRepository.update(chapter_id, chapter_data.model_dump(exclude_none=True))

        return jsonify({
            'success': True,
            'message': 'Module updated successfully',
            'chapter': updated_module
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
            'error': 'Module update failed',
            'details': str(e)
        }), 500


@api_v1.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@token_required
def delete_chapter(chapter_id):
    """
    Delete module (creator only)

    WARNING: This will cascade delete all lessons in the module!

    Response:
        200: Module deleted successfully
        403: Access denied
        404: Module not found
    """
    try:
        user = get_current_user()
        module = ChapterRepository.find_by_id(chapter_id)

        if not module:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404

        # Get course to check permissions
        course = CourseRepository.find_by_id(module['course_id'])

        is_creator = user['user_id'] == course['creator_id']
        is_admin = user['role'] in ['admin', 'superadmin']

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Delete module
        ChapterRepository.delete(chapter_id)

        return jsonify({
            'success': True,
            'message': 'Module deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Module deletion failed',
            'details': str(e)
        }), 500


@api_v1.route('/chapters/<chapter_id>/lessons', methods=['GET'])
def get_chapter_lessons(chapter_id):
    """
    Get all lessons for a module

    Response:
        200: List of lessons
        404: Module not found
    """
    try:
        module = ChapterRepository.find_by_id(chapter_id)

        if not module:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404

        lessons = LessonRepository.find_by_module(chapter_id)

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


@api_v1.route('/chapters/<chapter_id>/lessons', methods=['POST'])
@token_required
def create_lesson(chapter_id):
    """
    Create a new lesson in a module (creator only)

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
        404: Module not found
    """
    try:
        user = get_current_user()
        module = ChapterRepository.find_by_id(chapter_id)

        if not module:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404

        # Get course to check permissions
        course = CourseRepository.find_by_id(module['course_id'])

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


# ============================================================================
# LESSON ENDPOINTS
# ============================================================================

@api_v1.route('/lessons/<lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """
    Get lesson details

    Response:
        200: Lesson details
        404: Lesson not found
    """
    try:
        lesson = LessonRepository.find_by_id(lesson_id)  # lesson_id is UUID string

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


@api_v1.route('/lessons/<lesson_id>', methods=['PUT'])
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


@api_v1.route('/lessons/<lesson_id>', methods=['DELETE'])
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


@api_v1.route('/lessons/<lesson_id>/complete', methods=['POST'])
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


@api_v1.route('/lessons/<lesson_id>/start', methods=['POST'])
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


@api_v1.route('/lessons/<lesson_id>/progress', methods=['GET'])
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


@api_v1.route('/lessons/<lesson_id>/progress', methods=['PATCH'])
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


@api_v1.route('/lessons/<lesson_id>/methods', methods=['GET'])
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
                'icon': m['config'].get('icon', '📚') if m['config'] else '📚'
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
