"""
Admin Course Publishing Visibility Management

Visibility level management for published courses:
- private: Only owner can see
- community: Visible in community (requires published status)
- public: Public listing (future feature)

Endpoints:
- PATCH /api/v1/admin/courses/{course_id}/publishing/visibility - Update visibility

Phase: AI Editor Implementation - Publishing System
"""

import logging

from flask import jsonify, request

from app.api.v1 import api_v1
from app.infrastructure.persistence.database import get_connection
from app.api.middleware.auth import get_current_user
from app.infrastructure.persistence.repositories.course_publishing import CoursePublishingRepository
from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.infrastructure.security.permissions import Permissions, require_permission
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

VALID_VISIBILITIES = ['private', 'community', 'public']


@api_v1.route('/admin/courses/<course_id>/publishing/visibility', methods=['PATCH'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_update_visibility(course_id: str):
    """
    Update course visibility level.

    Path Parameters:
        - course_id: Course ID

    Request Body:
        - visibility: New visibility level (private, community, public)

    Returns:
        200: {success: True, data: CoursePublishing}
        400: Invalid visibility value or course not published
        404: Course or publishing record not found
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        if not data.get('visibility'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_VISIBILITY',
                    'message': 'error.visibility_required'
                }
            }), 400

        if data['visibility'] not in VALID_VISIBILITIES:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_VISIBILITY',
                    'message': 'error.invalid_visibility'
                }
            }), 400

        with get_connection() as conn:
            course_repo = CourseRepository(conn)
            publishing_repo = CoursePublishingRepository(conn)

            course = course_repo.find_by_id(course_id)
            if not course:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'COURSE_NOT_FOUND',
                        'message': 'error.course_not_found'
                    }
                }), 404

            publishing = publishing_repo.get_by_course(course_id)
            if not publishing:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'PUBLISHING_RECORD_NOT_FOUND',
                        'message': 'error.publishing_record_not_found'
                    }
                }), 404

            if publishing['status'] != 'published':
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'NOT_PUBLISHED',
                        'message': 'error.course_must_be_published'
                    }
                }), 400

            updated_publishing = publishing_repo.update_visibility(
                course_id,
                data['visibility']
            )

            AuditService.log_action(
                user_id=current_user['user_id'],
                action='admin.publishing.visibility_change',
                resource_type='course_publishing',
                resource_id=course_id,
                details={
                    'course_id': course_id,
                    'course_title': course['title'],
                    'new_visibility': data['visibility']
                },
                severity='info'
            )

            return jsonify({'success': True, 'data': updated_publishing}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_update_visibility: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_update_visibility'
            }
        }), 500
