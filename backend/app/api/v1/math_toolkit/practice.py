"""
LernsystemX Math Toolkit - Practice Module

Practice session management and calculator operations.

Calculator Functions:
- POST /math-toolkit/calculator/evaluate - Evaluate mathematical expression
- GET /math-toolkit/calculator/history - Get calculator history
- POST /math-toolkit/calculator/save - Save calculator entry

Practice Sessions:
- POST /math-toolkit/sessions - Start new practice session
- GET /math-toolkit/sessions/<id> - Get session details
- POST /math-toolkit/sessions/<id>/end - End session
- GET /math-toolkit/sessions/<id>/steps - Get session steps
- POST /math-toolkit/sessions/<id>/steps - Save calculation step

Interactive Learning:
- GET /math-toolkit/progress - Get user progress
- POST /math-toolkit/progress/<pattern_id> - Update user progress

All routes: /api/v1/math-toolkit/*
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.application.services.math_toolkit_service import MathToolkitService

logger = logging.getLogger(__name__)

practice_bp = Blueprint('math_toolkit_practice', __name__, url_prefix='/math-toolkit')

__all__ = ['math_toolkit_practice_bp']


# =============================================================================
# CALCULATOR
# =============================================================================

@practice_bp.route('/calculator/evaluate', methods=['POST'])
@jwt_required()
def evaluate_expression():
    """
    Evaluate mathematical expression

    Request Body:
        {
            "expression": "2 * (3 + 4)"
        }

    Response:
        {
            "success": true,
            "result": 14,
            "expression": "2 * (3 + 4)"
        }
    """
    try:
        data = request.get_json() or {}
        expression = data.get('expression', '')

        if not expression:
            return jsonify({'success': False, 'error': 'Kein Ausdruck angegeben'}), 400

        result = MathToolkitService.evaluate_expression(expression)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Fehler bei Auswertung: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@practice_bp.route('/calculator/history', methods=['GET'])
@jwt_required()
def get_calculator_history():
    """
    Get calculator history for current user

    Query Parameters:
        limit: Maximum number of entries (default: 50)

    Response:
        {
            "success": true,
            "data": [
                {
                    "history_id": 1,
                    "expression": "2 + 2",
                    "result": 4,
                    "created_at": "2025-01-12T10:00:00"
                }
            ]
        }
    """
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 50, type=int)

        history = MathToolkitService.get_calculator_history(user_id, limit)
        return jsonify({
            'success': True,
            'data': history
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden des Verlaufs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@practice_bp.route('/calculator/save', methods=['POST'])
@jwt_required()
def save_calculator_entry():
    """
    Save calculator entry

    Request Body:
        {
            "expression": "2 + 2",
            "result": 4,
            "result_display": "4",
            "session_id": "uuid",
            "keystrokes": ["2", "+", "2", "="],
            "memory_used": false,
            "memory_value": null
        }

    Response:
        {
            "success": true,
            "data": {"history_id": 123}
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        history_id = MathToolkitService.save_calculator_entry(
            user_id=user_id,
            expression=data.get('expression', ''),
            result=data.get('result'),
            result_display=data.get('result_display', ''),
            session_id=data.get('session_id'),
            keystrokes=data.get('keystrokes', []),
            memory_used=data.get('memory_used', False),
            memory_value=data.get('memory_value')
        )
        return jsonify({
            'success': True,
            'data': {'history_id': history_id}
        })
    except Exception as e:
        logger.error(f"Fehler beim Speichern: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# SESSIONS
# =============================================================================

@practice_bp.route('/sessions', methods=['POST'])
@jwt_required()
def start_session():
    """
    Start new practice session

    Request Body:
        {
            "session_type": "practice",
            "pattern_id": "uuid",
            "scaffolding_level": 1,
            "course_id": "uuid",
            "lesson_id": 123
        }

    Response:
        {
            "success": true,
            "data": {"session_id": "uuid"}
        }
    """
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


@practice_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """
    Get session details

    Response:
        {
            "success": true,
            "data": {
                "session_id": "uuid",
                "user_id": "uuid",
                "session_type": "practice",
                "started_at": "2025-01-12T10:00:00",
                "ended_at": null
            }
        }
    """
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


@practice_bp.route('/sessions/<session_id>/end', methods=['POST'])
@jwt_required()
def end_session(session_id):
    """
    End practice session

    Response:
        {"success": true}
    """
    try:
        MathToolkitService.end_session(session_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Fehler beim Beenden der Session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@practice_bp.route('/sessions/<session_id>/steps', methods=['GET'])
@jwt_required()
def get_session_steps(session_id):
    """
    Get all steps from a session

    Response:
        {
            "success": true,
            "data": [
                {
                    "step_id": "uuid",
                    "step_number": 1,
                    "input_expression": "2 + 2",
                    "result_value": 4,
                    "is_correct": true
                }
            ]
        }
    """
    try:
        steps = MathToolkitService.get_session_steps(session_id)
        return jsonify({
            'success': True,
            'data': steps
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden der Schritte: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@practice_bp.route('/sessions/<session_id>/steps', methods=['POST'])
@jwt_required()
def save_session_step(session_id):
    """
    Save calculation step

    Request Body:
        {
            "step_number": 1,
            "input_expression": "2 + 2",
            "input_values": {},
            "result_value": 4,
            "result_display": "4",
            "calculator_keystrokes": ["2", "+", "2", "="],
            "is_correct": true,
            "expected_value": 4,
            "error_type": null,
            "hint_shown": false
        }

    Response:
        {
            "success": true,
            "data": {"step_id": "uuid"}
        }
    """
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


# =============================================================================
# PROGRESS
# =============================================================================

@practice_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_user_progress():
    """
    Get user progress

    Query Parameters:
        pattern_id: Optional filter by pattern

    Response:
        {
            "success": true,
            "data": {
                "overall_level": 3,
                "patterns": [
                    {
                        "pattern_id": "uuid",
                        "current_level": 2,
                        "correct_count": 15,
                        "incorrect_count": 3
                    }
                ]
            }
        }
    """
    try:
        user_id = get_jwt_identity()
        pattern_id = request.args.get('pattern_id')

        progress = MathToolkitService.get_user_progress(user_id, pattern_id)
        return jsonify({
            'success': True,
            'data': progress
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden des Fortschritts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@practice_bp.route('/progress/<pattern_id>', methods=['POST'])
@jwt_required()
def update_user_progress(pattern_id):
    """
    Update user progress for pattern

    Request Body:
        {
            "is_correct": true,
            "update_level": true
        }

    Response:
        {
            "success": true,
            "data": {
                "pattern_id": "uuid",
                "current_level": 3,
                "correct_count": 16
            }
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        progress = MathToolkitService.update_user_progress(
            user_id=user_id,
            pattern_id=pattern_id,
            is_correct=data.get('is_correct', False),
            update_level=data.get('update_level', True)
        )
        return jsonify({
            'success': True,
            'data': progress
        })
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Fortschritts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
