"""
LernsystemX Math Toolkit - Tasks Module

Pattern recognition tasks and validation endpoints.

Pattern Recognition Tasks:
- GET /math-toolkit/tasks - Get pattern recognition tasks
- POST /math-toolkit/tasks/<id>/check - Check task answer

All routes: /api/v1/math-toolkit/*
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.application.services.lm.math_toolkit import MathToolkitService

logger = logging.getLogger(__name__)

tasks_bp = Blueprint('math_toolkit_tasks', __name__, url_prefix='/math-toolkit')

__all__ = ['math_toolkit_tasks_bp']


# =============================================================================
# PATTERN RECOGNITION TASKS
# =============================================================================

@tasks_bp.route('/tasks', methods=['GET'])
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


@tasks_bp.route('/tasks/<task_id>/check', methods=['POST'])
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
