"""
Admin Course Publishing Decisions - Approve & Reject

Moderation decision endpoints for course publishing workflow:
- Approve: Moderator approves course for publishing (with AI score)
- Reject: Moderator rejects with feedback (with AI score)

Endpoints:
- POST /api/v1/admin/courses/{course_id}/publishing/approve - Approve course
- POST /api/v1/admin/courses/{course_id}/publishing/reject - Reject course

Phase: AI Editor Implementation - Publishing System
"""

import logging
from decimal import Decimal

from flask import jsonify, request

from app.api.v1 import api_v1
from app.database import get_connection
from app.middleware.auth import get_current_user
from app.repositories.course_publishing import CoursePublishingRepository
from app.repositories.courses import CourseRepository
from app.repositories.moderation_audit import ModerationAuditRepository
from app.security.permissions import Permissions, require_permission
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


@api_v1.route('/admin/courses/<course_id>/publishing/approve', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_approve_course(course_id: str):
    """
    Approve course for publishing.

    Path Parameters:
        - course_id: Course ID

    Request Body:
        - moderation_notes: Optional notes (optional)
        - ai_score: AI quality score 0.0-1.0 (optional)

    Returns:
        200: {success: True, data: CoursePublishing}
        400: Course not in submitted status or invalid AI score
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

            if publishing['status'] != 'submitted':
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_STATUS',
                        'message': 'error.course_must_be_submitted'
                    }
                }), 400

            ai_score = None
            if 'ai_score' in data:
                try:
                    ai_score = Decimal(str(data['ai_score']))
                    if not (0.0 <= float(ai_score) <= 1.0):
                        return jsonify({
                            'success': False,
                            'error': {
                                'code': 'INVALID_AI_SCORE',
                                'message': 'error.ai_score_range'
                            }
                        }), 400
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'INVALID_AI_SCORE',
                            'message': 'error.ai_score_invalid'
                        }
                    }), 400

            publishing_repo.update_status(
                course_id,
                'approved',
                moderator_id=current_user['user_id'],
                moderation_notes=data.get('moderation_notes'),
                moderation_ai_score=ai_score
            )

            final_publishing = publishing_repo.update_status(
                course_id,
                'published',
                moderator_id=current_user['user_id'],
                moderation_notes=data.get('moderation_notes'),
                moderation_ai_score=ai_score
            )

            audit_repo.create(
                course_id=course_id,
                action='approved',
                moderator_id=current_user['user_id'],
                notes=data.get('moderation_notes')
            )

            AuditService.log_action(
                user_id=current_user['user_id'],
                action='admin.publishing.approve',
                resource_type='course_publishing',
                resource_id=course_id,
                details={
                    'course_id': course_id,
                    'course_title': course['title'],
                    'moderator_id': current_user['user_id'],
                    'moderation_notes': data.get('moderation_notes'),
                    'ai_score': float(ai_score) if ai_score else None
                },
                severity='info'
            )

            return jsonify({'success': True, 'data': final_publishing}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_approve_course: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_approve_course'
            }
        }), 500


@api_v1.route('/admin/courses/<course_id>/publishing/reject', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_reject_course(course_id: str):
    """
    Reject course submission.

    Path Parameters:
        - course_id: Course ID

    Request Body:
        - rejection_reason: Reason for rejection (required)
        - ai_score: AI quality score 0.0-1.0 (optional)

    Returns:
        200: {success: True, data: CoursePublishing}
        400: Missing reason or course not in submitted status
        404: Course or publishing record not found
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        if not data.get('rejection_reason'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_REASON',
                    'message': 'error.rejection_reason_required'
                }
            }), 400

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

            if publishing['status'] != 'submitted':
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_STATUS',
                        'message': 'error.course_must_be_submitted'
                    }
                }), 400

            ai_score = None
            if 'ai_score' in data:
                try:
                    ai_score = Decimal(str(data['ai_score']))
                    if not (0.0 <= float(ai_score) <= 1.0):
                        return jsonify({
                            'success': False,
                            'error': {
                                'code': 'INVALID_AI_SCORE',
                                'message': 'error.ai_score_range'
                            }
                        }), 400
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'INVALID_AI_SCORE',
                            'message': 'error.ai_score_invalid'
                        }
                    }), 400

            updated_publishing = publishing_repo.update_status(
                course_id,
                'rejected',
                moderator_id=current_user['user_id'],
                moderation_notes=data.get('rejection_reason'),
                moderation_ai_score=ai_score
            )

            audit_repo.create(
                course_id=course_id,
                action='rejected',
                moderator_id=current_user['user_id'],
                notes=data.get('rejection_reason')
            )

            AuditService.log_action(
                user_id=current_user['user_id'],
                action='admin.publishing.reject',
                resource_type='course_publishing',
                resource_id=course_id,
                details={
                    'course_id': course_id,
                    'course_title': course['title'],
                    'moderator_id': current_user['user_id'],
                    'rejection_reason': data.get('rejection_reason'),
                    'ai_score': float(ai_score) if ai_score else None
                },
                severity='warning'
            )

            return jsonify({'success': True, 'data': updated_publishing}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_reject_course: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_reject_course'
            }
        }), 500
