"""
Tutor Knowledge API Endpoints.

Endpoints for loading tutor knowledge and context from the database.
"""

import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.api.middleware.auth import token_required

logger = logging.getLogger(__name__)

# Blueprint for tutor knowledge
tts_tutor_bp = Blueprint('tts_tutor', __name__, url_prefix='/tutor')


@tts_tutor_bp.route('/knowledge', methods=['POST'])
@token_required
def get_tutor_knowledge():
    """
    Laedt Tutor-Wissen aus der Datenbank.

    Der Tutor verwendet dieses Wissen um kontextbezogene Erklaerungen zu geben.

    Request Body:
    {
        "course_id": "uuid",       // Optional: Kurs-Kontext
        "chapter_id": "uuid",      // Optional: Kapitel-Kontext
        "lesson_id": 123,          // Optional: Lektions-Inhalt
        "method_id": "uuid",       // Optional: Lernmethoden-Daten
        "include_files": true,     // Optional: Kurs-Dateien
        "include_progress": true   // Optional: Lernfortschritt
    }

    Response:
    {
        "success": true,
        "data": {
            "context_prompt": "...",  // Formatierter Kontext-String
            "course": {...},          // Kurs-Details
            "chapter": {...},         // Kapitel-Details
            "lesson": {...},          // Lektions-Details
            "method": {...}           // Lernmethoden-Details
        }
    }
    """
    try:
        from app.services.tutor_knowledge import TutorKnowledgeService

        user_id = get_jwt_identity()
        data = request.get_json() or {}

        course_id = data.get('course_id')
        chapter_id = data.get('chapter_id')
        lesson_id = data.get('lesson_id')
        method_id = data.get('method_id')
        include_files = data.get('include_files', True)
        include_progress = data.get('include_progress', True)

        # Build context prompt
        context_prompt = TutorKnowledgeService.build_tutor_context_prompt(
            course_id=course_id,
            chapter_id=chapter_id,
            lesson_id=lesson_id,
            method_id=method_id,
            user_id=user_id if include_progress else None,
            include_files=include_files,
            include_progress=include_progress
        )

        # Also return individual data objects
        result_data = {
            'context_prompt': context_prompt
        }

        if course_id:
            result_data['course'] = TutorKnowledgeService.get_course_context(course_id)

        if chapter_id:
            result_data['chapter'] = TutorKnowledgeService.get_chapter_context(chapter_id)

        if lesson_id:
            result_data['lesson'] = TutorKnowledgeService.get_lesson_content(lesson_id)

        if method_id:
            result_data['method'] = TutorKnowledgeService.get_learning_method_data(method_id)

        return jsonify({
            'success': True,
            'data': result_data
        })

    except Exception as e:
        logger.error(f"Tutor knowledge error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {'code': 'KNOWLEDGE_ERROR', 'message': str(e)}
        }), 500


@tts_tutor_bp.route('/course/<course_id>/context', methods=['GET'])
@token_required
def get_course_tutor_context(course_id: str):
    """
    Kurzform: Laedt Kurs-Kontext fuer den Tutor.

    URL Params:
        course_id: UUID des Kurses

    Response:
    {
        "success": true,
        "data": {
            "course": {...},
            "chapters": [...],
            "total_lessons": 42
        }
    }
    """
    try:
        from app.services.tutor_knowledge import TutorKnowledgeService

        context = TutorKnowledgeService.get_course_context(course_id)

        if not context:
            return jsonify({
                'success': False,
                'error': {'code': 'NOT_FOUND', 'message': 'Course not found'}
            }), 404

        return jsonify({
            'success': True,
            'data': context
        })

    except Exception as e:
        logger.error(f"Course context error: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'CONTEXT_ERROR', 'message': str(e)}
        }), 500


@tts_tutor_bp.route('/chapter/<chapter_id>/context', methods=['GET'])
@token_required
def get_chapter_tutor_context(chapter_id: str):
    """
    Kurzform: Laedt Kapitel-Kontext fuer den Tutor.

    URL Params:
        chapter_id: UUID des Kapitels

    Response:
    {
        "success": true,
        "data": {
            "chapter": {...},
            "lessons": [...],
            "learning_methods": [...]
        }
    }
    """
    try:
        from app.services.tutor_knowledge import TutorKnowledgeService

        context = TutorKnowledgeService.get_chapter_context(chapter_id)

        if not context:
            return jsonify({
                'success': False,
                'error': {'code': 'NOT_FOUND', 'message': 'Chapter not found'}
            }), 404

        return jsonify({
            'success': True,
            'data': context
        })

    except Exception as e:
        logger.error(f"Chapter context error: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'CONTEXT_ERROR', 'message': str(e)}
        }), 500
