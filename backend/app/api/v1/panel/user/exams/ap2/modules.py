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
- GET /telegram/status             — Verknüpfungs-Status

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
    Ap2ItemSkillRepository, Ap2LearningItemRepository,
)
from app.infrastructure.persistence.repositories.user import (
    TelegramLinkRepository,
)
from app.domain.models.ap2 import AttemptSource

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


def _skill_to_dict(s) -> dict:
    if not s:
        return {
            'kopf_serie_count': 0,
            'fail_count': 0,
            'effective_target': None,
            'total_attempts': 0,
            'stuetzrad_uses': 0,
            'is_mastered': False,
            'mastered_at': None,
            'snoozed_until': None,
            'last_attempt_at': None,
            'last_score_pct': None,
            'is_in_recovery': False,
            'should_suggest_stuetzrad': False,
            'should_suggest_pause': False,
        }
    return {
        'kopf_serie_count': s.kopf_serie_count,
        'fail_count': s.fail_count,
        'effective_target': s.effective_target,
        'total_attempts': s.total_attempts,
        'stuetzrad_uses': s.stuetzrad_uses,
        'is_mastered': s.is_mastered,
        'mastered_at': s.mastered_at.isoformat() if s.mastered_at else None,
        'snoozed_until': (
            s.snoozed_until.isoformat() if s.snoozed_until else None
        ),
        'last_attempt_at': (
            s.last_attempt_at.isoformat() if s.last_attempt_at else None
        ),
        'last_score_pct': s.last_score_pct,
        'is_in_recovery': s.is_in_recovery,
        'should_suggest_stuetzrad': s.should_suggest_stuetzrad,
        'should_suggest_pause': s.should_suggest_pause,
    }


def _item_with_skill_dict(item, skill) -> dict:
    base = _item_to_dict(item) or {}
    base['skill'] = _skill_to_dict(skill)
    return base


def register_module_routes(bp):
    """Registriert Modul-Routes am ap2_trainer_bp."""

    @bp.route('/modules', methods=['GET'])
    @token_required
    def list_modules():
        user = get_current_user()
        user_id = user['user_id']
        modules = Ap2ModuleRepository.find_all_active()
        all_progress = Ap2ModuleProgressRepository.find_all_for_user(user_id)
        progress_by_module = {p.module_id: p for p in all_progress}

        result = []
        for m in modules:
            p = progress_by_module.get(m.module_id)
            pool_ids = Ap2ModuleRepository.get_pool_item_ids(
                m.module_id, use_in='mastery',
            )
            item_stats = Ap2ItemSkillRepository.module_stats(user_id, pool_ids)
            if not p:
                from app.application.services.ap2.module_progress_service import (
                    ModuleProgressService as MPS,
                )
                init_status = MPS._compute_initial_status(user_id, m)
                entry = {
                    **_module_to_dict(m),
                    'progress': {
                        'status': init_status.value,
                        'streak_count': 0,
                        'total_attempts': 0,
                        'passed_attempts': 0,
                        'cooldown_until': None,
                        'same_day_recall_due_at': None,
                        'mastered_at': None,
                        'spotcheck_stage': 0,
                        'next_spotcheck_at': None,
                    },
                }
            else:
                entry = _module_to_dict(m, p)
            entry['item_stats'] = item_stats
            result.append(entry)

        return jsonify({'modules': result}), 200

    @bp.route('/modules/<module_id>/detail', methods=['GET'])
    @token_required
    def module_detail(module_id):
        """Item-Drilldown: alle Pool-Items + Skill-Status pro User."""
        user = get_current_user()
        user_id = user['user_id']
        try:
            mid = UUID(module_id)
        except ValueError:
            return jsonify({'error': 'invalid module_id'}), 400

        module = Ap2ModuleRepository.find_by_id(mid)
        if not module:
            return jsonify({'error': 'module not found'}), 404

        pool_ids = Ap2ModuleRepository.get_pool_item_ids(mid, use_in='mastery')
        items = Ap2LearningItemRepository.find_by_ids(pool_ids)
        skill_by_item = Ap2ItemSkillRepository.find_for_items(user_id, pool_ids)
        progress = Ap2ModuleProgressRepository.find_by_user_module(user_id, mid)

        return jsonify({
            'module': _module_to_dict(module, progress),
            'theory_markdown': module.theory_markdown,
            'item_stats': Ap2ItemSkillRepository.module_stats(user_id, pool_ids),
            'items': [
                _item_with_skill_dict(i, skill_by_item.get(i.item_id))
                for i in items
            ],
        }), 200

    @bp.route('/modules/<module_id>/start', methods=['POST'])
    @token_required
    def start_module(module_id):
        user = get_current_user()
        user_id = user['user_id']
        try:
            mid = UUID(module_id)
        except ValueError:
            return jsonify({'error': 'invalid module_id'}), 400

        try:
            progress, first_item = ModuleProgressService.start_module(user_id, mid)
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
        user_id = user['user_id']
        body = request.get_json() or {}

        try:
            mid = UUID(module_id)
            iid = UUID(body['item_id'])
        except (KeyError, ValueError):
            return jsonify({'error': 'item_id required'}), 400

        answer = (body.get('answer') or '').strip()
        if not answer:
            return jsonify({'error': 'answer required'}), 400

        stuetzrad_used = bool(body.get('stuetzrad', False))

        try:
            result = ModuleProgressService.submit_answer(
                user_id=user_id,
                module_id=mid,
                item_id=iid,
                user_answer=answer,
                source=AttemptSource.WEBAPP,
                stuetzrad_used=stuetzrad_used,
            )
        except ModuleNotAvailableError as e:
            return jsonify({'error': str(e)}), 409
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception:
            logger.exception('submit_answer failed')
            return jsonify({'error': 'evaluation failed'}), 500

        feedback = result['feedback']
        skill = result['skill']
        return jsonify({
            'pct': result['pct'],
            'passed': result['passed'],
            'points_earned': result['points_earned'],
            'stuetzrad_used': result.get('stuetzrad_used', False),
            'model_answer': result.get('model_answer'),
            'skill': {
                'kopf_serie_count': skill.kopf_serie_count,
                'effective_target': skill.effective_target,
                'fail_count': skill.fail_count,
                'stuetzrad_uses': skill.stuetzrad_uses,
                'is_mastered': skill.is_mastered,
                'should_suggest_stuetzrad': skill.should_suggest_stuetzrad,
                'should_suggest_pause': skill.should_suggest_pause,
            },
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
        user_id = user['user_id']
        try:
            mid = UUID(module_id)
        except ValueError:
            return jsonify({'error': 'invalid module_id'}), 400
        item = ModuleProgressService.get_recall_item(user_id, mid)
        return jsonify({'item': _item_to_dict(item)}), 200

    @bp.route('/modules/<module_id>/spotcheck-item', methods=['GET'])
    @token_required
    def get_spotcheck_item(module_id):
        user = get_current_user()
        user_id = user['user_id']
        try:
            mid = UUID(module_id)
        except ValueError:
            return jsonify({'error': 'invalid module_id'}), 400
        item = ModuleProgressService.get_spotcheck_item(user_id, mid)
        return jsonify({'item': _item_to_dict(item)}), 200

    # ============================================================
    # Telegram-Verknüpfung
    # ============================================================

    @bp.route('/telegram/link-code', methods=['POST'])
    @token_required
    def generate_telegram_link_code():
        user = get_current_user()
        user_id = user['user_id']
        code, expires = TelegramLinkRepository.create_link_code(user_id)
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
        user_id = user['user_id']
        TelegramLinkRepository.unlink_chat(user_id)
        return jsonify({'ok': True}), 200

    @bp.route('/telegram/status', methods=['GET'])
    @token_required
    def telegram_status():
        user = get_current_user()
        user_id = user['user_id']
        chat_id = TelegramLinkRepository.get_chat_id(user_id)
        return jsonify({
            'linked': chat_id is not None,
            'bot_username': 'Jozek2026Bot',
        }), 200
