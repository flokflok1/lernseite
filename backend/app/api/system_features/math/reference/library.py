"""
MathToolkit API - Reference Module

Endpoints:
- /math-toolkit/categories - Kategorien
- /math-toolkit/patterns - Rechenmuster
- /math-toolkit/formulas - Formel-Bibliothek
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
import logging

from app.api.system_features.math import math_toolkit_bp
from app.services.math_toolkit_service import MathToolkitService

logger = logging.getLogger(__name__)


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
