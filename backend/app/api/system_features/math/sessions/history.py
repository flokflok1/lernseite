"""
MathToolkit API - Sessions Module

Endpoints:
- /math-toolkit/sessions - Übungssitzungen starten
- /math-toolkit/sessions/<id> - Session abrufen
- /math-toolkit/sessions/<id>/end - Session beenden
- /math-toolkit/sessions/<id>/steps - Schritte abrufen/speichern
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.api.system_features.math import math_toolkit_bp
from app.services.math_toolkit_service import MathToolkitService

logger = logging.getLogger(__name__)


# =============================================================================
# SESSIONS
# =============================================================================

@math_toolkit_bp.route('/sessions', methods=['POST'])
@jwt_required()
def start_session():
    """Startet eine neue Toolkit-Session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        session_id = MathToolkitService.start_session(
            user_id=user_id,
            session_type=data.get('session_type', 'practice'),
            pattern_id=data.get('pattern_id'),
            scaffolding_level=data.get('scaffolding_level', 1),
            course_id=data.get('course_id'),
            lesson_id=data.get('lesson_id')
        )

        if not session_id:
            return jsonify({'success': False, 'error': 'Session konnte nicht erstellt werden'}), 500

        return jsonify({
            'success': True,
            'data': {'session_id': session_id}
        })
    except Exception as e:
        logger.error(f"Fehler beim Starten der Session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@math_toolkit_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """Holt Session-Details"""
    try:
        session = MathToolkitService.get_session(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session nicht gefunden'}), 404
        return jsonify({
            'success': True,
            'data': session
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden der Session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@math_toolkit_bp.route('/sessions/<session_id>/end', methods=['POST'])
@jwt_required()
def end_session(session_id):
    """Beendet eine Session"""
    try:
        MathToolkitService.end_session(session_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Fehler beim Beenden der Session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@math_toolkit_bp.route('/sessions/<session_id>/steps', methods=['GET'])
@jwt_required()
def get_session_steps(session_id):
    """Holt alle Schritte einer Session"""
    try:
        steps = MathToolkitService.get_session_steps(session_id)
        return jsonify({
            'success': True,
            'data': steps
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden der Schritte: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@math_toolkit_bp.route('/sessions/<session_id>/steps', methods=['POST'])
@jwt_required()
def save_session_step(session_id):
    """Speichert einen Rechenschritt"""
    try:
        data = request.get_json() or {}

        step_id = MathToolkitService.save_calculation_step(
            session_id=session_id,
            step_number=data.get('step_number', 1),
            input_expression=data.get('input_expression', ''),
            input_values=data.get('input_values'),
            result_value=data.get('result_value'),
            result_display=data.get('result_display'),
            calculator_keystrokes=data.get('calculator_keystrokes'),
            is_correct=data.get('is_correct'),
            expected_value=data.get('expected_value'),
            error_type=data.get('error_type'),
            hint_shown=data.get('hint_shown')
        )
        return jsonify({
            'success': True,
            'data': {'step_id': step_id}
        })
    except Exception as e:
        logger.error(f"Fehler beim Speichern des Schritts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
