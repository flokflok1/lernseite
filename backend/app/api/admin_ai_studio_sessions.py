"""
LernsystemX Admin AI Studio - Session Management API

Session CRUD endpoints for KI-Authoring-Studio:
- GET    /api/v1/admin/ai-studio/sessions         - List user's sessions
- POST   /api/v1/admin/ai-studio/sessions         - Create new session
- GET    /api/v1/admin/ai-studio/sessions/{id}    - Get session details
- PATCH  /api/v1/admin/ai-studio/sessions/{id}    - Update session
- DELETE /api/v1/admin/ai-studio/sessions/{id}    - Delete session

Phase D4 - KI-Authoring-Studio - ISO 27001:2013 compliant
Module split according to 35_Developer-Guide-KI-Prompts.md guidelines
"""

from flask import request, jsonify, g
from pydantic import ValidationError
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.extensions import limiter
from app.models.ai_studio import (
    AIStudioSessionCreateRequest,
    AIStudioSessionUpdateRequest,
    AIStudioSessionListItem,
    SessionStatus
)
from app.repositories.ai_studio_repository import (
    AIStudioRepository,
    AIStudioAnalyticsRepository,
    AIAuthoringTemplateRepository
)
from app.repositories.course_repository import CourseRepository
from app.services.audit_service import AuditService
from app.security.permissions import require_permission, Permissions


# ============================================================================
# Session CRUD Operations
# ============================================================================

@api_v1.route('/admin/ai-studio/sessions', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def list_ai_studio_sessions():
    """
    List user's AI authoring sessions

    Query Parameters:
        status: Filter by status (draft, in_progress, review, completed, cancelled)
        limit: Max results (default 20)

    Response 200:
        {
            "success": true,
            "sessions": [...]
        }
    """
    try:
        user_id = g.current_user['user_id']
        status = request.args.get('status')
        limit = int(request.args.get('limit', 20))

        sessions = AIStudioRepository.find_by_user(user_id, limit=limit, status=status)

        return jsonify({
            'success': True,
            'sessions': [AIStudioSessionListItem(**s).model_dump() for s in sessions]
        }), 200

    except Exception as e:
        logger.error(f"Error listing AI studio sessions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to list sessions',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def create_ai_studio_session():
    """
    Create new AI authoring session

    Request Body:
        {
            "course_id": "uuid",
            "session_name": "Kapitel 1",
            "source_type": "pdf",
            "template_key": "standard_chapter"
        }

    Response 201:
        {
            "success": true,
            "session": {...}
        }
    """
    try:
        data = request.get_json()
        req = AIStudioSessionCreateRequest(**data)

        # Verify course access
        course = CourseRepository.find_by_id(req.course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        user_id = g.current_user['user_id']

        # Get template config if specified
        template_config = None
        if req.template_key:
            template = AIAuthoringTemplateRepository.get_by_key(req.template_key)
            if template:
                template_config = template.get('template_config', {})

        session_data = {
            'user_id': user_id,
            'course_id': req.course_id,
            'session_name': req.session_name or f"Neue Session - {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            'source_type': req.source_type.value,
            'chapter_id': req.chapter_id
        }

        if template_config:
            session_data['ai_config'] = template_config.get('ai_settings', {})

        session = AIStudioRepository.create_session(session_data)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Failed to create session'
            }), 500

        # Log analytics
        AIStudioAnalyticsRepository.log_event({
            'session_id': session['session_id'],
            'user_id': user_id,
            'event_type': 'session_created',
            'event_data': {'source_type': req.source_type.value, 'template_key': req.template_key}
        })

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='ai_studio_session_created',
            resource_type='ai_authoring_session',
            resource_id=session['session_id'],
            details={'course_id': req.course_id}
        )

        return jsonify({
            'success': True,
            'session': session
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        logger.error(f"Error creating AI studio session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create session',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def get_ai_studio_session(session_id: str):
    """
    Get session details

    Response 200:
        {
            "success": true,
            "session": {...}
        }
    """
    try:
        session = AIStudioRepository.find_by_id(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        # Verify ownership
        user_id = g.current_user['user_id']
        if session['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        return jsonify({
            'success': True,
            'session': session
        }), 200

    except Exception as e:
        logger.error(f"Error getting AI studio session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get session',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def update_ai_studio_session(session_id: str):
    """
    Update session

    Request Body:
        {
            "session_name": "Updated name",
            "status": "in_progress",
            "current_step": "theory_generation"
        }
    """
    try:
        session = AIStudioRepository.find_by_id(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        # Verify ownership
        user_id = g.current_user['user_id']
        if session['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json()
        req = AIStudioSessionUpdateRequest(**data)

        update_data = {}
        if req.session_name:
            update_data['session_name'] = req.session_name
        if req.status:
            update_data['status'] = req.status.value
        if req.current_step:
            update_data['current_step'] = req.current_step.value
        if req.ai_config:
            update_data['ai_config'] = req.ai_config

        if not update_data:
            return jsonify({
                'success': False,
                'error': 'No update data provided'
            }), 400

        updated = AIStudioRepository.update_session(session_id, update_data)

        return jsonify({
            'success': True,
            'session': updated
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        logger.error(f"Error updating AI studio session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update session',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def delete_ai_studio_session(session_id: str):
    """Delete session"""
    try:
        session = AIStudioRepository.find_by_id(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        # Verify ownership
        user_id = g.current_user['user_id']
        if session['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        AIStudioRepository.delete_session(session_id)

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='ai_studio_session_deleted',
            resource_type='ai_authoring_session',
            resource_id=session_id
        )

        return jsonify({
            'success': True,
            'message': 'Session deleted'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting AI studio session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete session',
            'message': str(e)
        }), 500
