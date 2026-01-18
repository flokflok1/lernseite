"""
LernsystemX Courses API - Publishing & Statistics

Course publishing status management and course statistics.

Publishing & Statistics Operations:
- POST /courses/:id/publish - Publish course
- POST /courses/:id/unpublish - Unpublish course
- GET /courses/:id/stats - Get course statistics

All routes: /api/v1/courses/*
ISO 9001:2015 compliant - Course Management Layer
"""

from flask import Blueprint, request, jsonify
import logging

from app.repositories.courses import CourseRepository
from app.middleware.auth import token_required, get_current_user
from app.i18n.error_codes import ErrorCode
from app.i18n.error_codes import error_response

logger = logging.getLogger(__name__)

publishing_bp = Blueprint('courses_publishing', __name__, url_prefix='/courses')

__all__ = ['publishing_bp']


# =============================================================================
# COURSE PUBLISHING & STATISTICS
# =============================================================================

@publishing_bp.route('/<course_id>/publish', methods=['POST'])
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
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        # Check permissions (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        is_creator = user['user_id'] == course['creator_id']
        is_admin = PermissionService.check_threshold(user, 'courses.edit_any')

        if not (is_creator or is_admin):
            return error_response(ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS, 403)

        # Publish course
        published_course = CourseRepository.publish(course_id)

        if not published_course:
            return error_response(ErrorCode.COURSE_PUBLISH_FAILED, 400, details={'message': 'Course already published or cannot be published'})

        return jsonify({
            'success': True,
            'message': 'Course published successfully',
            'course': published_course
        }), 200

    except Exception as e:
        logger.error(f"Error publishing course: {e}")
        return error_response(ErrorCode.COURSE_PUBLISH_FAILED, 500, details={'details': str(e)})


@publishing_bp.route('/<course_id>/unpublish', methods=['POST'])
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
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        # Check permissions (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        is_creator = user['user_id'] == course['creator_id']
        is_admin = PermissionService.check_threshold(user, 'courses.edit_any')

        if not (is_creator or is_admin):
            return error_response(ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS, 403)

        # Unpublish course
        unpublished_course = CourseRepository.unpublish(course_id)

        return jsonify({
            'success': True,
            'message': 'Course unpublished successfully',
            'course': unpublished_course
        }), 200

    except Exception as e:
        logger.error(f"Error unpublishing course: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@publishing_bp.route('/<course_id>/stats', methods=['GET'])
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
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        # Check permissions (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        is_creator = user['user_id'] == course['creator_id']
        is_admin = PermissionService.check_threshold(user, 'courses.edit_any')

        if not (is_creator or is_admin):
            return error_response(ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS, 403, details={'message': 'You can only view stats for your own courses'})

        # Get statistics
        stats = CourseRepository.get_statistics(course_id)

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting course stats: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})
