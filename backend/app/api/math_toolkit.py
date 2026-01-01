"""
MathToolkit API - Endpoints für das Mathe-Lern-System

Endpoints:
- /math-toolkit/categories - Kategorien
- /math-toolkit/patterns - Rechenmuster
- /math-toolkit/formulas - Formel-Bibliothek
- /math-toolkit/calculator - Taschenrechner
- /math-toolkit/sessions - Übungssitzungen
- /math-toolkit/progress - User-Fortschritt
- /math-toolkit/tasks - Muster-Erkennungs-Aufgaben
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.api import api_v1
from app.services.math_toolkit_service import MathToolkitService

logger = logging.getLogger(__name__)

math_toolkit_bp = Blueprint('math_toolkit', __name__, url_prefix='/math-toolkit')

# Register blueprint with main API
api_v1.register_blueprint(math_toolkit_bp)


# =============================================================================
# CATEGORIES
# =============================================================================

@math_toolkit_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Holt alle Muster-Kategorien"""
    try:
        categories = MathToolkitService.get_categories()
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden der Kategorien: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# PATTERNS
# =============================================================================

@math_toolkit_bp.route('/patterns', methods=['GET'])
@jwt_required()
def get_patterns():
    """Holt Rechenmuster mit optionalen Filtern"""
    try:
        category = request.args.get('category')
        ihk_only = request.args.get('ihk_only', 'false').lower() == 'true'
        difficulty = request.args.get('difficulty', type=int)

        patterns = MathToolkitService.get_patterns(
            category_code=category,
            ihk_only=ihk_only,
            difficulty=difficulty
        )
        return jsonify({
            'success': True,
            'data': patterns
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden der Patterns: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@math_toolkit_bp.route('/patterns/<pattern_id>', methods=['GET'])
@jwt_required()
def get_pattern(pattern_id):
    """Holt ein Muster mit allen Details"""
    try:
        pattern = MathToolkitService.get_pattern_by_id(pattern_id)
        if not pattern:
            return jsonify({'success': False, 'error': 'Muster nicht gefunden'}), 404
        return jsonify({
            'success': True,
            'data': pattern
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden des Patterns: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# FORMULAS
# =============================================================================

@math_toolkit_bp.route('/formulas', methods=['GET'])
@jwt_required()
def get_formulas():
    """Holt Formeln aus der Bibliothek"""
    try:
        category = request.args.get('category')
        favorites = request.args.get('favorites', 'false').lower() == 'true'

        formulas = MathToolkitService.get_formulas(
            category_code=category,
            favorites_only=favorites
        )
        return jsonify({
            'success': True,
            'data': formulas
        })
    except Exception as e:
        logger.error(f"Fehler beim Laden der Formeln: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@math_toolkit_bp.route('/formulas/<formula_id>/favorite', methods=['POST'])
@jwt_required()
def toggle_formula_favorite(formula_id):
    """Toggled Favoriten-Status"""
    try:
        new_status = MathToolkitService.toggle_formula_favorite(formula_id)
        if new_status is None:
            return jsonify({'success': False, 'error': 'Formel nicht gefunden'}), 404
        return jsonify({
            'success': True,
            'data': {'is_favorite': new_status}
        })
    except Exception as e:
        logger.error(f"Fehler beim Favoriten-Toggle: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@math_toolkit_bp.route('/formulas/<formula_id>/use', methods=['POST'])
@jwt_required()
def use_formula(formula_id):
    """Erhöht Nutzungszähler"""
    try:
        MathToolkitService.increment_formula_usage(formula_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Fehler beim Formel-Use: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
