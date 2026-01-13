"""
LernsystemX Chapter Theory Read Operations (User)

User-facing read-only endpoints for chapter theories.

Endpoints:
- GET /api/v1/chapters/:chapter_id/theories - List all theories
- GET /api/v1/chapters/:chapter_id/theory - Get theory (with fallback)
- GET /api/v1/chapter-theory/:theory_id - Get specific theory by ID

DDD Refactored: 2026-01-08
Consolidated from management/list_get.py
User-facing operations (read-only)
"""

from flask import Blueprint, request, jsonify
import json
import logging

from app.extensions import limiter
from app.middleware.auth import token_required

from ..core.repository import (
    list_chapter_theories,
    get_chapter_theory,
    get_chapter_theory_by_id,
    get_fallback_theory,
)

logger = logging.getLogger(__name__)

# Blueprint for user read operations
chapter_theory_user_read_bp = Blueprint(
    'chapter_theory_user_read',
    __name__,
    url_prefix=''
)


@chapter_theory_user_read_bp.route('/chapters/<chapter_id>/theories', methods=['GET'])
@token_required
@limiter.limit("30 per minute")
def list_theories(chapter_id: str):
    """
    List all theories for a chapter.

    Response 200:
        {
            "success": true,
            "data": {
                "theories": [
                    {
                        "theoryId": "uuid",
                        "title": "ADHS-freundlich (15.12.2025)",
                        "style": "adhs",
                        "createdAt": "...",
                        "hasAudio": true
                    },
                    ...
                ],
                "count": 3
            }
        }
    """
    try:
        theories = list_chapter_theories(chapter_id)

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


@chapter_theory_user_read_bp.route('/chapters/<chapter_id>/theory', methods=['GET'])
@token_required
@limiter.limit("30 per minute")
def get_theory(chapter_id: str):
    """
    Get chapter theory (cached from DB).
    Returns the most recent theory, optionally filtered by style.

    Query params:
        style: Theory style (adhs, detailed, short, exam_focus, standard)
        theory_id: Specific theory ID to fetch

    Response 200:
        {
            "success": true,
            "data": {
                "hasTheory": true,
                "theoryId": "uuid",
                "title": "...",
                "theory": {...},
                "audioUrl": "...",
                "style": "adhs",
                "createdAt": "..."
            }
        }
    """
    try:
        theory_id = request.args.get('theory_id')
        style = request.args.get('style', 'adhs')

        # If specific theory_id requested, get that one
        if theory_id:
            theory_record = get_chapter_theory_by_id(theory_id)
        else:
            # Validate style
            valid_styles = ['adhs', 'detailed', 'short', 'exam_focus', 'standard']
            if style not in valid_styles:
                style = 'adhs'

            # Get from database - try requested style first
            theory_record = get_chapter_theory(chapter_id, style)

            # Fallback: if no theory for requested style, try to find ANY available
            if not theory_record:
                theory_record = get_fallback_theory(chapter_id)
                if theory_record:
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


@chapter_theory_user_read_bp.route('/chapter-theory/<theory_id>', methods=['GET'])
@token_required
def get_theory_by_id(theory_id: str):
    """Get a specific theory by ID."""
    try:
        theory_record = get_chapter_theory_by_id(theory_id)

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
