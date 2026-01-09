"""
Course Write Operations (POST/PUT/DELETE Endpoints)

Endpoints:
- POST   /courses - Create course (creator)
- PUT    /courses/:id - Update course
- DELETE /courses/:id - Archive course
- POST   /courses/:id/publish - Publish course
- POST   /courses/:id/unpublish - Unpublish course
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.course import CourseCreate, CourseUpdate
from app.repositories.courses import CourseRepository
from app.middleware.auth import token_required, role_required, get_current_user

# Blueprint for this module
courses_bp = Blueprint(
    'courses_crud',
    __name__,
    url_prefix='/courses'
)


@courses_bp.route('', methods=['POST'])
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
        return jsonify({
            'success': False,
            'error': 'Course creation failed',
            'details': str(e)
        }), 500


@courses_bp.route('/<course_id>', methods=['PUT'])
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
            user.get('organization_id') == course.get('organization_id')
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


@courses_bp.route('/<course_id>', methods=['DELETE'])
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


@courses_bp.route('/<course_id>/publish', methods=['POST'])
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


@courses_bp.route('/<course_id>/unpublish', methods=['POST'])
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
