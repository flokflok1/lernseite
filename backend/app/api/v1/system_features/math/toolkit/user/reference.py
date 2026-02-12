"""
LernsystemX Math Toolkit - Reference Library Module

Reference library and hints endpoints for mathematical patterns and formulas.

Reference Library:
- GET /math-toolkit/categories - Get pattern categories
- GET /math-toolkit/patterns - Get calculation patterns (with filters)
- GET /math-toolkit/patterns/<id> - Get pattern details
- GET /math-toolkit/formulas - Get formula library
- POST /math-toolkit/formulas/<id>/favorite - Toggle favorite status
- POST /math-toolkit/formulas/<id>/use - Increment usage counter
- GET /math-toolkit/hints - Get contextual hints

All routes: /api/v1/math-toolkit/*
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.application.services.math_toolkit.service import MathToolkitService

logger = logging.getLogger(__name__)

reference_bp = Blueprint('math_toolkit_reference', __name__, url_prefix='/math-toolkit')

__all__ = ['math_toolkit_reference_bp']


# =============================================================================
# CATEGORIES
# =============================================================================

@reference_bp.route('/categories', methods=['GET'])
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

@reference_bp.route('/patterns', methods=['GET'])
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


@reference_bp.route('/patterns/<pattern_id>', methods=['GET'])
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

@reference_bp.route('/formulas', methods=['GET'])
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


@reference_bp.route('/formulas/<formula_id>/favorite', methods=['POST'])
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


@reference_bp.route('/formulas/<formula_id>/use', methods=['POST'])
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
# HINTS
# =============================================================================

@reference_bp.route('/hints', methods=['GET'])
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
