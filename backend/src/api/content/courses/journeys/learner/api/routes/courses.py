"""
Learner Course Routes (Journey-Based API)

Learner journey for course browsing and enrollment.
ALL data loaded dynamically from database - NO hardcoded values.

Endpoints:
- GET /api/v1/courses - Browse published courses
- GET /api/v1/courses/<id> - Get course details
- GET /api/v1/courses/categories - Get available categories (from DB)
- GET /api/v1/my/courses - Get user's enrolled courses
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
from src.core.auth.permissions import require_auth
from src.api.content.courses.core.application.services.course_service import CourseService
from src.core.utils.validators import Validators, ValidationError


# Create blueprint
learner_courses_bp = Blueprint('learner_courses', __name__, url_prefix='/api/v1/courses')


@learner_courses_bp.route('', methods=['GET'])
def browse_courses():
    """
    Browse published public courses.

    Query params (all optional):
    - category_id: Filter by category (from DB)
    - limit: Result limit (default 100)
    - offset: Result offset (default 0)

    Returns:
        200: List of published courses
        500: Server error
    """
    try:
        # Get query parameters
        category_id = request.args.get('category_id')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        # Get published courses
        courses = CourseService.list_published_courses(
            category_id=category_id,
            limit=limit,
            offset=offset
        )

        # Convert to dict (public data only)
        courses_data = [
            {
                'course_id': c.course_id,
                'title': c.title,
                'description': c.description,
                'category_id': c.category_id,
                'difficulty_level': c.difficulty_level,
                'price': c.price,
                'published_at': c.published_at.isoformat() if c.published_at else None
            }
            for c in courses
        ]

        return jsonify({
            'success': True,
            'data': courses_data,
            'meta': {
                'limit': limit,
                'offset': offset,
                'count': len(courses_data)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BROWSE_COURSES_ERROR',
                'message': str(e)
            }
        }), 500


@learner_courses_bp.route('/<course_id>', methods=['GET'])
def get_course(course_id: str):
    """
    Get course details.

    Args:
        course_id: Course UUID

    Returns:
        200: Course data (public or accessible)
        403: Permission denied
        404: Course not found
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(course_id)

        # Get user info (optional for public courses)
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)

        # Get course
        course = CourseService.get_course_by_id(
            course_id=course_id,
            user_id=user_id,
            user_role=user_role
        )

        if not course:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'COURSE_NOT_FOUND',
                    'message': f'Course {course_id} not found'
                }
            }), 404

        # Convert to dict (public data only for non-authenticated)
        course_data = {
            'course_id': course.course_id,
            'title': course.title,
            'description': course.description,
            'category_id': course.category_id,
            'difficulty_level': course.difficulty_level,
            'price': course.price,
            'published_at': course.published_at.isoformat() if course.published_at else None
        }

        # Add additional info for authenticated users
        if user_id and user_role:
            course_data.update({
                'status': course.status,
                'visibility': course.visibility,
                'is_published': course.is_published,
                'creator_id': course.creator_id
            })

        return jsonify({
            'success': True,
            'data': course_data
        }), 200

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
                'code': 'INVALID_UUID',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_COURSE_ERROR',
                'message': str(e)
            }
        }), 500


# Note: Enrolled courses endpoint will be implemented when enrollment domain is ready
# @learner_courses_bp.route('/my/courses', methods=['GET'])
# @require_auth
# def get_enrolled_courses():
#     """Get user's enrolled courses."""
#     pass
