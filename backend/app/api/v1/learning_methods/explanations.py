"""
LernsystemX Lesson Explanations API - Consolidated

Lesson explanation management and access for users and admins.

User Endpoints (Read):
- GET /lessons/:lesson_id/explanations - List all explanations for a lesson
- GET /lesson-explanation/:explanation_id - Get specific explanation by ID

Admin Endpoints (Management):
- PATCH /lesson-explanation/:explanation_id - Update explanation title
- DELETE /lesson-explanation/:explanation_id - Delete specific explanation

Note: Explanation generation is handled by /admin/tutor/generate-lesson-explanation

All routes: /api/v1/lessons/*, /api/v1/lesson-explanation/*
ISO 9001:2015 compliant - Content Management Layer
"""

from flask import Blueprint, request, jsonify
import json
import logging
from typing import Optional, Dict, Any

from app.extensions import limiter
from app.api.middleware.auth import token_required
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all

# Blueprint
lesson_explanations_bp = Blueprint('lesson_explanations', __name__, url_prefix='')

__all__ = ['lesson_explanations_bp']

logger = logging.getLogger(__name__)


# =============================================================================
# USER ENDPOINTS - READ OPERATIONS
# =============================================================================

@lesson_explanations_bp.route('/lessons/<lesson_id>/explanations', methods=['GET'])
@token_required
@limiter.limit("60 per minute")
def list_lesson_explanations(lesson_id: str):
    """
    List all explanations for a lesson.

    Response:
        200: List of explanations with metadata
        500: Server error
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


@lesson_explanations_bp.route('/lesson-explanation/<explanation_id>', methods=['GET'])
@token_required
@limiter.limit("60 per minute")
def get_lesson_explanation(explanation_id: str):
    """
    Get a specific lesson explanation by ID.

    Response:
        200: Explanation data
        404: Explanation not found
        500: Server error
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


# =============================================================================
# ADMIN ENDPOINTS - MANAGEMENT OPERATIONS
# =============================================================================

@lesson_explanations_bp.route('/lesson-explanation/<explanation_id>', methods=['PATCH'])
@token_required
@limiter.limit("30 per minute")
def update_lesson_explanation(explanation_id: str):
    """
    Update lesson explanation (admin only).

    Request Body:
        {
            "title": "Neue Bezeichnung"
        }

    Response:
        200: Explanation updated successfully
        400: Invalid request
        404: Explanation not found
        500: Server error
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


@lesson_explanations_bp.route('/lesson-explanation/<explanation_id>', methods=['DELETE'])
@token_required
@limiter.limit("30 per minute")
def delete_lesson_explanation(explanation_id: str):
    """
    Delete a lesson explanation (admin only).

    Response:
        200: Explanation deleted successfully
        404: Explanation not found
        500: Server error
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
