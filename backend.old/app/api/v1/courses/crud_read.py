"""
Course Read Operations (GET Endpoints)

Endpoints:
- GET /courses - List/search public courses
- GET /courses/:id - Get course details
"""

from flask import Blueprint, request, jsonify

from app.repositories.courses import CourseRepository
from app.repositories.enrollments.core import EnrollmentRepository
from app.middleware.auth import get_current_user

# Import blueprint from write.py and register read endpoints
from .crud_write import courses_bp


@courses_bp.route('', methods=['GET'])
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


@courses_bp.route('/<course_id>', methods=['GET'])
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
        if course.get('organization_id') and user.get('organization_id') == course['organization_id']:
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
