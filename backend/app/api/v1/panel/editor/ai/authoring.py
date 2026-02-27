"""
Course Editor - AI Course Authoring

Feature-based AI course authoring with permission-aware access.
Admin: Full access to all course authoring sessions
User: Only access to authoring sessions for own courses

Chat-basiertes Kurs-Authoring mit persistenten Sessions:
- POST /api/v1/course-editor/ai/sessions - Neue Session erstellen
- GET /api/v1/course-editor/ai/sessions/<id> - Session laden
- POST /api/v1/course-editor/ai/sessions/<id>/chat - Chat-Message verarbeiten
- POST /api/v1/course-editor/ai/sessions/<id>/finalize - Session finalisieren
- DELETE /api/v1/course-editor/ai/sessions/<id> - Session archivieren
- GET /api/v1/course-editor/ai/courses/<course_id>/sessions - Alle Sessions eines Kurses
- GET /api/v1/course-editor/ai/method-types - Verfügbare Lernmethoden-Typen

Phase D4 - KI-Kurs-Builder
"""

from typing import Optional, Tuple
from flask import request, jsonify, g
import logging

from app.api.v1.panel.editor.ai import ai_editor_bp
from app.api.v1.panel.editor.shared.permissions import check_course_permission
from app.core.bootstrap.extensions import limiter
from app.api.middleware.auth import token_required
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response
from app.infrastructure.persistence.repositories.authoring.sessions import (
    CourseAuthoringSessionRepository,
)

logger = logging.getLogger(__name__)

# Roles with full access (mirrors permissions.py ADMIN_ROLES)
_ADMIN_ROLES = {'admin', 'owner', 'superadmin'}


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
        return error_response(ErrorCode.COURSE_FILE_NOT_FOUND, 404, details={'error': 'Session not found'})

    if str(session.get('created_by')) != str(user.get('user_id')):
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 403, details={'error': 'No access to this session'})

    return None


@ai_editor_bp.route('/sessions', methods=['POST'])
@check_course_permission('write')
@limiter.limit("10 per minute")
def create_course_authoring_session():
    """
    Erstellt eine neue Course Authoring Session.

    Request Body:
        {
            "course_id": "uuid",
            "model_profile": "anthropic-claude-sonnet" (optional)
        }

    Response 200:
        {
            "success": true,
            "data": {
                "session_id": "uuid",
                "course_id": "uuid",
                "draft_structure": {...},
                "status": "active"
            }
        }
    """
    try:
        from app.application.services.content.course_authoring import (
            get_course_authoring_service, CourseAuthoringError
        )

        data = request.get_json()
        if not data:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, details={'field': 'body', 'message': 'Request body required'})

        course_id = data.get('course_id')
        if not course_id:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, details={'field': 'course_id'})

        model_profile = data.get('model_profile', 'anthropic-claude-sonnet')
        provider_name = data.get('provider_name')
        model_name = data.get('model_name')
        user_id = g.current_user['user_id']

        # Explicit course access check (decorator can't check body params)
        user = g.current_user
        if user.get('role') not in _ADMIN_ROLES:
            from app.application.services.content.course_authoring.database import DatabaseOperations
            if not DatabaseOperations.check_user_access(user_id, course_id):
                return error_response(
                    ErrorCode.COURSE_FILE_OPERATION_FAILED, 403,
                    details={'error': 'No access to this course'}
                )

        # Validate manual model selection (DDD: validation in service layer)
        if provider_name and model_name:
            from app.application.services.content.course_authoring.session import CourseAuthoringService
            CourseAuthoringService.validate_model_selection(provider_name, model_name)

        service = get_course_authoring_service(
            provider=provider_name,
            model=model_name
        )
        result = service.create_session(
            user_id=user_id,
            course_id=course_id,
            model_profile=model_profile
        )

        logger.info(f"Created course authoring session {result['session_id']} "
                   f"for course {course_id} by user {user_id}")

        return jsonify({'success': True, 'data': result}), 200

    except CourseAuthoringError as e:
        logger.error(f"Course authoring error: {str(e)}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 400, details={'error': str(e)})
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}", exc_info=True)
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': 'Internal server error'})


@ai_editor_bp.route('/sessions/<session_id>', methods=['GET'])
@check_course_permission('read')
def get_course_authoring_session(session_id):
    """
    Lädt eine bestehende Course Authoring Session.

    Path Parameters:
        session_id: Session UUID

    Response 200:
        {
            "success": true,
            "data": {
                "session_id": "uuid",
                "course_id": "uuid",
                "course_title": "...",
                "draft_structure": {...},
                "chat_history": [...],
                "status": "active",
                "total_tokens_used": 1234
            }
        }
    """
    denied = _verify_session_access(session_id)
    if denied:
        return denied

    try:
        from app.application.services.content.course_authoring import (
            get_course_authoring_service, CourseAuthoringError
        )

        user_id = g.current_user['user_id']
        service = get_course_authoring_service()
        result = service.get_session(session_id, user_id)

        return jsonify({'success': True, 'data': result}), 200

    except CourseAuthoringError as e:
        logger.error(f"Course authoring error: {str(e)}")
        return error_response(ErrorCode.COURSE_FILE_NOT_FOUND, 404, details={'error': str(e)})
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}", exc_info=True)
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': 'Internal server error'})


@ai_editor_bp.route('/sessions/<session_id>/chat', methods=['POST'])
@check_course_permission('write')
@limiter.limit("30 per minute")
def course_authoring_chat(session_id):
    """
    Verarbeitet eine Chat-Nachricht und aktualisiert die Kursstruktur.

    Path Parameters:
        session_id: Session UUID

    Request Body:
        {
            "message": "Erstelle 3 Kapitel für IT-Grundlagen",
            "mode": "structure|lesson|method|exam" (optional),
            "file_ids": ["uuid1", "uuid2"] (optional)
        }

    Response 200:
        {
            "success": true,
            "data": {
                "assistant_message": "Ich habe 3 Kapitel erstellt...",
                "draft_structure": {...},
                "operations_applied": ["add_chapter", "add_chapter", "add_chapter"],
                "tokens_used": 1234
            }
        }
    """
    denied = _verify_session_access(session_id)
    if denied:
        return denied

    try:
        from app.application.services.content.course_authoring import (
            get_course_authoring_service, CourseAuthoringError
        )

        data = request.get_json()
        if not data:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, details={'field': 'body', 'message': 'Request body required'})

        message = data.get('message')
        if not message:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, details={'field': 'message'})

        mode = data.get('mode')
        file_ids = data.get('file_ids', [])
        user_id = g.current_user['user_id']

        service = get_course_authoring_service()
        result = service.apply_chat_message(
            session_id=session_id,
            user_id=user_id,
            message=message,
            mode=mode,
            file_ids=file_ids
        )

        ops_count = len(result.get('operations_applied', []))
        logger.info(f"Chat processed for session {session_id}, operations: {ops_count}")

        # Auto-finalize: if operations were applied, write to real DB immediately
        if ops_count > 0:
            try:
                finalize_result = service.finalize_session(session_id, user_id)
                result['finalized'] = True
                result['finalize_stats'] = finalize_result.get('stats', {})
                logger.info(f"Auto-finalized session {session_id}: {finalize_result.get('stats')}")

                # Create a fresh session so the user can keep chatting
                course_id = result['draft_structure'].get('course_id')
                if course_id:
                    new_session = service.create_session(
                        user_id=user_id,
                        course_id=course_id,
                        model_profile='anthropic-claude-sonnet'
                    )
                    result['new_session_id'] = new_session['session_id']
                    result['draft_structure'] = new_session['draft_structure']
                    logger.info(f"Created follow-up session {new_session['session_id']}")
            except Exception as e:
                logger.error(f"Auto-finalize failed for session {session_id}: {e}", exc_info=True)
                result['finalized'] = False
                result['finalize_error'] = str(e)

        return jsonify({'success': True, 'data': result}), 200

    except CourseAuthoringError as e:
        logger.error(f"Course authoring error: {str(e)}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 400, details={'error': str(e)})
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}", exc_info=True)
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': 'Internal server error'})


@ai_editor_bp.route('/sessions/<session_id>/finalize', methods=['POST'])
@check_course_permission('write')
@limiter.limit("5 per minute")
def finalize_course_authoring_session(session_id):
    """
    Finalisiert eine Session und erstellt echte Kursinhalte.

    Path Parameters:
        session_id: Session UUID

    Response 200:
        {
            "success": true,
            "data": {
                "status": "ok",
                "created_chapter_ids": ["uuid1", "uuid2"],
                "created_lesson_ids": ["uuid1", "uuid2", ...],
                "created_method_ids": ["uuid1", ...],
                "stats": {
                    "chapters": 2,
                    "lessons": 5,
                    "methods": 10
                }
            }
        }
    """
    denied = _verify_session_access(session_id)
    if denied:
        return denied

    try:
        from app.application.services.content.course_authoring import (
            get_course_authoring_service, CourseAuthoringError
        )

        user_id = g.current_user['user_id']
        service = get_course_authoring_service()
        result = service.finalize_session(session_id, user_id)

        logger.info(f"Finalized session {session_id}: "
                   f"{result['stats']['chapters']} chapters, "
                   f"{result['stats']['lessons']} lessons, "
                   f"{result['stats']['methods']} methods")

        return jsonify({'success': True, 'data': result}), 200

    except CourseAuthoringError as e:
        logger.error(f"Course authoring error: {str(e)}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 400, details={'error': str(e)})
    except Exception as e:
        logger.error(f"Error finalizing session: {str(e)}", exc_info=True)
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': 'Internal server error'})


@ai_editor_bp.route('/sessions/<session_id>', methods=['DELETE'])
@check_course_permission('delete')
def archive_course_authoring_session(session_id):
    """
    Archiviert eine Session (soft delete).

    Path Parameters:
        session_id: Session UUID

    Response 200:
        {
            "success": true,
            "message": "Session archived"
        }
    """
    denied = _verify_session_access(session_id)
    if denied:
        return denied

    try:
        user_id = g.current_user['user_id']

        # Update status to archived (ownership already verified by _verify_session_access)
        CourseAuthoringSessionRepository.archive_session(session_id, user_id)

        logger.info(f"Archived session {session_id} by user {user_id}")

        return jsonify({'success': True, 'message': 'Session archived'}), 200

    except Exception as e:
        logger.error(f"Error archiving session: {str(e)}", exc_info=True)
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': 'Internal server error'})


@ai_editor_bp.route('/courses/<course_id>/sessions', methods=['GET'])
@check_course_permission('read')
def list_course_authoring_sessions(course_id):
    """
    Listet alle Sessions eines Kurses.

    Path Parameters:
        course_id: Course UUID

    Query Parameters:
        status: Filter by status (active, finalized, archived)

    Response 200:
        {
            "success": true,
            "data": {
                "sessions": [
                    {
                        "session_id": "uuid",
                        "status": "active",
                        "created_at": "...",
                        "total_operations": 5
                    }
                ]
            }
        }
    """
    try:
        from app.infrastructure.persistence.repositories.authoring.sessions import CourseAuthoringSessionRepository

        status_filter = request.args.get('status')

        results = CourseAuthoringSessionRepository.list_sessions_for_course(
            course_id, status_filter=status_filter
        )

        sessions = []
        for row in results:
            sessions.append({
                'session_id': str(row['session_id']),
                'status': row['status'],
                'model_profile': row['model_profile'],
                'total_tokens_used': row['total_tokens_used'],
                'total_operations': row['total_operations'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None,
                'finalized_at': row['finalized_at'].isoformat() if row['finalized_at'] else None
            })

        return jsonify({'success': True, 'data': {'sessions': sessions}}), 200

    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}", exc_info=True)
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': 'Internal server error'})


@ai_editor_bp.route('/method-types', methods=['GET'])
@check_course_permission('read')
def get_method_types():
    """
    Gibt verfügbare Lernmethoden-Typen zurück.

    Response 200:
        {
            "success": true,
            "data": {
                "method_types": [
                    {
                        "type": "calculator_tutorial",
                        "name": "Taschenrechner-Tutorial",
                        "description": "Schritt-für-Schritt Anleitung für Taschenrechner",
                        "icon": "🧮"
                    },
                    ...
                ]
            }
        }
    """
    method_types = [
        {
            'type': 'calculator_tutorial',
            'name': 'Taschenrechner-Tutorial',
            'description': 'Schritt-für-Schritt Anleitung für Taschenrechner (Casio, TI)',
            'icon': '🧮',
            'lm_type': 1
        },
        {
            'type': 'tool_tutorial',
            'name': 'Tool-Tutorial',
            'description': 'Software/CLI-Anleitung (z.B. pfSense, Linux)',
            'icon': '🛠️',
            'lm_type': 9
        },
        {
            'type': 'step_by_step',
            'name': 'Prozess-Anleitung',
            'description': 'Mehrstufiger Prozess (z.B. Handelskalkulation)',
            'icon': '📋',
            'lm_type': 1
        },
        {
            'type': 'theory',
            'name': 'Theorieblatt',
            'description': 'Strukturierte Theorie mit Kernkonzepten',
            'icon': '📖',
            'lm_type': 0
        },
        {
            'type': 'quiz',
            'name': 'Quiz',
            'description': 'Multiple-Choice und Verständnisfragen',
            'icon': '❓',
            'lm_type': 2
        },
        {
            'type': 'flashcards',
            'name': 'Karteikarten',
            'description': 'Lernkarten für Begriffe und Definitionen',
            'icon': '🗂️',
            'lm_type': 6
        },
        {
            'type': 'exercise',
            'name': 'Übungsaufgabe',
            'description': 'Praktische Übung mit Lösung',
            'icon': '✏️',
            'lm_type': 8
        },
        {
            'type': 'exam',
            'name': 'Prüfungssimulation',
            'description': 'IHK-Stil Prüfungsaufgaben',
            'icon': '🎓',
            'lm_type': 10
        }
    ]

    return jsonify({'success': True, 'data': {'method_types': method_types}}), 200


@ai_editor_bp.route('/available-models', methods=['GET'])
@check_course_permission('read')
def get_available_models():
    """Returns active providers with their active chat models (editor-level)."""
    try:
        from app.application.services.content.course_authoring.session import (
            CourseAuthoringService,
        )
        result = CourseAuthoringService.get_available_models()
        return jsonify({'success': True, 'data': {'providers': result}}), 200
    except Exception as e:
        logger.error(f"Error fetching available models: {str(e)}", exc_info=True)
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500,
                            details={'error': 'Internal server error'})
