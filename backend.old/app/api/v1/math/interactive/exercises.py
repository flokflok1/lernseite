"""
MathToolkit API - Interactive Module

Endpoints:
- /math-toolkit/progress - User-Fortschritt
- /math-toolkit/hints - Hilfestellungen
- /math-toolkit/tasks - Muster-Erkennungs-Aufgaben
- /math-toolkit/admin/* - Admin-Funktionen
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.api.v1.math import math_toolkit_bp
from app.services.math_toolkit_service import MathToolkitService

logger = logging.getLogger(__name__)


# =============================================================================
# PROGRESS
# =============================================================================

@math_toolkit_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_user_progress():
    """Holt User-Fortschritt"""
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


@math_toolkit_bp.route('/progress/<pattern_id>', methods=['POST'])
@jwt_required()
def update_user_progress(pattern_id):
    """Aktualisiert User-Fortschritt"""
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


# =============================================================================
# HINTS
# =============================================================================

@math_toolkit_bp.route('/hints', methods=['GET'])
@jwt_required()
def get_hint():
    """Holt passenden Hint"""
    try:
        pattern_id = request.args.get('pattern_id')
        hint_type = request.args.get('hint_type', 'step_help')
        level = request.args.get('level', 1, type=int)
        step = request.args.get('step', type=int)
        error = request.args.get('error')

        if not pattern_id:
            return jsonify({'success': False, 'error': 'pattern_id erforderlich'}), 400

        hint = MathToolkitService.get_hint(
            pattern_id=pattern_id,
            hint_type=hint_type,
            scaffolding_level=level,
            step_number=step,
            error_type=error
        )
        return jsonify({
            'success': True,
            'data': {'hint': hint}
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden des Hints: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# PATTERN RECOGNITION TASKS
# =============================================================================

@math_toolkit_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Holt Muster-Erkennungs-Aufgaben"""
    try:
        pattern_id = request.args.get('pattern_id')
        task_type = request.args.get('type')
        difficulty = request.args.get('difficulty', type=int)
        limit = request.args.get('limit', 10, type=int)

        tasks = MathToolkitService.get_pattern_tasks(
            pattern_id=pattern_id,
            task_type=task_type,
            difficulty=difficulty,
            limit=limit
        )
        return jsonify({
            'success': True,
            'data': tasks
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden der Tasks: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@math_toolkit_bp.route('/tasks/<task_id>/check', methods=['POST'])
@jwt_required()
def check_task_answer(task_id):
    """Prüft Antwort auf eine Aufgabe"""
    try:
        data = request.get_json() or {}
        answer = data.get('answer')

        result = MathToolkitService.check_pattern_task_answer(task_id, answer)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Fehler beim Prüfen der Antwort: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================

@math_toolkit_bp.route('/admin/patterns', methods=['POST'])
@jwt_required()
def create_pattern():
    """Erstellt neues Rechenmuster (Admin)"""
    try:
        # TODO: Admin-Check
        data = request.get_json() or {}

        pattern_id = MathToolkitService.create_pattern(
            pattern_code=data.get('pattern_code'),
            name=data.get('name'),
            category_code=data.get('category_code'),
            formula_template=data.get('formula_template'),
            variables=data.get('variables', []),
            steps_template=data.get('steps_template', []),
            description=data.get('description'),
            formula_latex=data.get('formula_latex'),
            example_values=data.get('example_values', {}),
            difficulty=data.get('difficulty', 1),
            ihk_relevant=data.get('ihk_relevant', False),
            tags=data.get('tags', [])
        )

        if not pattern_id:
            return jsonify({'success': False, 'error': 'Pattern konnte nicht erstellt werden'}), 500

        return jsonify({
            'success': True,
            'data': {'pattern_id': pattern_id}
        })
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Patterns: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@math_toolkit_bp.route('/admin/formulas', methods=['POST'])
@jwt_required()
def create_formula():
    """Erstellt neue Formel (Admin)"""
    try:
        # TODO: Admin-Check
        data = request.get_json() or {}

        formula_id = MathToolkitService.create_formula(
            name=data.get('name'),
            formula_text=data.get('formula_text'),
            category_code=data.get('category_code'),
            description=data.get('description'),
            formula_latex=data.get('formula_latex'),
            formula_display=data.get('formula_display'),
            variables=data.get('variables', []),
            example_input=data.get('example_input', {}),
            example_output=data.get('example_output'),
            tags=data.get('tags', [])
        )

        if not formula_id:
            return jsonify({'success': False, 'error': 'Formel konnte nicht erstellt werden'}), 500

        return jsonify({
            'success': True,
            'data': {'formula_id': formula_id}
        })
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Formel: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
