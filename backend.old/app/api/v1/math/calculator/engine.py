"""
MathToolkit API - Calculator Module

Endpoints:
- /math-toolkit/calculator/evaluate - Ausdruck auswerten
- /math-toolkit/calculator/history - Verlauf abrufen
- /math-toolkit/calculator/save - Eingabe speichern
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.api.v1.math import math_toolkit_bp
from app.services.math_toolkit_service import MathToolkitService

logger = logging.getLogger(__name__)


# =============================================================================
# CALCULATOR
# =============================================================================

@math_toolkit_bp.route('/calculator/evaluate', methods=['POST'])
@jwt_required()
def evaluate_expression():
    """Wertet mathematischen Ausdruck aus"""
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


@math_toolkit_bp.route('/calculator/history', methods=['GET'])
@jwt_required()
def get_calculator_history():
    """Holt Taschenrechner-Verlauf"""
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


@math_toolkit_bp.route('/calculator/save', methods=['POST'])
@jwt_required()
def save_calculator_entry():
    """Speichert Taschenrechner-Eingabe"""
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
