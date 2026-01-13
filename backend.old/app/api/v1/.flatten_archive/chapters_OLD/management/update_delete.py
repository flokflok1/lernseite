"""
LernsystemX Chapter Theory CRUD - Update and Delete Operations

User-facing endpoints for modifying chapter theories:
- PATCH /api/v1/chapter-theory/:theory_id - Update theory title
- DELETE /api/v1/chapter-theory/:theory_id - Delete specific theory
- DELETE /api/v1/chapters/:chapter_id/theory - Delete theory by style
"""

from flask import Blueprint, request, jsonify
import logging

from app.middleware.auth import token_required

from ..repository import (
    update_chapter_theory_title,
    delete_chapter_theory_by_id,
    delete_chapter_theory_by_style,
)

logger = logging.getLogger(__name__)

# Blueprint for update/delete operations
chapter_theory_update_delete_bp = Blueprint(
    'chapter_theory_update_delete',
    __name__,
    url_prefix=''
)


@chapter_theory_update_delete_bp.route('/chapter-theory/<theory_id>', methods=['PATCH'])
@token_required
def update_theory(theory_id: str):
    """Update theory title."""
    try:
        data = request.get_json() or {}
        title = data.get('title')

        if not title:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400

        result = update_chapter_theory_title(theory_id, title)

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


@chapter_theory_update_delete_bp.route('/chapter-theory/<theory_id>', methods=['DELETE'])
@token_required
def delete_theory_by_id_endpoint(theory_id: str):
    """Delete a specific theory by ID."""
    try:
        deleted = delete_chapter_theory_by_id(theory_id)

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


@chapter_theory_update_delete_bp.route('/chapters/<chapter_id>/theory', methods=['DELETE'])
@token_required
def delete_theory(chapter_id: str):
    """
    Delete chapter theory from database.

    Query params:
        style: Theory style (adhs, detailed, short, exam_focus, standard)
               If not specified, deletes ALL theories for this chapter

    Response 200:
        {
            "success": true,
            "message": "Theory deleted"
        }
    """
    try:
        style = request.args.get('style')
        deleted = delete_chapter_theory_by_style(chapter_id, style)

        if deleted:
            logger.info(f"Deleted chapter theory for {chapter_id} (style={style})")
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
