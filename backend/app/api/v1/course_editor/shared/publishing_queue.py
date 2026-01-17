"""
Admin Course Publishing Queue & Dashboard

Publishing queue and dashboard for course listing:
- Review queue: List of submitted courses awaiting moderation
- Published courses: List of published courses by visibility level

Endpoints:
- GET /api/v1/admin/publishing/queue - Get review queue
- GET /api/v1/admin/publishing/published - Get published courses

Phase: AI Editor Implementation - Publishing System
"""

import logging

from flask import jsonify, request

from app.api.v1 import api_v1
from app.database import get_connection
from app.repositories.course_publishing import CoursePublishingRepository
from app.security.permissions import Permissions, require_permission

logger = logging.getLogger(__name__)

VALID_VISIBILITIES = ['private', 'community', 'public']


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
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))

        with get_connection() as conn:
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
    """
    try:
        visibility = request.args.get('visibility', 'community')
        limit = min(int(request.args.get('limit', 100)), 500)
        offset = int(request.args.get('offset', 0))

        # Validate visibility
        if visibility not in VALID_VISIBILITIES:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_VISIBILITY',
                    'message': 'error.invalid_visibility'
                }
            }), 400

        with get_connection() as conn:
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
