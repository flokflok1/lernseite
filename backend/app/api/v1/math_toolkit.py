"""
LernsystemX Math Toolkit API - Consolidated

Calculator Functions:
- POST /math-toolkit/calculator/evaluate - Evaluate mathematical expression
- GET /math-toolkit/calculator/history - Get calculator history
- POST /math-toolkit/calculator/save - Save calculator entry

Reference Library:
- GET /math-toolkit/categories - Get pattern categories
- GET /math-toolkit/patterns - Get calculation patterns (with filters)
- GET /math-toolkit/patterns/<id> - Get pattern details
- GET /math-toolkit/formulas - Get formula library
- POST /math-toolkit/formulas/<id>/favorite - Toggle favorite status
- POST /math-toolkit/formulas/<id>/use - Increment usage counter

Practice Sessions:
- POST /math-toolkit/sessions - Start new practice session
- GET /math-toolkit/sessions/<id> - Get session details
- POST /math-toolkit/sessions/<id>/end - End session
- GET /math-toolkit/sessions/<id>/steps - Get session steps
- POST /math-toolkit/sessions/<id>/steps - Save calculation step

Interactive Learning:
- GET /math-toolkit/progress - Get user progress
- POST /math-toolkit/progress/<pattern_id> - Update user progress
- GET /math-toolkit/hints - Get contextual hints
- GET /math-toolkit/tasks - Get pattern recognition tasks
- POST /math-toolkit/tasks/<id>/check - Check task answer

Admin Functions:
- POST /math-toolkit/admin/patterns - Create new pattern (admin only)
- POST /math-toolkit/admin/formulas - Create new formula (admin only)

All routes: /api/v1/math-toolkit/*
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.math_toolkit_service import MathToolkitService

logger = logging.getLogger(__name__)

math_toolkit_bp = Blueprint('math_toolkit', __name__, url_prefix='/math-toolkit')

__all__ = ['math_toolkit_bp']


# =============================================================================
# CALCULATOR
# =============================================================================

@math_toolkit_bp.route('/calculator/evaluate', methods=['POST'])
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


@math_toolkit_bp.route('/calculator/history', methods=['GET'])
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


@math_toolkit_bp.route('/calculator/save', methods=['POST'])
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
# CATEGORIES
# =============================================================================

@math_toolkit_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """
    Get all pattern categories

    Response:
        {
            "success": true,
            "data": [
                {
                    "category_code": "CALC_BASIC",
                    "name": "Grundrechenarten",
                    "description": "Addition, Subtraktion, Multiplikation, Division"
                }
            ]
        }
    """
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
    """
    Get calculation patterns with optional filters

    Query Parameters:
        category: Filter by category code
        ihk_only: Only IHK-relevant patterns (default: false)
        difficulty: Filter by difficulty (1-5)

    Response:
        {
            "success": true,
            "data": [
                {
                    "pattern_id": "uuid",
                    "pattern_code": "CALC_PERCENT",
                    "name": "Prozentrechnung",
                    "difficulty": 2,
                    "ihk_relevant": true
                }
            ]
        }
    """
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
    """
    Get pattern details with all information

    Response:
        {
            "success": true,
            "data": {
                "pattern_id": "uuid",
                "pattern_code": "CALC_PERCENT",
                "name": "Prozentrechnung",
                "formula_template": "result = base * (percent / 100)",
                "variables": [...],
                "steps_template": [...],
                "difficulty": 2
            }
        }
    """
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
    """
    Get formulas from library

    Query Parameters:
        category: Filter by category code
        favorites: Only show favorites (default: false)

    Response:
        {
            "success": true,
            "data": [
                {
                    "formula_id": "uuid",
                    "name": "Kreisfläche",
                    "formula_text": "A = π * r²",
                    "is_favorite": false
                }
            ]
        }
    """
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
    """
    Toggle favorite status for formula

    Response:
        {
            "success": true,
            "data": {"is_favorite": true}
        }
    """
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
    """
    Increment usage counter for formula

    Response:
        {"success": true}
    """
    try:
        MathToolkitService.increment_formula_usage(formula_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Fehler beim Formel-Use: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# SESSIONS
# =============================================================================

@math_toolkit_bp.route('/sessions', methods=['POST'])
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


@math_toolkit_bp.route('/sessions/<session_id>', methods=['GET'])
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


@math_toolkit_bp.route('/sessions/<session_id>/end', methods=['POST'])
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


@math_toolkit_bp.route('/sessions/<session_id>/steps', methods=['GET'])
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


@math_toolkit_bp.route('/sessions/<session_id>/steps', methods=['POST'])
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

@math_toolkit_bp.route('/progress', methods=['GET'])
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


@math_toolkit_bp.route('/progress/<pattern_id>', methods=['POST'])
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


# =============================================================================
# HINTS
# =============================================================================

@math_toolkit_bp.route('/hints', methods=['GET'])
@jwt_required()
def get_hint():
    """
    Get contextual hints

    Query Parameters:
        pattern_id: Pattern ID (required)
        hint_type: Type of hint (default: step_help)
        level: Scaffolding level (default: 1)
        step: Step number
        error: Error type

    Response:
        {
            "success": true,
            "data": {
                "hint": "Multipliziere zuerst den Grundwert mit dem Prozentsatz..."
            }
        }
    """
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
    """
    Get pattern recognition tasks

    Query Parameters:
        pattern_id: Optional filter by pattern
        type: Task type
        difficulty: Difficulty level (1-5)
        limit: Maximum number of tasks (default: 10)

    Response:
        {
            "success": true,
            "data": [
                {
                    "task_id": "uuid",
                    "task_type": "identify_pattern",
                    "question": "Welches Rechenmuster liegt vor?",
                    "options": [...]
                }
            ]
        }
    """
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
    """
    Check answer for task

    Request Body:
        {"answer": "CALC_PERCENT"}

    Response:
        {
            "success": true,
            "is_correct": true,
            "correct_answer": "CALC_PERCENT",
            "explanation": "..."
        }
    """
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
    """
    Create new calculation pattern (admin only)

    Request Body:
        {
            "pattern_code": "CALC_PERCENT",
            "name": "Prozentrechnung",
            "category_code": "CALC_BASIC",
            "formula_template": "result = base * (percent / 100)",
            "variables": [...],
            "steps_template": [...],
            "description": "...",
            "formula_latex": "...",
            "example_values": {},
            "difficulty": 2,
            "ihk_relevant": true,
            "tags": []
        }

    Response:
        {
            "success": true,
            "data": {"pattern_id": "uuid"}
        }
    """
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
    """
    Create new formula (admin only)

    Request Body:
        {
            "name": "Kreisfläche",
            "formula_text": "A = π * r²",
            "category_code": "GEOM",
            "description": "...",
            "formula_latex": "...",
            "formula_display": "...",
            "variables": [...],
            "example_input": {},
            "example_output": "...",
            "tags": []
        }

    Response:
        {
            "success": true,
            "data": {"formula_id": "uuid"}
        }
    """
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
