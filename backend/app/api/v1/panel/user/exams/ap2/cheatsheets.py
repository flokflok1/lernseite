"""
AP2 Trainer API — Cheatsheets (User-generierte Markdown).

Endpoints:
- GET /cheatsheets — Liste aller Cheatsheets des Users
- GET /cheatsheets/<topic_slug> — Einzelnes Cheatsheet
- PUT /cheatsheets/<topic_slug> — Speichern/Update

DDD: API-Layer. Keine SQL, keine Geschäftslogik.
"""

import logging

from flask import jsonify, request

from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2TopicRepository,
    Ap2CheatsheetRepository,
)

logger = logging.getLogger(__name__)


def register_cheatsheet_routes(bp):
    """Registriert Cheatsheet-Routes am ap2_trainer_bp."""

    @bp.route('/cheatsheets', methods=['GET'])
    @token_required
    def list_cheatsheets():
        """Alle Cheatsheets des Users mit Topic-Namen."""
        try:
            user = get_current_user()
            rows = Ap2CheatsheetRepository.find_all_for_user(user['user_id'])
            return jsonify({
                'success': True,
                'cheatsheets': [{
                    'topic_slug': r['slug'],
                    'topic_name': r['name_de'],
                    'bereich': r['bereich'],
                    'word_count': r['word_count'],
                    'updated_at': r['updated_at'].isoformat() if r['updated_at'] else None,
                } for r in rows],
            }), 200
        except Exception:
            logger.exception('AP2 list cheatsheets failed')
            return jsonify({'success': False, 'error': 'list_failed'}), 500

    @bp.route('/cheatsheets/<topic_slug>', methods=['GET'])
    @token_required
    def get_cheatsheet(topic_slug: str):
        """Lädt das Cheatsheet eines Themas."""
        try:
            user = get_current_user()
            topic = Ap2TopicRepository.find_by_slug(topic_slug)
            if topic is None:
                return jsonify({'success': False, 'error': 'topic_not_found'}), 404

            cs = Ap2CheatsheetRepository.get(user['user_id'], topic.topic_id)
            return jsonify({
                'success': True,
                'topic_slug': topic.slug,
                'topic_name': topic.name_de,
                'markdown_content': cs.markdown_content if cs else '',
                'word_count': cs.word_count if cs else 0,
                'updated_at': (
                    cs.updated_at.isoformat() if cs and cs.updated_at else None
                ),
            }), 200
        except Exception:
            logger.exception('AP2 get cheatsheet failed for topic=%s', topic_slug)
            return jsonify({'success': False, 'error': 'get_failed'}), 500

    @bp.route('/cheatsheets/<topic_slug>', methods=['PUT'])
    @token_required
    def upsert_cheatsheet(topic_slug: str):
        """Speichert/Updated das Cheatsheet eines Themas.

        Body: { markdown_content: str }
        """
        try:
            user = get_current_user()
            body = request.get_json(force=True, silent=True) or {}
            content = body.get('markdown_content', '')

            topic = Ap2TopicRepository.find_by_slug(topic_slug)
            if topic is None:
                return jsonify({'success': False, 'error': 'topic_not_found'}), 404

            cs = Ap2CheatsheetRepository.upsert(
                user_id=user['user_id'],
                topic_id=topic.topic_id,
                markdown=content,
            )
            return jsonify({
                'success': True,
                'word_count': cs.word_count,
            }), 200
        except Exception:
            logger.exception('AP2 upsert cheatsheet failed for topic=%s', topic_slug)
            return jsonify({'success': False, 'error': 'upsert_failed'}), 500
