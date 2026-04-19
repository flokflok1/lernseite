"""
AP2 Trainer API — User Learning Preferences.

Endpoints:
- GET /preferences — aktuelle Lern-Einstellungen (oder Defaults)
- PUT /preferences — base_target, max_target, recovery_mode,
                     stuetzrad_default, mastery_strictness aktualisieren

DDD: API-Layer. Keine SQL, keine Geschäftslogik (nur Repo-Aufrufe).
"""

import logging

from flask import jsonify, request

from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2UserPrefsRepository,
)
from app.domain.models.ap2 import (
    RecoveryMode, StuetzradDefault, MasteryStrictness,
    ABS_MIN_TARGET, ABS_MAX_TARGET,
)

logger = logging.getLogger(__name__)


def _prefs_to_dict(p) -> dict:
    return {
        'base_target': p.base_target,
        'max_target': p.max_target,
        'recovery_mode': p.recovery_mode.value,
        'stuetzrad_default': p.stuetzrad_default.value,
        'mastery_strictness': p.mastery_strictness.value,
    }


def _prefs_meta() -> dict:
    """Enum-Optionen für UI (Dropdowns, Radios)."""
    return {
        'recovery_modes': [m.value for m in RecoveryMode],
        'stuetzrad_defaults': [s.value for s in StuetzradDefault],
        'mastery_strictness_levels': [m.value for m in MasteryStrictness],
        'abs_min_target': ABS_MIN_TARGET,
        'abs_max_target': ABS_MAX_TARGET,
    }


def register_preferences_routes(bp):
    """Registriert Preference-Routes am ap2_trainer_bp."""

    @bp.route('/preferences', methods=['GET'])
    @token_required
    def get_preferences():
        user = get_current_user()
        prefs = Ap2UserPrefsRepository.get_or_create(user['user_id'])
        return jsonify({
            'preferences': _prefs_to_dict(prefs),
            'meta': _prefs_meta(),
        }), 200

    @bp.route('/preferences', methods=['PUT'])
    @token_required
    def update_preferences():
        user = get_current_user()
        body = request.get_json() or {}
        prefs = Ap2UserPrefsRepository.get_or_create(user['user_id'])

        try:
            if 'base_target' in body:
                prefs.base_target = _clamp_target(int(body['base_target']))
            if 'max_target' in body:
                prefs.max_target = _clamp_target(int(body['max_target']))
            if prefs.max_target < prefs.base_target:
                prefs.max_target = prefs.base_target
            if 'recovery_mode' in body:
                prefs.recovery_mode = RecoveryMode(body['recovery_mode'])
            if 'stuetzrad_default' in body:
                prefs.stuetzrad_default = StuetzradDefault(
                    body['stuetzrad_default']
                )
            if 'mastery_strictness' in body:
                prefs.mastery_strictness = MasteryStrictness(
                    body['mastery_strictness']
                )
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'invalid field: {e}'}), 400

        saved = Ap2UserPrefsRepository.upsert(prefs)
        return jsonify({
            'preferences': _prefs_to_dict(saved),
            'meta': _prefs_meta(),
        }), 200


def _clamp_target(v: int) -> int:
    return max(ABS_MIN_TARGET, min(v, ABS_MAX_TARGET))
