"""
LernsystemX Lesson Explanations API

Endpoints for managing lesson explanations (Tutor-Erklarungen).
Similar to chapter_theory but for individual lessons.

- GET /api/v1/lessons/{lesson_id}/explanations - List all explanations for a lesson
- GET /api/v1/lesson-explanation/{explanation_id} - Get specific explanation
- PATCH /api/v1/lesson-explanation/{explanation_id} - Update title
- DELETE /api/v1/lesson-explanation/{explanation_id} - Delete explanation
"""

from flask import request, jsonify, g
import logging
import json

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.extensions import limiter
from app.middleware.auth import token_required
from app.database.connection import fetch_one, fetch_all


@api_v1.route('/lessons/<lesson_id>/explanations', methods=['GET'])
@token_required
@limiter.limit("60 per minute")
def list_lesson_explanations(lesson_id: str):
    """
    List all explanations for a lesson.

    Response 200:
        {
            "success": true,
            "data": {
                "explanations": [
                    {
                        "explanationId": "uuid",
                        "title": "ADHS-Erklarung",
                        "style": "adhs",
                        "hasAudio": true,
                        "tokensUsed": 1234,
                        "createdAt": "2025-01-15T10:30:00Z",
                        "updatedAt": "2025-01-15T10:30:00Z"
                    }
                ]
            }
        }
    """
    try:
        query = """
            SELECT
                explanation_id,
                title,
                style,
                audio_url,
                tokens_used,
                created_at,
                updated_at
            FROM lesson_explanations
            WHERE lesson_id = %s
            ORDER BY created_at DESC
        """
        rows = fetch_all(query, (lesson_id,))

        explanations = []
        for row in rows:
            explanations.append({
                'explanationId': str(row['explanation_id']),
                'title': row['title'] or f"Erklarung ({row['style']})",
                'style': row['style'],
                'hasAudio': bool(row['audio_url']),
                'tokensUsed': row['tokens_used'] or 0,
                'createdAt': row['created_at'].isoformat() if row['created_at'] else None,
                'updatedAt': row['updated_at'].isoformat() if row['updated_at'] else None
            })

        return jsonify({
            'success': True,
            'data': {
                'explanations': explanations,
                'count': len(explanations)
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to list lesson explanations: {e}")
        return jsonify({
            'success': False,
            'error': {'message': 'Failed to load explanations', 'details': str(e)}
        }), 500


@api_v1.route('/lesson-explanation/<explanation_id>', methods=['GET'])
@token_required
@limiter.limit("60 per minute")
def get_lesson_explanation(explanation_id: str):
    """
    Get a specific lesson explanation by ID.

    Response 200:
        {
            "success": true,
            "data": {
                "explanationId": "uuid",
                "lessonId": "uuid",
                "title": "ADHS-Erklarung",
                "style": "adhs",
                "steps": [...],
                "audioUrl": "...",
                "tokensUsed": 1234,
                "createdAt": "...",
                "updatedAt": "..."
            }
        }
    """
    try:
        query = """
            SELECT
                explanation_id,
                lesson_id,
                title,
                style,
                explanation_data,
                audio_url,
                audio_duration_seconds,
                tokens_used,
                model_used,
                created_at,
                updated_at
            FROM lesson_explanations
            WHERE explanation_id = %s
        """
        row = fetch_one(query, (explanation_id,))

        if not row:
            return jsonify({
                'success': False,
                'error': {'message': 'Explanation not found'}
            }), 404

        # Parse explanation data
        explanation_data = row['explanation_data']
        if isinstance(explanation_data, str):
            explanation_data = json.loads(explanation_data)

        return jsonify({
            'success': True,
            'data': {
                'explanationId': str(row['explanation_id']),
                'lessonId': str(row['lesson_id']),
                'title': row['title'] or f"Erklarung ({row['style']})",
                'style': row['style'],
                'steps': explanation_data.get('steps', []),
                'overview': explanation_data.get('overview'),
                'summary': explanation_data.get('summary'),
                'audioUrl': row['audio_url'],
                'audioDuration': row['audio_duration_seconds'],
                'tokensUsed': row['tokens_used'] or 0,
                'modelUsed': row['model_used'],
                'createdAt': row['created_at'].isoformat() if row['created_at'] else None,
                'updatedAt': row['updated_at'].isoformat() if row['updated_at'] else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to get lesson explanation: {e}")
        return jsonify({
            'success': False,
            'error': {'message': 'Failed to load explanation', 'details': str(e)}
        }), 500


@api_v1.route('/lesson-explanation/<explanation_id>', methods=['PATCH'])
@token_required
@limiter.limit("30 per minute")
def update_lesson_explanation(explanation_id: str):
    """
    Update lesson explanation (currently only title).

    Request Body:
        {
            "title": "Neue Bezeichnung"
        }

    Response 200:
        {
            "success": true,
            "data": {
                "explanationId": "uuid",
                "title": "Neue Bezeichnung"
            }
        }
    """
    try:
        data = request.get_json()

        if not data or 'title' not in data:
            return jsonify({
                'success': False,
                'error': {'message': 'Title is required'}
            }), 400

        new_title = data['title'].strip()
        if not new_title:
            return jsonify({
                'success': False,
                'error': {'message': 'Title cannot be empty'}
            }), 400

        query = """
            UPDATE lesson_explanations
            SET title = %s
            WHERE explanation_id = %s
            RETURNING explanation_id, title
        """
        result = fetch_one(query, (new_title, explanation_id))

        if not result:
            return jsonify({
                'success': False,
                'error': {'message': 'Explanation not found'}
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'explanationId': str(result['explanation_id']),
                'title': result['title']
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to update lesson explanation: {e}")
        return jsonify({
            'success': False,
            'error': {'message': 'Failed to update explanation', 'details': str(e)}
        }), 500


@api_v1.route('/lesson-explanation/<explanation_id>', methods=['DELETE'])
@token_required
@limiter.limit("30 per minute")
def delete_lesson_explanation(explanation_id: str):
    """
    Delete a lesson explanation.

    Response 200:
        {
            "success": true,
            "message": "Explanation deleted"
        }
    """
    try:
        query = """
            DELETE FROM lesson_explanations
            WHERE explanation_id = %s
            RETURNING explanation_id
        """
        result = fetch_one(query, (explanation_id,))

        if not result:
            return jsonify({
                'success': False,
                'error': {'message': 'Explanation not found'}
            }), 404

        logger.info(f"Deleted lesson explanation {explanation_id}")

        return jsonify({
            'success': True,
            'message': 'Explanation deleted'
        }), 200

    except Exception as e:
        logger.error(f"Failed to delete lesson explanation: {e}")
        return jsonify({
            'success': False,
            'error': {'message': 'Failed to delete explanation', 'details': str(e)}
        }), 500
