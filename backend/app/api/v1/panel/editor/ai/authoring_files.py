"""
Authoring Files API — File upload/list/delete/content for AI authoring sessions.

All endpoints require authentication via check_course_permission + session
ownership verification. Business logic delegated to AuthoringFileService
(Application Layer).

Routes:
  POST   /authoring/sessions/<session_id>/files          — Upload file
  GET    /authoring/sessions/<session_id>/files           — List files
  DELETE /authoring/sessions/<session_id>/files/<file_id> — Delete file
  GET    /authoring/sessions/<session_id>/files/<file_id>/content — Get extracted text
"""

from typing import Optional, Tuple
from flask import Blueprint, request, jsonify, g
import logging

from app.api.v1.panel.editor.shared.permissions import check_course_permission
from app.core.bootstrap.extensions import limiter
from app.infrastructure.persistence.repositories.authoring.sessions.sessions import (
    CourseAuthoringSessionRepository,
)

logger = logging.getLogger(__name__)

# Roles with full access (mirrors permissions.py ADMIN_ROLES)
_ADMIN_ROLES = {'admin', 'owner', 'superadmin'}

authoring_files_bp = Blueprint(
    'authoring_files', __name__, url_prefix='/authoring'
)


def _verify_session_access(session_id: str) -> Optional[Tuple[dict, int]]:
    """
    Verify current user owns the session or is admin.

    Returns None if access is granted, or a (response, status_code) tuple
    to return immediately if access is denied.
    """
    user = g.current_user
    if user.get('role') in _ADMIN_ROLES:
        return None

    session = CourseAuthoringSessionRepository.get_session_with_course(session_id)
    if not session:
        return jsonify({
            'success': False,
            'error': 'Session not found',
        }), 404

    if str(session.get('created_by')) != str(user.get('user_id')):
        return jsonify({
            'success': False,
            'error': 'You do not have access to this session',
        }), 403

    return None


@authoring_files_bp.route(
    '/sessions/<session_id>/files', methods=['POST']
)
@check_course_permission('write')
@limiter.limit("30 per minute")
def upload_file(session_id):
    """Upload a file to an authoring session."""
    denied = _verify_session_access(session_id)
    if denied:
        return denied

    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400

    file_obj = request.files['file']
    if not file_obj.filename:
        return jsonify({
            'success': False,
            'error': 'Empty filename'
        }), 400

    try:
        from app.application.services.ai.authoring_file_service import (
            AuthoringFileService,
        )

        user_id = str(g.current_user.get('user_id', ''))
        result = AuthoringFileService.upload_file(
            session_id=session_id,
            file_obj=file_obj,
            filename=file_obj.filename,
            user_id=user_id,
        )

        return jsonify({
            'success': True,
            'data': result,
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 400

    except Exception as e:
        logger.error(f"File upload failed: {e}")
        return jsonify({
            'success': False,
            'error': 'File upload failed',
        }), 500


@authoring_files_bp.route(
    '/sessions/<session_id>/files', methods=['GET']
)
@check_course_permission('read')
def list_files(session_id):
    """List all files for an authoring session."""
    denied = _verify_session_access(session_id)
    if denied:
        return denied

    try:
        from app.application.services.ai.authoring_file_service import (
            AuthoringFileService,
        )

        files = AuthoringFileService.list_files(session_id)
        return jsonify({
            'success': True,
            'data': {'files': files},
        })

    except Exception as e:
        logger.error(f"File listing failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list files',
        }), 500


@authoring_files_bp.route(
    '/sessions/<session_id>/files/<file_id>', methods=['DELETE']
)
@check_course_permission('write')
def delete_file(session_id, file_id):
    """Delete a file from an authoring session."""
    denied = _verify_session_access(session_id)
    if denied:
        return denied

    try:
        from app.application.services.ai.authoring_file_service import (
            AuthoringFileService,
        )

        success = AuthoringFileService.delete_file(session_id, file_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'File not found or access denied',
            }), 404

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete file',
        }), 500


@authoring_files_bp.route(
    '/sessions/<session_id>/files/<file_id>/content', methods=['GET']
)
@check_course_permission('read')
def get_file_content(session_id, file_id):
    """Get extracted text content for a file."""
    denied = _verify_session_access(session_id)
    if denied:
        return denied

    try:
        from app.application.services.ai.authoring_file_service import (
            AuthoringFileService,
        )

        result = AuthoringFileService.get_extracted_content(
            session_id, file_id
        )
        if not result:
            return jsonify({
                'success': False,
                'error': 'File not found or access denied',
            }), 404

        return jsonify({
            'success': True,
            'data': result,
        })

    except Exception as e:
        logger.error(f"Get file content failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get file content',
        }), 500
