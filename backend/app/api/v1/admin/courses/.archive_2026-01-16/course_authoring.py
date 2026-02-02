"""
LernsystemX Admin Course Authoring API

Chat-basiertes Kurs-Authoring mit persistenten Sessions:
- POST /api/v1/admin/course-authoring/sessions - Neue Session erstellen
- GET /api/v1/admin/course-authoring/sessions/<id> - Session laden
- POST /api/v1/admin/course-authoring/sessions/<id>/chat - Chat-Message verarbeiten
- POST /api/v1/admin/course-authoring/sessions/<id>/finalize - Session finalisieren
- DELETE /api/v1/admin/course-authoring/sessions/<id> - Session archivieren
- GET /api/v1/admin/course-authoring/sessions - Alle Sessions eines Kurses

Phase D4 - KI-Kurs-Builder
"""

from flask import request, jsonify, g
import logging

from app.api.v1 import api_v1
from app.core.bootstrap.extensions import limiter
from app.api.middleware.auth import token_required, permission_required

logger = logging.getLogger(__name__)


@api_v1.route('/admin/course-authoring/sessions', methods=['POST'])
@token_required
@permission_required('content.courses:write')
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
        from app.application.services.course_authoring_service import (
            get_course_authoring_service, CourseAuthoringError
        )

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        course_id = data.get('course_id')
        if not course_id:
            return jsonify({'success': False, 'error': 'course_id is required'}), 400

        model_profile = data.get('model_profile', 'anthropic-claude-sonnet')
        user_id = g.current_user['user_id']

        service = get_course_authoring_service()
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
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create session'}), 500


@api_v1.route('/admin/course-authoring/sessions/<session_id>', methods=['GET'])
@token_required
@permission_required('content.courses:read')
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
    try:
        from app.application.services.course_authoring_service import (
            get_course_authoring_service, CourseAuthoringError
        )

        user_id = g.current_user['user_id']
        service = get_course_authoring_service()
        result = service.get_session(session_id, user_id)

        return jsonify({'success': True, 'data': result}), 200

    except CourseAuthoringError as e:
        logger.error(f"Course authoring error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get session'}), 500


@api_v1.route('/admin/course-authoring/sessions/<session_id>/chat', methods=['POST'])
@token_required
@permission_required('content.courses:write')
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
    try:
        from app.application.services.course_authoring_service import (
            get_course_authoring_service, CourseAuthoringError
        )

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        message = data.get('message')
        if not message:
            return jsonify({'success': False, 'error': 'message is required'}), 400

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

        logger.info(f"Chat processed for session {session_id}, "
                   f"operations: {len(result.get('operations_applied', []))}")

        return jsonify({'success': True, 'data': result}), 200

    except CourseAuthoringError as e:
        logger.error(f"Course authoring error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process message'}), 500


@api_v1.route('/admin/course-authoring/sessions/<session_id>/finalize', methods=['POST'])
@token_required
@permission_required('content.courses:write')
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
    try:
        from app.application.services.course_authoring_service import (
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
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error finalizing session: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to finalize session'}), 500


@api_v1.route('/admin/course-authoring/sessions/<session_id>', methods=['DELETE'])
@token_required
@permission_required('content.courses:write')
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
    try:
        from app.infrastructure.persistence.database.connection import execute_query

        user_id = g.current_user['user_id']

        # Update status to archived
        query = """
            UPDATE course_authoring_sessions
            SET status = 'archived'
            WHERE session_id = %s
            AND (created_by = %s OR EXISTS (
                SELECT 1 FROM users u
                JOIN roles r ON r.role_id = u.role_id
                WHERE u.user_id = %s AND r.role_name = 'admin'
            ))
        """
        execute_query(query, (session_id, user_id, user_id))

        logger.info(f"Archived session {session_id} by user {user_id}")

        return jsonify({'success': True, 'message': 'Session archived'}), 200

    except Exception as e:
        logger.error(f"Error archiving session: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to archive session'}), 500


@api_v1.route('/admin/course-authoring/courses/<course_id>/sessions', methods=['GET'])
@token_required
@permission_required('content.courses:read')
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
        from app.infrastructure.persistence.database.connection import fetch_all

        status_filter = request.args.get('status')

        query = """
            SELECT session_id, status, model_profile,
                   total_tokens_used, total_operations,
                   created_at, updated_at, finalized_at
            FROM course_authoring_sessions
            WHERE course_id = %s
        """
        params = [course_id]

        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)

        query += " ORDER BY created_at DESC"

        results = fetch_all(query, tuple(params))

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
        logger.error(f"Error listing sessions: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to list sessions'}), 500


@api_v1.route('/admin/course-authoring/method-types', methods=['GET'])
@token_required
@permission_required('content.courses:read')
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
            'lm_type': 22
        },
        {
            'type': 'flashcards',
            'name': 'Karteikarten',
            'description': 'Lernkarten für Begriffe und Definitionen',
            'icon': '🗂️',
            'lm_type': 13
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
            'lm_type': 19
        }
    ]

    return jsonify({'success': True, 'data': {'method_types': method_types}}), 200
