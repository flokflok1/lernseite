"""
LernsystemX Chapter Theory API - Consolidated

Chapter theory management and access for users and admins.

User Endpoints (Read-only):
- GET /chapters/:chapter_id/theories - List all theories for a chapter
- GET /chapters/:chapter_id/theory - Get theory with fallback
- GET /chapter-theory/:theory_id - Get specific theory by ID

Admin Endpoints (Management):
- PATCH /chapter-theory/:theory_id - Update theory title
- DELETE /chapter-theory/:theory_id - Delete specific theory
- DELETE /chapters/:chapter_id/theory - Delete theory by style

Note: Theory generation is handled by /admin/tutor/generate-chapter-theory

All routes: /api/v1/chapters/*, /api/v1/chapter-theory/*
ISO 9001:2015 compliant - Content Management Layer
"""

from flask import Blueprint, request, jsonify
import json
import logging
from typing import Optional, Dict, Any, List

from app.core.bootstrap.extensions import limiter
from app.api.middleware.auth import token_required
from app.infrastructure.persistence.repositories.content.chapter_theory import ChapterTheoryRepository

# Blueprint
chapter_theory_bp = Blueprint('chapter_theory', __name__, url_prefix='')

__all__ = ['chapter_theory_bp']

logger = logging.getLogger(__name__)


# =============================================================================
# USER ENDPOINTS - READ OPERATIONS
# =============================================================================

@chapter_theory_bp.route('/chapters/<chapter_id>/theories', methods=['GET'])
@token_required
@limiter.limit("30 per minute")
def list_theories(chapter_id: str):
    """
    List all theories for a chapter.

    Response:
        200: List of theories with metadata
        500: Server error
    """
    try:
        theories = ChapterTheoryRepository.list_by_chapter(chapter_id)

        theory_list = []
        for t in theories:
            theory_list.append({
                'theoryId': str(t.get('theory_id')),
                'title': t.get('title') or f"Theorieblatt ({t.get('style', 'standard')})",
                'style': t.get('style'),
                'hasAudio': bool(t.get('audio_url')),
                'tokensUsed': t.get('tokens_used', 0),
                'createdAt': t.get('created_at').isoformat() if t.get('created_at') else None,
                'updatedAt': t.get('updated_at').isoformat() if t.get('updated_at') else None
            })

        return jsonify({
            'success': True,
            'data': {
                'theories': theory_list,
                'count': len(theory_list)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing chapter theories: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list theories',
            'message': str(e)
        }), 500


@chapter_theory_bp.route('/chapters/<chapter_id>/theory', methods=['GET'])
@token_required
@limiter.limit("30 per minute")
def get_theory(chapter_id: str):
    """
    Get chapter theory (cached from DB).
    Returns the most recent theory, optionally filtered by style.

    Query Parameters:
        style (str): Theory style (adhs, detailed, short, exam_focus, standard)
        theory_id (str): Specific theory ID to fetch

    Response:
        200: Theory data or indication that no theory exists
        500: Server error
    """
    try:
        theory_id = request.args.get('theory_id')
        style = request.args.get('style', 'adhs')

        # If specific theory_id requested, get that one
        if theory_id:
            theory_record = ChapterTheoryRepository.get_by_id(theory_id)
        else:
            # Validate style
            valid_styles = ['adhs', 'detailed', 'short', 'exam_focus', 'standard']
            if style not in valid_styles:
                style = 'adhs'

            # Get from database - try requested style first
            theory_record = ChapterTheoryRepository.get_by_chapter_and_style(chapter_id, style)

            # Fallback: if no theory for requested style, try to find ANY available
            if not theory_record:
                all_theories = ChapterTheoryRepository.list_by_chapter(chapter_id)
                if all_theories:
                    theory_record = all_theories[0]  # Get most recent
                    logger.info(
                        f"Using fallback theory with style={theory_record.get('style')} "
                        f"for chapter {chapter_id}"
                    )

        if not theory_record:
            return jsonify({
                'success': True,
                'data': {
                    'hasTheory': False,
                    'theory': None,
                    'style': style,
                    'message': 'No theory generated yet for this chapter'
                }
            }), 200

        # Parse theory_data from JSONB
        theory_data = theory_record.get('theory_data', {})
        if isinstance(theory_data, str):
            theory_data = json.loads(theory_data)

        # Return actual style from record (might differ if fallback was used)
        actual_style = theory_record.get('style', style)

        return jsonify({
            'success': True,
            'data': {
                'hasTheory': True,
                'theoryId': str(theory_record.get('theory_id')),
                'title': theory_record.get('title') or f"Theorieblatt ({actual_style})",
                'theory': theory_data,
                'audioUrl': theory_record.get('audio_url'),
                'audioDuration': theory_record.get('audio_duration_seconds'),
                'style': actual_style,
                'requestedStyle': style,
                'createdAt': theory_record.get('created_at').isoformat() if theory_record.get('created_at') else None,
                'tokensUsed': theory_record.get('tokens_used', 0)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting chapter theory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get chapter theory',
            'message': str(e)
        }), 500


@chapter_theory_bp.route('/chapter-theory/<theory_id>', methods=['GET'])
@token_required
def get_theory_by_id(theory_id: str):
    """
    Get a specific theory by ID.

    Response:
        200: Theory data
        404: Theory not found
        500: Server error
    """
    try:
        theory_record = ChapterTheoryRepository.get_by_id(theory_id)

        if not theory_record:
            return jsonify({
                'success': False,
                'error': 'Theory not found'
            }), 404

        # Parse theory_data from JSONB
        theory_data = theory_record.get('theory_data', {})
        if isinstance(theory_data, str):
            theory_data = json.loads(theory_data)

        return jsonify({
            'success': True,
            'data': {
                'theoryId': str(theory_record.get('theory_id')),
                'chapterId': str(theory_record.get('chapter_id')),
                'title': theory_record.get('title'),
                'style': theory_record.get('style'),
                'theory': theory_data,
                'audioUrl': theory_record.get('audio_url'),
                'audioDuration': theory_record.get('audio_duration_seconds'),
                'createdAt': theory_record.get('created_at').isoformat() if theory_record.get('created_at') else None,
                'tokensUsed': theory_record.get('tokens_used', 0)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting theory by ID: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get theory',
            'message': str(e)
        }), 500


# =============================================================================
# ADMIN ENDPOINTS - MANAGEMENT OPERATIONS
# =============================================================================

@chapter_theory_bp.route('/chapter-theory/<theory_id>', methods=['PATCH'])
@token_required
def update_theory(theory_id: str):
    """
    Update theory title (admin only).

    Request Body:
        {
            "title": "New title"
        }

    Response:
        200: Theory updated successfully
        400: Invalid request
        404: Theory not found
        500: Server error
    """
    try:
        data = request.get_json() or {}
        title = data.get('title')

        if not title:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400

        result = ChapterTheoryRepository.update_title(theory_id, title)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Theory not found'
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'theoryId': str(result.get('theory_id')),
                'title': result.get('title'),
                'updatedAt': result.get('updated_at').isoformat() if result.get('updated_at') else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Error updating theory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update theory',
            'message': str(e)
        }), 500


@chapter_theory_bp.route('/chapter-theory/<theory_id>', methods=['DELETE'])
@token_required
def delete_theory_by_id(theory_id: str):
    """
    Delete a specific theory by ID (admin only).

    Response:
        200: Theory deleted successfully
        404: Theory not found
        500: Server error
    """
    try:
        deleted = ChapterTheoryRepository.delete_by_id(theory_id)

        if not deleted:
            return jsonify({
                'success': False,
                'error': 'Theory not found'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Theory deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting theory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete theory',
            'message': str(e)
        }), 500


@chapter_theory_bp.route('/chapters/<chapter_id>/theory', methods=['DELETE'])
@token_required
def delete_theory_by_style(chapter_id: str):
    """
    Delete chapter theory from database (admin only).

    Query Parameters:
        style (str): Theory style (adhs, detailed, short, exam_focus, standard)
                     If not specified, deletes ALL theories for this chapter

    Response:
        200: Theory deleted successfully
        404: Theory not found
        500: Server error
    """
    try:
        style = request.args.get('style')
        deleted = ChapterTheoryRepository.delete_by_chapter_and_style(chapter_id, style)

        if deleted:
            logger.info(f"Deleted chapter theory for {chapter_id} (style={style or 'ALL'})")
            return jsonify({
                'success': True,
                'message': 'Theory deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Theory not found'
            }), 404

    except Exception as e:
        logger.error(f"Error deleting chapter theory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete theory',
            'message': str(e)
        }), 500
