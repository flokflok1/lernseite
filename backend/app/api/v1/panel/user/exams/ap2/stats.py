"""
AP2 Trainer API — Stats + Topics.

Endpoints:
- GET /stats — Dashboard-Payload (Mastery, Bereiche, Schwächen)
- GET /topics — Topic-Liste mit Priorität
- GET /topics/<slug> — Topic-Details + Items pro Phase

DDD: API-Layer. Keine SQL.
"""

import logging

from flask import jsonify

from app.api.middleware.auth import token_required, get_current_user
from app.application.services.ap2 import Ap2DashboardService
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2TopicRepository,
    Ap2LearningItemRepository,
)
from app.domain.models.ap2 import ItemType

logger = logging.getLogger(__name__)


def register_stats_routes(bp):
    """Registriert Stats- und Topic-Routes am ap2_trainer_bp."""

    @bp.route('/stats', methods=['GET'])
    @token_required
    def get_stats():
        """Dashboard-Payload für eingeloggten User."""
        try:
            user = get_current_user()
            stats = Ap2DashboardService.get_user_stats(user['user_id'])
            return jsonify({'success': True, **stats}), 200
        except Exception:
            logger.exception('AP2 stats failed')
            return jsonify({'success': False, 'error': 'stats_failed'}), 500

    @bp.route('/topics', methods=['GET'])
    @token_required
    def list_topics():
        """Alle Topics mit Priorität + Bereich."""
        try:
            topics = Ap2TopicRepository.find_all()
            return jsonify({
                'success': True,
                'topics': [_topic_to_dict(t) for t in topics],
            }), 200
        except Exception:
            logger.exception('AP2 list topics failed')
            return jsonify({'success': False, 'error': 'list_failed'}), 500

    @bp.route('/topics/<slug>', methods=['GET'])
    @token_required
    def get_topic_detail(slug: str):
        """Topic + Items pro Phase (Blurt/Cued/Application).

        Items werden OHNE Musterlösung zurückgegeben (User darf nicht
        spoilern). Lösung kommt nur im Bewertungs-Response.
        """
        try:
            topic = Ap2TopicRepository.find_by_slug(slug)
            if topic is None:
                return jsonify({
                    'success': False, 'error': 'topic_not_found',
                }), 404

            items_by_phase = {}
            for item_type in (ItemType.BLURT, ItemType.CUED, ItemType.APPLICATION):
                items = Ap2LearningItemRepository.find_by_topic(
                    topic.topic_id, item_type
                )
                items_by_phase[item_type.value] = [
                    _item_to_dict_safe(i) for i in items
                ]

            return jsonify({
                'success': True,
                'topic': _topic_to_dict(topic),
                'items': items_by_phase,
            }), 200
        except Exception:
            logger.exception('AP2 topic detail failed for slug=%s', slug)
            return jsonify({'success': False, 'error': 'detail_failed'}), 500


def _topic_to_dict(t) -> dict:
    return {
        'topic_id': str(t.topic_id),
        'slug': t.slug,
        'name_de': t.name_de,
        'name_en': t.name_en,
        'bereich': t.bereich.value,
        'priority': t.priority.value,
        'expected_points': t.expected_points,
        'exam_count': t.exam_count,
        'description': t.description,
        'is_critical': t.is_critical,
    }


def _item_to_dict_safe(item) -> dict:
    """Item ohne model_answer + grading_criteria (Anti-Spoiler)."""
    return {
        'item_id': str(item.item_id),
        'item_type': item.item_type.value,
        'prompt': item.prompt,
        'points': item.points,
        'source_exam': item.source_exam,
        'anlage_id': str(item.anlage_id) if item.anlage_id else None,
        'difficulty': item.difficulty,
        'estimated_time_sec': item.estimated_time_sec,
        'calculator_hint': item.calculator_hint,
    }
