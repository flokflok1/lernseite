"""
LernsystemX Math Toolkit - Admin Module

Administrative endpoints for pattern and formula management.

Admin Functions:
- POST /math-toolkit/admin/patterns - Create new pattern (admin only)
- POST /math-toolkit/admin/formulas - Create new formula (admin only)

All routes: /api/v1/math-toolkit/*
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.application.services.content.lm.math_toolkit import MathToolkitService

logger = logging.getLogger(__name__)

admin_bp = Blueprint('math_toolkit_admin', __name__, url_prefix='/math-toolkit')

__all__ = ['math_toolkit_admin_bp']


# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================

@admin_bp.route('/admin/patterns', methods=['POST'])
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


@admin_bp.route('/admin/formulas', methods=['POST'])
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
