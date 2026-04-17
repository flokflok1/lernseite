"""
AP2 Trainer API — Study Flow (Attempts + Sessions + Review-Queue).

Endpoints:
- POST /attempts/submit — Antwort einreichen → KI bewerten → Schedule + Mastery updaten
- GET  /review/queue — Heute fällige Items (SM-2)
- POST /sessions/start — StudySession beginnen
- POST /sessions/<session_id>/end — Session beenden

DDD: API-Layer. Keine SQL, keine Geschäftslogik (nur Service-Aufrufe).
"""

import logging
from uuid import UUID

from flask import jsonify, request

from app.api.middleware.auth import token_required, get_current_user
from app.application.services.ap2 import (
    Ap2AttemptService,
    Ap2SchedulerService,
    Ap2SessionService,
)
from app.domain.models.ap2 import Phase, SessionType

logger = logging.getLogger(__name__)


def register_study_routes(bp):
    """Registriert Study-Flow-Routes am ap2_trainer_bp."""

    @bp.route('/attempts/submit', methods=['POST'])
    @token_required
    def submit_attempt():
        """Verarbeitet einen User-Attempt (Blurt/Cued/Application).

        Body:
          {
            item_id: UUID,
            phase: 'blurt' | 'cued' | 'application',
            answer_text: str,
            answer_hotspots: { hotspot_id: value } | null,
            time_spent_sec: int | null,
            user_quality_override: 0-5 | null,
            session_id: UUID | null  // optional, fügt zu Session hinzu
          }

        Returns:
          { success, attempt_id, pct, points_earned, points_total,
            feedback, mastery_score, next_review_at }
        """
        try:
            user = get_current_user()
            body = request.get_json(force=True, silent=True) or {}

            item_id = _parse_uuid(body.get('item_id'), 'item_id')
            phase = _parse_phase(body.get('phase'))

            result = Ap2AttemptService.submit(
                user_id=user['user_id'],
                item_id=item_id,
                phase=phase,
                answer_text=body.get('answer_text', ''),
                answer_hotspots=body.get('answer_hotspots'),
                time_spent_sec=body.get('time_spent_sec'),
                user_quality_override=body.get('user_quality_override'),
            )

            # Optionales Session-Aggregat updaten
            session_id = body.get('session_id')
            if session_id:
                Ap2SessionService.record_attempt(
                    session_id=UUID(session_id),
                    pct=result.attempt.pct,
                    points_earned=result.attempt.points_earned,
                    points_total=result.attempt.points_total,
                )

            return jsonify({
                'success': True,
                'attempt_id': str(result.attempt.attempt_id),
                'pct': result.attempt.pct,
                'points_earned': result.attempt.points_earned,
                'points_total': result.attempt.points_total,
                'feedback': _feedback_to_dict(result.attempt.feedback_structured),
                'model_answer': result.item.model_answer,
                'mastery_score': result.mastery_score,
                'next_review_at': result.next_review_at.isoformat(),
            }), 200

        except ValueError as ve:
            return jsonify({'success': False, 'error': str(ve)}), 400
        except Exception:
            logger.exception('AP2 submit attempt failed')
            return jsonify({'success': False, 'error': 'submit_failed'}), 500

    @bp.route('/review/queue', methods=['GET'])
    @token_required
    def get_review_queue():
        """Heute fällige Items (SM-2 Spaced Repetition Queue)."""
        try:
            user = get_current_user()
            limit = min(int(request.args.get('limit', 20)), 100)

            items = Ap2SchedulerService.get_due_queue(user['user_id'], limit=limit)
            count = Ap2SchedulerService.count_due(user['user_id'])

            return jsonify({
                'success': True,
                'count_total_due': count,
                'items': [_due_item_to_dict(r) for r in items],
            }), 200
        except Exception:
            logger.exception('AP2 review queue failed')
            return jsonify({'success': False, 'error': 'queue_failed'}), 500

    @bp.route('/sessions/start', methods=['POST'])
    @token_required
    def start_session():
        """Startet eine neue StudySession."""
        try:
            user = get_current_user()
            body = request.get_json(force=True, silent=True) or {}

            session_type = SessionType(body.get('session_type', 'topic_study'))
            topic_id = body.get('topic_id')
            metadata = body.get('metadata')

            session = Ap2SessionService.start(
                user_id=user['user_id'],
                session_type=session_type,
                topic_id=UUID(topic_id) if topic_id else None,
                metadata=metadata,
            )
            return jsonify({
                'success': True,
                'session_id': str(session.session_id),
                'started_at': session.started_at.isoformat(),
            }), 201
        except ValueError as ve:
            return jsonify({'success': False, 'error': str(ve)}), 400
        except Exception:
            logger.exception('AP2 start session failed')
            return jsonify({'success': False, 'error': 'session_start_failed'}), 500

    @bp.route('/sessions/<session_id>/end', methods=['POST'])
    @token_required
    def end_session(session_id: str):
        """Beendet eine StudySession."""
        try:
            Ap2SessionService.end(UUID(session_id))
            return jsonify({'success': True}), 200
        except ValueError as ve:
            return jsonify({'success': False, 'error': str(ve)}), 400
        except Exception:
            logger.exception('AP2 end session failed for id=%s', session_id)
            return jsonify({'success': False, 'error': 'session_end_failed'}), 500


def _parse_uuid(value, field_name: str) -> UUID:
    if not value:
        raise ValueError(f'{field_name} is required')
    return UUID(value)


def _parse_phase(value) -> Phase:
    if not value:
        raise ValueError('phase is required')
    return Phase(value)


def _feedback_to_dict(fb) -> dict:
    if fb is None:
        return {'summary': '', 'correct_aspects': [], 'missing_aspects': [],
                'partial_aspects': [], 'incorrect_aspects': [], 'suggestions': []}
    return {
        'summary': fb.summary,
        'correct_aspects': fb.correct_aspects,
        'missing_aspects': fb.missing_aspects,
        'partial_aspects': fb.partial_aspects,
        'incorrect_aspects': fb.incorrect_aspects,
        'suggestions': fb.suggestions,
    }


def _due_item_to_dict(r: dict) -> dict:
    """Joined-Row aus Repository in API-Format."""
    return {
        'item_id': str(r['item_id']),
        'topic_id': str(r['topic_id']),
        'topic_name': r['topic_name'],
        'topic_bereich': r['topic_bereich'],
        'item_type': r['item_type'],
        'prompt': r['prompt'],
        'points': float(r['points']),
        'difficulty': r['difficulty'],
        'estimated_time_sec': r['estimated_time_sec'],
        'next_review_at': r['next_review_at'].isoformat() if r['next_review_at'] else None,
        'repetitions': r['repetitions'],
    }
