"""
Admin Course Publishing Workflow API

Course publishing workflow:
- draft: Course created, not yet submitted
- submitted: User submitted for community review
- approved: Moderator approved for publishing
- rejected: Moderator rejected (needs revision)
- published: Course is published and available

Visibility levels:
- private: Only owner can see
- community: Visible in community (requires published status)
- public: Public listing (future feature)

Endpoints:
- GET    /api/v1/admin/courses/{course_id}/publishing - Get publishing status
- POST   /api/v1/admin/courses/{course_id}/publishing/submit - Submit for review
- POST   /api/v1/admin/courses/{course_id}/publishing/approve - Admin approve
- POST   /api/v1/admin/courses/{course_id}/publishing/reject - Admin reject
- PATCH  /api/v1/admin/courses/{course_id}/publishing/visibility - Change
- GET    /api/v1/admin/publishing/queue - List courses for moderation
- GET    /api/v1/admin/publishing/published - List published courses

Phase: AI Studio Implementation - Publishing System
"""

import logging
from decimal import Decimal

from flask import jsonify, request

from app.api.v1 import api_v1
from app.database import get_connection
from app.middleware.auth import get_current_user
from app.models.course_publishing import (
    CoursePublishingResponse,
    CoursePublishingStateChange,
)
from app.repositories.course_publishing import CoursePublishingRepository
from app.repositories.courses import CourseRepository
from app.repositories.moderation_audit import ModerationAuditRepository
from app.security.permissions import Permissions, require_permission
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


# ============================================================================
# Publishing Status & Management
# ============================================================================

@api_v1.route('/admin/courses/<course_id>/publishing', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_publishing_status(course_id: str):
    """
    Get publishing status for a course.

    Path Parameters:
        - course_id: Course ID

    Returns:
        200: {success: True, data: CoursePublishing}
        404: Course or publishing record not found

    Example:
        GET /admin/courses/uuid-1/publishing
        Response:
            {
                "success": true,
                "data": {
                    "course_id": "uuid-1",
                    "status": "published",
                    "visibility": "community"
                }
            }
    """
    try:
        with get_db_connection() as conn:
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
@require_permission(Permissions.ADMIN_COURSE_WRITE)
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

    Example:
        POST /admin/courses/uuid-1/publishing/submit
        Body: {"submission_notes": "Ready for review"}
        Response: {success: True, data: {...}}
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        with get_db_connection() as conn:
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

    Example:
        POST /admin/courses/uuid-1/publishing/approve
        Body: {"moderation_notes": "Excellent content", "ai_score": 0.95}
        Response: {success: True, data: {...}}
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        with get_db_connection() as conn:
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

    Example:
        POST /admin/courses/uuid-1/publishing/reject
        Body: {"rejection_reason": "Missing learning methods", "ai_score": 0.35}
        Response: {success: True, data: {...}}
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

        with get_db_connection() as conn:
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

    Example:
        PATCH /admin/courses/uuid-1/publishing/visibility
        Body: {"visibility": "community"}
        Response: {success: True, data: {...}}
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

        valid_visibilities = ['private', 'community', 'public']
        if data['visibility'] not in valid_visibilities:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_VISIBILITY',
                    'message': 'error.invalid_visibility'
                }
            }), 400

        with get_db_connection() as conn:
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


# ============================================================================
# Publishing Queue & Dashboard
# ============================================================================

@api_v1.route('/admin/publishing/queue', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_get_review_queue():
    """
    Get submitted courses awaiting review (moderation queue).

    Query Parameters:
        - limit: Max results (default 50, max 500)
        - offset: Skip N records (default 0)

    Returns:
        200: {success: True, data: CoursePublishing[], total: int}

    Example:
        GET /admin/publishing/queue?limit=50&offset=0
        Response:
            {
                "success": true,
                "data": [{...}, {...}],
                "total": 150,
                "limit": 50,
                "offset": 0
            }
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))

        with get_db_connection() as conn:
            publishing_repo = CoursePublishingRepository(conn)

            submitted = publishing_repo.list_submitted(
                limit=limit,
                offset=offset
            )
            total = publishing_repo.count_by_status('submitted')

        return jsonify({
            'success': True,
            'data': submitted,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        logger.error(f"ERROR in admin_get_review_queue: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_load_review_queue'
            }
        }), 500


@api_v1.route('/admin/publishing/published', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_published_courses():
    """
    Get published courses in community.

    Query Parameters:
        - visibility: Filter by visibility (default community)
        - limit: Max results (default 100, max 500)
        - offset: Skip N records (default 0)

    Returns:
        200: {success: True, data: CoursePublishing[], total: int}
        400: Invalid visibility value

    Example:
        GET /admin/publishing/published?visibility=community&limit=100&offset=0
        Response:
            {
                "success": true,
                "data": [{...}, {...}],
                "total": 350,
                "visibility": "community",
                "limit": 100,
                "offset": 0
            }
    """
    try:
        visibility = request.args.get('visibility', 'community')
        limit = min(int(request.args.get('limit', 100)), 500)
        offset = int(request.args.get('offset', 0))

        # Validate visibility
        valid_visibilities = ['private', 'community', 'public']
        if visibility not in valid_visibilities:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_VISIBILITY',
                    'message': 'error.invalid_visibility'
                }
            }), 400

        with get_db_connection() as conn:
            publishing_repo = CoursePublishingRepository(conn)

            # Get published courses
            published = publishing_repo.list_published(
                visibility=visibility,
                limit=limit,
                offset=offset
            )
            # Count only published courses with matching visibility
            total = sum(
                1 for p in publishing_repo.list_by_status('published')
                if p['visibility'] == visibility
            )

        return jsonify({
            'success': True,
            'data': published,
            'total': total,
            'visibility': visibility,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        logger.error(f"ERROR in admin_get_published_courses: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_load_published_courses'
            }
        }), 500
