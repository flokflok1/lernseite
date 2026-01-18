"""
Admin Course CRUD Endpoints

Endpoints:
- GET    /api/v1/admin/courses - List all courses
- GET    /api/v1/admin/courses/{id} - Get course details
- POST   /api/v1/admin/courses - Create course
- PATCH  /api/v1/admin/courses/{id} - Update course
- POST   /api/v1/admin/courses/{id}/status - Change status
- DELETE /api/v1/admin/courses/{id} - Archive course
- DELETE /api/v1/admin/courses/{id}/permanent - Hard delete
"""

from flask import request, jsonify, g
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

from app.api.v1 import api_v1
from app.domain.models.admin_course import (
    AdminCourseCreateRequest,
    AdminCourseUpdateRequest,
    AdminCourseStatusUpdateRequest
)
from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.services.audit_service import AuditService
from app.api.middleware.auth import get_current_user
from app.infrastructure.security.permissions import require_permission, Permissions


@api_v1.route('/admin/courses', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_list_courses():
    """List all courses with advanced filtering and pagination."""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        status = request.args.get('status', 'all')
        search = request.args.get('search')
        creator_id = request.args.get('creator_id')
        organization_id = request.args.get('organization_id')
        category = request.args.get('category')
        category_id = request.args.get('category_id')
        level = request.args.get('level')
        language = request.args.get('language')
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        result = CourseRepository.admin_list_courses(
            page=page,
            per_page=per_page,
            status=status,
            search=search,
            creator_id=int(creator_id) if creator_id else None,
            organization_id=int(organization_id) if organization_id else None,
            category=category,
            category_id=int(category_id) if category_id else None,
            level=level,
            language=language,
            sort=sort,
            order=order
        )

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.courses.list',
            resource_type='course',
            details={'filters': {'status': status, 'search': search}}
        )

        return jsonify({
            'success': True,
            'courses': result['courses'],
            'pagination': result['pagination']
        }), 200

    except ValueError as e:
        return jsonify({'success': False, 'error': 'Invalid parameter', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"ERROR in admin_list_courses: {e}")
        return jsonify({'success': False, 'error': 'Failed to list courses', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_course_details(course_id: str):
    """Get detailed information about a specific course."""
    try:
        course_details = CourseRepository.admin_get_course_by_id(course_id)

        if not course_details:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.courses.view',
            resource_type='course',
            resource_id=str(course_id)
        )

        return jsonify({'success': True, 'course': course_details}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_get_course_details: {e}")
        return jsonify({'success': False, 'error': 'Failed to get course details', 'details': str(e)}), 500


@api_v1.route('/admin/courses', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_create_course():
    """Create a new course as admin."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        course_request = AdminCourseCreateRequest(**data)

        new_course = CourseRepository.admin_create_course(
            course_data=course_request.model_dump(exclude_none=True),
            created_by_admin=current_user['user_id']
        )

        if not new_course:
            return jsonify({'success': False, 'error': 'Failed to create course'}), 500

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.courses.create',
            resource_type='course',
            resource_id=str(new_course['course_id']),
            details={'title': new_course['title']},
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': 'Course created successfully',
            'course': new_course
        }), 201

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"ERROR in admin_create_course: {e}")
        return jsonify({'success': False, 'error': 'Failed to create course', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_update_course(course_id: str):
    """Update course metadata."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        update_request = AdminCourseUpdateRequest(**data)

        existing_course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not existing_course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        updated_course = CourseRepository.admin_update_course(
            course_id=course_id,
            update_data=update_request.model_dump(exclude_none=True),
            updated_by_admin=current_user['user_id']
        )

        if not updated_course:
            return jsonify({'success': False, 'error': 'Failed to update course'}), 500

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.courses.update',
            resource_type='course',
            resource_id=str(course_id),
            details={'updated_fields': list(update_request.model_dump(exclude_none=True).keys())},
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': 'Course updated successfully',
            'course': updated_course
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"ERROR in admin_update_course: {e}")
        return jsonify({'success': False, 'error': 'Failed to update course', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>/status', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_update_course_status(course_id: str):
    """Change course status (publish, unpublish, archive, unarchive)."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        status_request = AdminCourseStatusUpdateRequest(**data)

        existing_course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not existing_course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        result = None
        new_status = None

        if status_request.action == 'publish':
            result = CourseRepository.publish(course_id)
            new_status = 'published'
        elif status_request.action == 'unpublish':
            result = CourseRepository.unpublish(course_id)
            new_status = 'draft'
        elif status_request.action == 'archive':
            result = CourseRepository.archive(course_id)
            new_status = 'archived'
        elif status_request.action == 'unarchive':
            result = CourseRepository.unarchive(course_id)
            new_status = 'draft'
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid action',
                'message': 'Action must be: publish, unpublish, archive, unarchive'
            }), 400

        if not result:
            return jsonify({'success': False, 'error': 'Failed to change course status'}), 400

        AuditService.log_action(
            user_id=current_user['user_id'],
            action=f'admin.courses.{status_request.action}',
            resource_type='course',
            resource_id=str(course_id),
            details={'action': status_request.action, 'reason': status_request.reason},
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': f'Course {status_request.action}ed successfully',
            'status': new_status
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"ERROR in admin_update_course_status: {e}")
        return jsonify({'success': False, 'error': 'Failed to change status', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_DELETE)
def admin_delete_course(course_id: str):
    """Archive a course (soft delete)."""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        reason = data.get('reason', 'Deleted by admin')

        existing_course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not existing_course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        result = CourseRepository.archive(course_id)

        if not result:
            return jsonify({'success': False, 'error': 'Failed to archive course'}), 500

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.courses.delete',
            resource_type='course',
            resource_id=str(course_id),
            details={'reason': reason, 'course_title': existing_course['title']},
            severity='critical'
        )

        return jsonify({'success': True, 'message': 'Course archived successfully'}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_delete_course: {e}")
        return jsonify({'success': False, 'error': 'Failed to archive course', 'details': str(e)}), 500


@api_v1.route('/admin/courses/<course_id>/permanent', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_DELETE)
def admin_permanent_delete_course(course_id: str):
    """Permanently delete a course (hard delete). WARNING: Cannot be undone!"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        if not data.get('confirm', False):
            return jsonify({
                'success': False,
                'error': 'Confirmation required',
                'message': 'Set "confirm": true to permanently delete'
            }), 400

        reason = data.get('reason', 'Permanently deleted by admin')

        existing_course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not existing_course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        course_title = existing_course['title']
        result = CourseRepository.delete(course_id)

        if not result:
            return jsonify({'success': False, 'error': 'Failed to permanently delete'}), 500

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.courses.permanent_delete',
            resource_type='course',
            resource_id=str(course_id),
            details={'reason': reason, 'course_title': course_title, 'permanent': True},
            severity='critical'
        )

        return jsonify({'success': True, 'message': 'Course permanently deleted'}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_permanent_delete_course: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete', 'details': str(e)}), 500
