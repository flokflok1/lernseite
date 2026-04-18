"""
AP2 Trainer API — Anlagen (beschriftbare Prüfungs-Appendices).

Endpoints:
- GET /anlagen — Liste aller Anlagen
- GET /anlagen/<anlage_id> — Anlage-Detail mit Hotspots

DDD: API-Layer. Keine SQL, keine Geschäftslogik.
"""

import logging
from uuid import UUID

from flask import jsonify

from app.api.middleware.auth import token_required
from app.infrastructure.persistence.repositories.ap2 import Ap2AnlageRepository
from app.domain.models.ap2 import Anlage

logger = logging.getLogger(__name__)


def register_anlagen_routes(bp):
    """Registriert Anlagen-Routes am ap2_trainer_bp."""

    @bp.route('/anlagen', methods=['GET'])
    @token_required
    def list_anlagen():
        """Alle verfügbaren Anlagen (für Library-View)."""
        try:
            anlagen = Ap2AnlageRepository.find_all()
            return jsonify({
                'success': True,
                'anlagen': [_anlage_to_dict_summary(a) for a in anlagen],
            }), 200
        except Exception:
            logger.exception('AP2 list anlagen failed')
            return jsonify({'success': False, 'error': 'list_failed'}), 500

    @bp.route('/anlagen/<anlage_id>', methods=['GET'])
    @token_required
    def get_anlage_detail(anlage_id: str):
        """Anlage-Detail mit Hotspots (für Anzeige + Beschriftung)."""
        try:
            anlage = Ap2AnlageRepository.find_by_id(UUID(anlage_id))
            if anlage is None:
                return jsonify({
                    'success': False, 'error': 'anlage_not_found',
                }), 404
            return jsonify({
                'success': True,
                'anlage': _anlage_to_dict_full(anlage),
            }), 200
        except ValueError:
            return jsonify({'success': False, 'error': 'invalid_id'}), 400
        except Exception:
            logger.exception('AP2 anlage detail failed for id=%s', anlage_id)
            return jsonify({'success': False, 'error': 'detail_failed'}), 500


def _anlage_to_dict_summary(a: Anlage) -> dict:
    """Compact für Listen-Ansicht."""
    return {
        'anlage_id': str(a.anlage_id),
        'slug': a.slug,
        'title': a.title,
        'anlage_type': a.anlage_type.value,
        'source_exam': a.source_exam,
        'anlage_number': a.anlage_number,
        'has_hotspots': a.has_hotspots,
    }


def _anlage_to_dict_full(a: Anlage) -> dict:
    """Vollständig — inkl. Hotspots OHNE correct_answers (Anti-Spoiler)."""
    return {
        'anlage_id': str(a.anlage_id),
        'slug': a.slug,
        'title': a.title,
        'anlage_type': a.anlage_type.value,
        'source_exam': a.source_exam,
        'anlage_number': a.anlage_number,
        'image_url': a.image_url,
        'image_width': a.image_width,
        'image_height': a.image_height,
        'svg_markup': a.svg_markup,
        'description': a.description,
        'footnote': a.footnote,
        'hotspots': [{
            'hotspot_id': h.hotspot_id,
            'x': h.x, 'y': h.y, 'width': h.width, 'height': h.height,
            'hotspot_type': h.hotspot_type.value,
            'placeholder': h.placeholder,
            'hint': h.hint,
            'dropdown_options': h.dropdown_options,
            'points': h.points,
            # correct_answers werden NICHT exposed (Anti-Spoiler)
        } for h in a.hotspots],
        'total_points': a.total_points,
    }
