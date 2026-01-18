"""
LernsystemX Courses API - CRUD Write Operations

User course creation, updates, and archival.

Write Operations:
- POST /courses - Create course (creators+)
- PUT /courses/:id - Update course
- DELETE /courses/:id - Archive course

All routes: /api/v1/courses/*
ISO 9001:2015 compliant - Course Management Layer
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import logging

from app.domain.models.course import CourseCreate, CourseUpdate
from app.repositories.courses import CourseRepository
from app.middleware.auth import token_required, role_required, get_current_user
from app.i18n.error_codes import ErrorCode
from app.i18n.error_codes import error_response

logger = logging.getLogger(__name__)

crud_bp = Blueprint('courses_crud', __name__, url_prefix='/courses')

__all__ = ['crud_bp']


# =============================================================================
# COURSE CRUD - WRITE OPERATIONS
# =============================================================================

@crud_bp.route('', methods=['POST'])
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
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})

    except Exception as e:
        logger.error(f"Error creating course: {e}")
        return error_response(ErrorCode.COURSE_CREATE_FAILED, 500, details={'details': str(e)})


@crud_bp.route('/<course_id>', methods=['PUT'])
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
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

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
            return error_response(ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS, 403, details={'message': 'You can only update your own courses'})

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
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})

    except Exception as e:
        logger.error(f"Error updating course: {e}")
        return error_response(ErrorCode.COURSE_UPDATE_FAILED, 500, details={'details': str(e)})


@crud_bp.route('/<course_id>', methods=['DELETE'])
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
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        # Check permissions (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        is_creator = user['user_id'] == course['creator_id']
        is_admin = PermissionService.check_threshold(user, 'courses.edit_any')

        if not (is_creator or is_admin):
            return error_response(ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS, 403, details={'message': 'You can only archive your own courses'})

        # Archive course
        CourseRepository.archive(course_id)

        return jsonify({
            'success': True,
            'message': 'Course archived successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error archiving course: {e}")
        return error_response(ErrorCode.COURSE_ARCHIVE_FAILED, 500, details={'details': str(e)})
