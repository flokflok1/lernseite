"""
Admin Math Routes (Journey-Based API)

Admin journey for math toolkit management.
ALL data loaded dynamically from database - NO hardcoded values.

Endpoints:
- GET /api/v1/admin/math/categories - List pattern categories
- GET /api/v1/admin/math/categories/<id> - Get category details
- GET /api/v1/admin/math/patterns - List patterns
- GET /api/v1/admin/math/patterns/<id> - Get pattern details
- GET /api/v1/admin/math/formulas - List formulas
- GET /api/v1/admin/math/formulas/<id> - Get formula details
- GET /api/v1/admin/math/sessions - List sessions
- GET /api/v1/admin/math/sessions/<id> - Get session details
- GET /api/v1/admin/math/users/<user_id>/progress - Get user progress
"""

from flask import Blueprint, request, jsonify
from src.core.auth.permissions import require_auth, require_role
from src.api.content.math.application.services.math_service import MathService
from src.core.utils.validators import Validators, ValidationError


# Create blueprint
admin_math_bp = Blueprint('admin_math', __name__)


# ============================================================================
# PATTERN CATEGORIES
# ============================================================================

@admin_math_bp.route('/api/v1/admin/math/categories', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def list_math_categories():
    """List all math pattern categories (e.g., Prozent, Kalkulation, Zins)."""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        categories = MathService.list_categories(active_only=active_only)

        categories_data = [
            {
                'category_id': c.category_id,
                'category_code': c.category_code,
                'name': c.name,
                'description': c.description,
                'icon': c.icon,
                'color': c.color,
                'sort_order': c.sort_order,
                'is_active': c.is_active,
                'created_at': c.created_at.isoformat() if c.created_at else None
            }
            for c in categories
        ]

        return jsonify({
            'success': True,
            'data': categories_data,
            'meta': {'count': len(categories_data)}
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_CATEGORIES_ERROR', 'message': str(e)}}), 500


@admin_math_bp.route('/api/v1/admin/math/categories/<category_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_math_category(category_id: str):
    """Get math pattern category details by ID."""
    try:
        Validators.validate_uuid(category_id)
        category = MathService.get_category_by_id(category_id)

        if not category:
            return jsonify({'success': False, 'error': {'code': 'CATEGORY_NOT_FOUND', 'message': f'Category {category_id} not found'}}), 404

        category_data = {
            'category_id': category.category_id,
            'category_code': category.category_code,
            'name': category.name,
            'description': category.description,
            'icon': category.icon,
            'color': category.color,
            'sort_order': category.sort_order,
            'is_active': category.is_active,
            'created_at': category.created_at.isoformat() if category.created_at else None,
            'updated_at': category.updated_at.isoformat() if category.updated_at else None
        }

        return jsonify({'success': True, 'data': category_data}), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_CATEGORY_ERROR', 'message': str(e)}}), 500


# ============================================================================
# PATTERNS
# ============================================================================

@admin_math_bp.route('/api/v1/admin/math/patterns', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def list_math_patterns():
    """
    List all math patterns (e.g., Bezugskalkulation, Prozentrechnung, Dreisatz).

    Query params:
    - category_id: Filter by category
    - difficulty: Filter by difficulty (1-5)
    - ihk_relevant: Filter by IHK relevance (true/false)
    - active_only: Only active patterns (default: true)
    - limit: Result limit (default: 100)
    - offset: Result offset (default: 0)
    """
    try:
        category_id = request.args.get('category_id')
        difficulty = request.args.get('difficulty', type=int)
        ihk_relevant = request.args.get('ihk_relevant', '').lower() == 'true' if request.args.get('ihk_relevant') else None
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        patterns = MathService.list_patterns(
            category_id=category_id,
            difficulty=difficulty,
            ihk_relevant=ihk_relevant,
            active_only=active_only,
            limit=limit,
            offset=offset
        )

        patterns_data = [
            {
                'pattern_id': p.pattern_id,
                'category_id': p.category_id,
                'pattern_code': p.pattern_code,
                'name': p.name,
                'description': p.description,
                'formula_template': p.formula_template,
                'difficulty': p.difficulty,
                'ihk_relevant': p.ihk_relevant,
                'tags': p.tags,
                'is_active': p.is_active,
                'created_at': p.created_at.isoformat() if p.created_at else None
            }
            for p in patterns
        ]

        return jsonify({
            'success': True,
            'data': patterns_data,
            'meta': {'count': len(patterns_data), 'limit': limit, 'offset': offset}
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_PATTERNS_ERROR', 'message': str(e)}}), 500


@admin_math_bp.route('/api/v1/admin/math/patterns/<pattern_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_math_pattern(pattern_id: str):
    """Get math pattern details by ID with full variables and steps."""
    try:
        Validators.validate_uuid(pattern_id)
        pattern = MathService.get_pattern_by_id(pattern_id)

        if not pattern:
            return jsonify({'success': False, 'error': {'code': 'PATTERN_NOT_FOUND', 'message': f'Pattern {pattern_id} not found'}}), 404

        pattern_data = {
            'pattern_id': pattern.pattern_id,
            'category_id': pattern.category_id,
            'pattern_code': pattern.pattern_code,
            'name': pattern.name,
            'description': pattern.description,
            'formula_template': pattern.formula_template,
            'formula_latex': pattern.formula_latex,
            'variables': pattern.variables,
            'steps_template': pattern.steps_template,
            'example_values': pattern.example_values,
            'difficulty': pattern.difficulty,
            'ihk_relevant': pattern.ihk_relevant,
            'tags': pattern.tags,
            'sort_order': pattern.sort_order,
            'is_active': pattern.is_active,
            'created_at': pattern.created_at.isoformat() if pattern.created_at else None,
            'updated_at': pattern.updated_at.isoformat() if pattern.updated_at else None
        }

        return jsonify({'success': True, 'data': pattern_data}), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_PATTERN_ERROR', 'message': str(e)}}), 500


# ============================================================================
# FORMULAS
# ============================================================================

@admin_math_bp.route('/api/v1/admin/math/formulas', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def list_math_formulas():
    """
    List all math formulas from formula library.

    Query params:
    - category_id: Filter by category
    - pattern_id: Filter by pattern
    - favorites_only: Only favorite formulas (default: false)
    - active_only: Only active formulas (default: true)
    - limit: Result limit (default: 100)
    - offset: Result offset (default: 0)
    """
    try:
        category_id = request.args.get('category_id')
        pattern_id = request.args.get('pattern_id')
        favorites_only = request.args.get('favorites_only', 'false').lower() == 'true'
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        formulas = MathService.list_formulas(
            category_id=category_id,
            pattern_id=pattern_id,
            favorites_only=favorites_only,
            active_only=active_only,
            limit=limit,
            offset=offset
        )

        formulas_data = [
            {
                'formula_id': f.formula_id,
                'category_id': f.category_id,
                'pattern_id': f.pattern_id,
                'name': f.name,
                'formula_text': f.formula_text,
                'formula_latex': f.formula_latex,
                'is_favorite': f.is_favorite,
                'usage_count': f.usage_count,
                'tags': f.tags,
                'created_at': f.created_at.isoformat() if f.created_at else None
            }
            for f in formulas
        ]

        return jsonify({
            'success': True,
            'data': formulas_data,
            'meta': {'count': len(formulas_data), 'limit': limit, 'offset': offset}
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_FORMULAS_ERROR', 'message': str(e)}}), 500


@admin_math_bp.route('/api/v1/admin/math/formulas/<formula_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_math_formula(formula_id: str):
    """Get math formula details by ID."""
    try:
        Validators.validate_uuid(formula_id)
        formula = MathService.get_formula_by_id(formula_id)

        if not formula:
            return jsonify({'success': False, 'error': {'code': 'FORMULA_NOT_FOUND', 'message': f'Formula {formula_id} not found'}}), 404

        formula_data = {
            'formula_id': formula.formula_id,
            'category_id': formula.category_id,
            'pattern_id': formula.pattern_id,
            'name': formula.name,
            'description': formula.description,
            'formula_text': formula.formula_text,
            'formula_latex': formula.formula_latex,
            'formula_display': formula.formula_display,
            'variables': formula.variables,
            'example_input': formula.example_input,
            'example_output': formula.example_output,
            'tags': formula.tags,
            'is_favorite': formula.is_favorite,
            'usage_count': formula.usage_count,
            'sort_order': formula.sort_order,
            'is_active': formula.is_active,
            'created_at': formula.created_at.isoformat() if formula.created_at else None
        }

        return jsonify({'success': True, 'data': formula_data}), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_FORMULA_ERROR', 'message': str(e)}}), 500


# ============================================================================
# SESSIONS & PROGRESS
# ============================================================================

@admin_math_bp.route('/api/v1/admin/math/users/<user_id>/progress', methods=['GET'])
@require_auth
@require_role(['admin', 'moderator'])
def get_user_math_progress(user_id: str):
    """Get user's math progress for all patterns (admin view)."""
    try:
        Validators.validate_uuid(user_id)

        progress_list = MathService.get_all_user_progress(user_id)

        progress_data = [
            {
                'progress_id': p.progress_id,
                'pattern_id': p.pattern_id,
                'current_level': p.current_level,
                'total_attempts': p.total_attempts,
                'correct_attempts': p.correct_attempts,
                'mastery_score': float(p.mastery_score),
                'current_streak': p.current_streak,
                'best_streak': p.best_streak,
                'accuracy': p.get_accuracy(),
                'last_practiced_at': p.last_practiced_at.isoformat() if p.last_practiced_at else None,
                'next_review_at': p.next_review_at.isoformat() if p.next_review_at else None
            }
            for p in progress_list
        ]

        return jsonify({
            'success': True,
            'data': progress_data,
            'meta': {'user_id': user_id, 'count': len(progress_data)}
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_PROGRESS_ERROR', 'message': str(e)}}), 500
