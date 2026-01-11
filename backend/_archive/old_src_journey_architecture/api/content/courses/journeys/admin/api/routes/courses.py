"""
Admin Course Routes (Journey-Based API)

Admin journey for course management.
ALL data loaded dynamically from database - NO hardcoded values.

Endpoints:
- GET /api/v1/admin/courses - List all courses (with filters from DB)
- GET /api/v1/admin/courses/<id> - Get course details
- POST /api/v1/admin/courses - Create new course
- PUT /api/v1/admin/courses/<id> - Update course
- POST /api/v1/admin/courses/<id>/publish - Publish course
- POST /api/v1/admin/courses/<id>/archive - Archive course
- DELETE /api/v1/admin/courses/<id> - Delete course (soft delete)
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
from src.core.auth.permissions import require_auth, require_role
from src.api.content.courses.core.application.services.course_service import CourseService
from src.core.utils.validators import Validators, ValidationError


# Create blueprint
admin_courses_bp = Blueprint('admin_courses', __name__, url_prefix='/api/v1/admin/courses')


@admin_courses_bp.route('', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator'])
def list_courses():
    """
    List all courses with dynamic filters.

    Query params (all optional, loaded from DB):
    - status: Filter by status (from DB enum)
    - visibility: Filter by visibility (from DB enum)
    - category_id: Filter by category (from DB)
    - creator_id: Filter by creator
    - organisation_id: Filter by organisation
    - limit: Result limit (default 100)
    - offset: Result offset (default 0)

    Returns:
        200: List of courses with metadata
        500: Server error
    """
    try:
        # Get user info from auth context
        user_id = request.user_id
        user_role = request.user_role
        user_org_id = getattr(request, 'user_org_id', None)

        # Get query parameters - all dynamic from DB
        filters = {
            'status': request.args.get('status'),
            'visibility': request.args.get('visibility'),
            'category_id': request.args.get('category_id'),
            'creator_id': request.args.get('creator_id'),
            'organisation_id': request.args.get('organisation_id')
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}

        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        # Get courses
        courses = CourseService.list_courses(
            user_id=user_id,
            user_role=user_role,
            user_org_id=user_org_id,
            filters=filters,
            limit=limit,
            offset=offset
        )

        # Get total count
        total = CourseService.count_courses(filters=filters)

        # Convert to dict
        courses_data = [
            {
                'course_id': c.course_id,
                'title': c.title,
                'description': c.description,
                'creator_id': c.creator_id,
                'category_id': c.category_id,
                'difficulty_level': c.difficulty_level,
                'status': c.status,
                'visibility': c.visibility,
                'is_published': c.is_published,
                'is_drm_protected': c.is_drm_protected,
                'organisation_id': c.organisation_id,
                'price': c.price,
                'created_at': c.created_at.isoformat() if c.created_at else None,
                'updated_at': c.updated_at.isoformat() if c.updated_at else None,
                'published_at': c.published_at.isoformat() if c.published_at else None
            }
            for c in courses
        ]

        return jsonify({
            'success': True,
            'data': courses_data,
            'meta': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'count': len(courses_data)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'LIST_COURSES_ERROR',
                'message': str(e)
            }
        }), 500


@admin_courses_bp.route('/<course_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator'])
def get_course(course_id: str):
    """
    Get course by ID.

    Args:
        course_id: Course UUID

    Returns:
        200: Course data
        403: Permission denied
        404: Course not found
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(course_id)

        # Get user info
        user_id = request.user_id
        user_role = request.user_role

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

        # Convert to dict
        course_data = {
            'course_id': course.course_id,
            'title': course.title,
            'description': course.description,
            'creator_id': course.creator_id,
            'category_id': course.category_id,
            'difficulty_level': course.difficulty_level,
            'status': course.status,
            'visibility': course.visibility,
            'is_published': course.is_published,
            'is_drm_protected': course.is_drm_protected,
            'organisation_id': course.organisation_id,
            'price': course.price,
            'created_at': course.created_at.isoformat() if course.created_at else None,
            'updated_at': course.updated_at.isoformat() if course.updated_at else None,
            'published_at': course.published_at.isoformat() if course.published_at else None
        }

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


@admin_courses_bp.route('', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def create_course():
    """
    Create new course.

    Request body:
    - title: Course title (required)
    - category_id: Category UUID (required, must exist in DB)
    - description: Course description (optional)
    - difficulty_level: Difficulty 1-5 (optional, default 1)
    - organisation_id: Organisation UUID (optional)
    - price: Price (optional)

    Returns:
        201: Created course
        400: Validation error
        500: Server error
    """
    try:
        data = request.get_json()

        # Validate required fields
        Validators.validate_json_keys(data, ['title', 'category_id'])

        # Get user info
        user_id = request.user_id

        # Create course
        course = CourseService.create_course(
            title=data['title'],
            creator_id=user_id,
            category_id=data['category_id'],
            description=data.get('description'),
            difficulty_level=data.get('difficulty_level', 1),
            organisation_id=data.get('organisation_id'),
            price=data.get('price')
        )

        # Convert to dict
        course_data = {
            'course_id': course.course_id,
            'title': course.title,
            'description': course.description,
            'creator_id': course.creator_id,
            'category_id': course.category_id,
            'difficulty_level': course.difficulty_level,
            'status': course.status,
            'visibility': course.visibility,
            'is_published': course.is_published,
            'is_drm_protected': course.is_drm_protected,
            'organisation_id': course.organisation_id,
            'price': course.price,
            'created_at': course.created_at.isoformat() if course.created_at else None,
            'updated_at': course.updated_at.isoformat() if course.updated_at else None,
            'published_at': course.published_at.isoformat() if course.published_at else None
        }

        return jsonify({
            'success': True,
            'data': course_data
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_DATA',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATE_COURSE_ERROR',
                'message': str(e)
            }
        }), 500


@admin_courses_bp.route('/<course_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'creator'])
def update_course(course_id: str):
    """
    Update course.

    Args:
        course_id: Course UUID

    Request body (all optional):
    - title: New title
    - description: New description
    - category_id: New category (from DB)
    - difficulty_level: New difficulty
    - price: New price

    Returns:
        200: Updated course
        403: Permission denied
        404: Course not found
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(course_id)

        data = request.get_json()

        # Get user info
        user_id = request.user_id
        user_role = request.user_role

        # Update course
        course = CourseService.update_course(
            course_id=course_id,
            user_id=user_id,
            user_role=user_role,
            updates=data
        )

        # Convert to dict
        course_data = {
            'course_id': course.course_id,
            'title': course.title,
            'description': course.description,
            'creator_id': course.creator_id,
            'category_id': course.category_id,
            'difficulty_level': course.difficulty_level,
            'status': course.status,
            'visibility': course.visibility,
            'is_published': course.is_published,
            'is_drm_protected': course.is_drm_protected,
            'organisation_id': course.organisation_id,
            'price': course.price,
            'created_at': course.created_at.isoformat() if course.created_at else None,
            'updated_at': course.updated_at.isoformat() if course.updated_at else None,
            'published_at': course.published_at.isoformat() if course.published_at else None
        }

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

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'COURSE_NOT_FOUND',
                'message': str(e)
            }
        }), 404

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
                'code': 'UPDATE_COURSE_ERROR',
                'message': str(e)
            }
        }), 500


@admin_courses_bp.route('/<course_id>/publish', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def publish_course(course_id: str):
    """
    Publish course.

    Args:
        course_id: Course UUID

    Returns:
        200: Published course
        403: Permission denied
        404: Course not found
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(course_id)

        # Get user info
        user_id = request.user_id
        user_role = request.user_role

        # Publish course
        course = CourseService.publish_course(
            course_id=course_id,
            user_id=user_id,
            user_role=user_role
        )

        # Convert to dict
        course_data = {
            'course_id': course.course_id,
            'title': course.title,
            'status': course.status,
            'is_published': course.is_published,
            'published_at': course.published_at.isoformat() if course.published_at else None
        }

        return jsonify({
            'success': True,
            'data': course_data,
            'message': 'Course published successfully'
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': str(e)
            }
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'COURSE_NOT_FOUND',
                'message': str(e)
            }
        }), 404

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
                'code': 'PUBLISH_COURSE_ERROR',
                'message': str(e)
            }
        }), 500


@admin_courses_bp.route('/<course_id>/archive', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def archive_course(course_id: str):
    """
    Archive course.

    Args:
        course_id: Course UUID

    Returns:
        200: Archived course
        403: Permission denied
        404: Course not found
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(course_id)

        # Get user info
        user_id = request.user_id
        user_role = request.user_role

        # Archive course
        course = CourseService.archive_course(
            course_id=course_id,
            user_id=user_id,
            user_role=user_role
        )

        # Convert to dict
        course_data = {
            'course_id': course.course_id,
            'title': course.title,
            'status': course.status,
            'is_published': course.is_published
        }

        return jsonify({
            'success': True,
            'data': course_data,
            'message': 'Course archived successfully'
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': str(e)
            }
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'COURSE_NOT_FOUND',
                'message': str(e)
            }
        }), 404

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
                'code': 'ARCHIVE_COURSE_ERROR',
                'message': str(e)
            }
        }), 500


@admin_courses_bp.route('/<course_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_course(course_id: str):
    """
    Delete course (soft delete - archives instead).

    Args:
        course_id: Course UUID

    Returns:
        200: Deletion success
        403: Permission denied
        404: Course not found
        500: Server error
    """
    try:
        # Validate UUID
        Validators.validate_uuid(course_id)

        # Get user info
        user_id = request.user_id
        user_role = request.user_role

        # Delete course (soft delete)
        CourseService.delete_course(
            course_id=course_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'message': 'Course deleted successfully'
        }), 200

    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': str(e)
            }
        }), 403

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'COURSE_NOT_FOUND',
                'message': str(e)
            }
        }), 404

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
                'code': 'DELETE_COURSE_ERROR',
                'message': str(e)
            }
        }), 500
