"""
Admin Course Publishing Workflow - Status & Submission

Core publishing workflow management:
- draft: Course created, not yet submitted
- submitted: User submitted for community review
- approved: Moderator approved for publishing
- rejected: Moderator rejected (needs revision)
- published: Course is published and available

Endpoints:
- GET    /api/v1/admin/courses/{course_id}/publishing - Get publishing status
- POST   /api/v1/admin/courses/{course_id}/publishing/submit - Submit for review

Phase: AI Editor Implementation - Publishing System
"""

import logging
from flask import jsonify, request

from app.api.v1 import api_v1
from app.infrastructure.persistence.database import get_connection
from app.api.middleware.auth import get_current_user, permission_required
from app.infrastructure.persistence.repositories.content.publishing import CoursePublishingRepository
from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.infrastructure.persistence.repositories.audit.moderation_audit import ModerationAuditRepository
from app.application.services.system.audit.service import AuditService

logger = logging.getLogger(__name__)


@api_v1.route('/admin/courses/<course_id>/publishing', methods=['GET'])
@permission_required('content.courses:read')
def admin_get_publishing_status(course_id: str):
    """
    Get publishing status for a course.

    Path Parameters:
        - course_id: Course ID

    Returns:
        200: {success: True, data: CoursePublishing}
        404: Course or publishing record not found
    """
    try:
        with get_connection() as conn:
            course_repo = CourseRepository(conn)
            course = course_repo.find_by_id(course_id)

            if not course:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'COURSE_NOT_FOUND',
                        'message': 'error.course_not_found'
                    }
                }), 404

            publishing_repo = CoursePublishingRepository(conn)
            publishing = publishing_repo.get_by_course(course_id)

        if not publishing:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PUBLISHING_RECORD_NOT_FOUND',
                    'message': 'error.publishing_record_not_found'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': publishing
        }), 200

    except Exception as e:
        logger.error(f"ERROR in admin_get_publishing_status: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_get_publishing_status'
            }
        }), 500


@api_v1.route('/admin/courses/<course_id>/publishing/submit', methods=['POST'])
@permission_required('content.courses:write')
def admin_submit_for_review(course_id: str):
    """
    Submit course for community review.

    Path Parameters:
        - course_id: Course ID

    Request Body:
        - submission_notes: Optional notes for moderators (optional)

    Returns:
        200: {success: True, data: CoursePublishing}
        400: Course not in draft status or validation error
        404: Course or publishing record not found
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        with get_connection() as conn:
            course_repo = CourseRepository(conn)
            publishing_repo = CoursePublishingRepository(conn)
            audit_repo = ModerationAuditRepository(conn)

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

            if publishing['status'] != 'draft':
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_STATUS',
                        'message': 'error.course_must_be_draft'
                    }
                }), 400

            updated_publishing = publishing_repo.update_status(
                course_id,
                'submitted',
                moderator_id=None,
                moderation_notes=data.get('submission_notes')
            )

            audit_repo.create(
                course_id=course_id,
                action='submitted',
                moderator_id=None,
                notes=data.get('submission_notes')
            )

            AuditService.log_action(
                user_id=current_user['user_id'],
                action='admin.publishing.submit',
                resource_type='course_publishing',
                resource_id=course_id,
                details={
                    'course_id': course_id,
                    'course_title': course['title'],
                    'submission_notes': data.get('submission_notes')
                },
                severity='info'
            )

            return jsonify({'success': True, 'data': updated_publishing}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_submit_for_review: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_submit_course'
            }
        }), 500
