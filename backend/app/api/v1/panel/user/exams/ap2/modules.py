"""
AP2 Trainer API — Modules + Telegram-Verknüpfung.

Endpoints:
- GET  /modules                    — Liste aller Module mit User-Status
- POST /modules/<id>/start         — Modul starten (oder fortsetzen)
- POST /modules/<id>/submit        — Antwort auf aktuelles Item einreichen
- GET  /modules/<id>/recall-item   — Same-Day-Recall-Item ziehen
- GET  /modules/<id>/spotcheck-item — Spot-Check-Item ziehen

- POST /telegram/link-code         — Neuen Verknüpfungs-Code generieren
- DELETE /telegram/link            — Verknüpfung lösen

DDD: API-Layer. Keine SQL, keine Geschäftslogik (nur Service-Aufrufe).
"""

import logging
from uuid import UUID

from flask import jsonify, request

from app.api.middleware.auth import token_required, get_current_user
from app.application.services.ap2 import (
    ModuleProgressService, ModuleNotAvailableError,
)
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2ModuleRepository, Ap2ModuleProgressRepository,
)
from app.infrastructure.persistence.repositories.user import (
    TelegramLinkRepository,
)
from app.domain.models.ap2 import AttemptSource, ModuleStatus

logger = logging.getLogger(__name__)


def _module_to_dict(module, progress=None) -> dict:
    return {
        'module_id': str(module.module_id),
        'slug': module.slug,
        'name_de': module.name_de,
        'description': module.description,
        'estimated_min': module.estimated_min,
        'difficulty': module.difficulty,
        'sort_order': module.sort_order,
        'prerequisite_slugs': module.prerequisite_slugs,
        'progress': _progress_to_dict(progress) if progress else None,
    }


def _progress_to_dict(p) -> dict:
    return {
        'status': p.status.value,
        'streak_count': p.streak_count,
        'total_attempts': p.total_attempts,
        'passed_attempts': p.passed_attempts,
        'cooldown_until': p.cooldown_until.isoformat() if p.cooldown_until else None,
        'same_day_recall_due_at': (
            p.same_day_recall_due_at.isoformat()
            if p.same_day_recall_due_at else None
        ),
        'mastered_at': p.mastered_at.isoformat() if p.mastered_at else None,
        'spotcheck_stage': p.spotcheck_stage,
        'next_spotcheck_at': (
            p.next_spotcheck_at.isoformat() if p.next_spotcheck_at else None
        ),
    }


def _item_to_dict(item) -> dict:
    if not item:
        return None
    return {
        'item_id': str(item.item_id),
        'item_type': item.item_type.value,
        'prompt': item.prompt,
        'points': float(item.points),
        'difficulty': item.difficulty,
        'estimated_time_sec': item.estimated_time_sec,
        'calculator_hint': item.calculator_hint,
    }


def register_module_routes(bp):
    """Registriert Modul-Routes am ap2_trainer_bp."""

    @bp.route('/modules', methods=['GET'])
    @token_required
    def list_modules():
        user = get_current_user()
        modules = Ap2ModuleRepository.find_all_active()
        all_progress = Ap2ModuleProgressRepository.find_all_for_user(user.user_id)
        progress_by_module = {p.module_id: p for p in all_progress}

        result = []
        for m in modules:
            p = progress_by_module.get(m.module_id)
            if not p:
                # Init lazy: nur Status berechnen, nicht persistieren
                from app.application.services.ap2.module_progress_service import (
                    ModuleProgressService as MPS,
                )
                # Wir geben einen "virtuellen" Status zurück
                init_status = MPS._compute_initial_status(user.user_id, m)
                result.append({
                    **_module_to_dict(m),
                    'progress': {'status': init_status.value, 'streak_count': 0,
                                 'mastered_at': None, 'next_spotcheck_at': None},
                })
            else:
                result.append(_module_to_dict(m, p))

        return jsonify({'modules': result}), 200

    @bp.route('/modules/<module_id>/start', methods=['POST'])
    @token_required
    def start_module(module_id):
        user = get_current_user()
        try:
            mid = UUID(module_id)
        except ValueError:
            return jsonify({'error': 'invalid module_id'}), 400

        try:
            progress, first_item = ModuleProgressService.start_module(
                user.user_id, mid
            )
        except ModuleNotAvailableError as e:
            return jsonify({'error': str(e)}), 409
        except ValueError as e:
            return jsonify({'error': str(e)}), 404

        module = Ap2ModuleRepository.find_by_id(mid)
        return jsonify({
            'module': _module_to_dict(module, progress),
            'theory_markdown': module.theory_markdown if module else None,
            'first_item': _item_to_dict(first_item),
        }), 200

    @bp.route('/modules/<module_id>/submit', methods=['POST'])
    @token_required
    def submit_module_answer(module_id):
        user = get_current_user()
        body = request.get_json() or {}

        try:
            mid = UUID(module_id)
            iid = UUID(body['item_id'])
        except (KeyError, ValueError):
            return jsonify({'error': 'item_id required'}), 400

        answer = (body.get('answer') or '').strip()
        if not answer:
            return jsonify({'error': 'answer required'}), 400

        try:
            result = ModuleProgressService.submit_answer(
                user_id=user.user_id,
                module_id=mid,
                item_id=iid,
                user_answer=answer,
                source=AttemptSource.WEBAPP,
            )
        except ModuleNotAvailableError as e:
            return jsonify({'error': str(e)}), 409
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception:
            logger.exception('submit_answer failed')
            return jsonify({'error': 'evaluation failed'}), 500

        feedback = result['feedback']
        return jsonify({
            'pct': result['pct'],
            'passed': result['passed'],
            'points_earned': result['points_earned'],
            'feedback': {
                'summary': feedback.summary,
                'correct_aspects': feedback.correct_aspects,
                'missing_aspects': feedback.missing_aspects,
                'partial_aspects': feedback.partial_aspects,
                'incorrect_aspects': feedback.incorrect_aspects,
                'suggestions': feedback.suggestions,
            },
            'progress': _progress_to_dict(result['progress']),
            'next_item': _item_to_dict(result.get('next_item')),
        }), 200

    @bp.route('/modules/<module_id>/recall-item', methods=['GET'])
    @token_required
    def get_recall_item(module_id):
        user = get_current_user()
        try:
            mid = UUID(module_id)
        except ValueError:
            return jsonify({'error': 'invalid module_id'}), 400
        item = ModuleProgressService.get_recall_item(user.user_id, mid)
        return jsonify({'item': _item_to_dict(item)}), 200

    @bp.route('/modules/<module_id>/spotcheck-item', methods=['GET'])
    @token_required
    def get_spotcheck_item(module_id):
        user = get_current_user()
        try:
            mid = UUID(module_id)
        except ValueError:
            return jsonify({'error': 'invalid module_id'}), 400
        item = ModuleProgressService.get_spotcheck_item(user.user_id, mid)
        return jsonify({'item': _item_to_dict(item)}), 200

    # ============================================================
    # Telegram-Verknüpfung
    # ============================================================

    @bp.route('/telegram/link-code', methods=['POST'])
    @token_required
    def generate_telegram_link_code():
        user = get_current_user()
        code, expires = TelegramLinkRepository.create_link_code(user.user_id)
        return jsonify({
            'code': code,
            'expires_at': expires.isoformat(),
            'bot_username': 'Jozek2026Bot',
            'instruction': (
                f'Öffne Telegram, suche @Jozek2026Bot und sende: /start {code}'
            ),
        }), 200

    @bp.route('/telegram/link', methods=['DELETE'])
    @token_required
    def unlink_telegram():
        user = get_current_user()
        TelegramLinkRepository.unlink_chat(user.user_id)
        return jsonify({'ok': True}), 200

    @bp.route('/telegram/status', methods=['GET'])
    @token_required
    def telegram_status():
        user = get_current_user()
        chat_id = TelegramLinkRepository.get_chat_id(user.user_id)
        return jsonify({
            'linked': chat_id is not None,
            'bot_username': 'Jozek2026Bot',
        }), 200
