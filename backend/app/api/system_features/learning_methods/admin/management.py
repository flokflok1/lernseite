"""
LernsystemX Learning Methods API - Admin Endpoints

Admin-only endpoints for learning method management:
- POST   /api/v1/learning-methods             - Create method
- PUT    /api/v1/learning-methods/:id         - Update method
- DELETE /api/v1/learning-methods/:id         - Delete method
- GET    /api/v1/learning-methods/stats       - Get statistics
- POST   /api/v1/learning-methods/:id/activate   - Activate method
- POST   /api/v1/learning-methods/:id/deactivate - Deactivate method

ISO 27001:2013 compliant - AI execution security and token management
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint

from .._helpers import (
    request,
    jsonify,
    ValidationError,
    LearningMethodCreate,
    LearningMethodUpdate,
    LearningMethodRepository,
    admin_required,
)

# Blueprint for admin learning method endpoints
lm_admin_bp = Blueprint(
    'learning_methods_admin',
    __name__,
    url_prefix='/learning-methods'
)


@lm_admin_bp.route('', methods=['POST'])
@admin_required
def create_learning_method():
    """
    Create new learning method (admin only)

    Request Body:
        {
            "name": "Advanced Quiz",
            "description": "Quiz with adaptive difficulty",
            "tier": "premium",
            "config": {
                "ai_enabled": true,
                "adaptive_difficulty": true,
                "max_questions": 100,
                "ai_model": "gpt-4o-mini",
                "ai_provider": "openai"
            },
            "active": true
        }

    Response:
        201: Method created
        400: Validation error
        403: Insufficient permissions
    """
    try:
        data = request.get_json()

        # Validate with Pydantic
        method_data = LearningMethodCreate(**data)

        # Check if method with same name exists
        existing = LearningMethodRepository.find_by_name(method_data.name)
        if existing:
            return jsonify({
                'success': False,
                'error': 'Learning method already exists',
                'message': f'A method named "{method_data.name}" already exists'
            }), 400

        # Create method
        method = LearningMethodRepository.create(method_data.model_dump())

        return jsonify({
            'success': True,
            'message': 'Learning method created successfully',
            'method': method
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to create learning method',
            'details': str(e)
        }), 500


@lm_admin_bp.route('/<string:method_id>', methods=['PUT'])
@admin_required
def update_learning_method(method_id: str):
    """
    Update learning method (admin only)

    Request Body: Partial update data
        {
            "description": "Updated description",
            "config": {...},
            "active": true
        }

    Response:
        200: Method updated
        400: Validation error
        403: Insufficient permissions
        404: Method not found
    """
    try:
        method = LearningMethodRepository.find_by_id(method_id)

        if not method:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        data = request.get_json()

        # Validate with Pydantic
        method_data = LearningMethodUpdate(**data)

        # Update method
        updated_method = LearningMethodRepository.update(
            method_id,
            method_data.model_dump(exclude_none=True)
        )

        return jsonify({
            'success': True,
            'message': 'Learning method updated successfully',
            'method': updated_method
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update learning method',
            'details': str(e)
        }), 500


@lm_admin_bp.route('/<string:method_id>', methods=['DELETE'])
@admin_required
def delete_learning_method(method_id: str):
    """
    Delete learning method (admin only)

    WARNING: Hard delete. Use deactivate instead for methods in use.

    Response:
        200: Method deleted
        403: Insufficient permissions
        404: Method not found
    """
    try:
        method = LearningMethodRepository.find_by_id(method_id)

        if not method:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        # Delete method
        LearningMethodRepository.delete(method_id)

        return jsonify({
            'success': True,
            'message': 'Learning method deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete learning method',
            'details': str(e)
        }), 500


@lm_admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_learning_method_stats():
    """
    Get overall learning method statistics (admin only)

    Response:
        200: Statistics
        {
            "success": true,
            "stats": {
                "total_methods": 21,
                "active_methods": 21,
                "by_tier": {"basic": 11, "premium": 6, "pro": 4},
                "ai_powered_count": 10,
                "most_used": "Flashcards",
                "total_executions": 12567,
                "total_tokens": 2500000,
                "total_cost_eur": 125.50
            }
        }
    """
    try:
        stats = LearningMethodRepository.get_statistics()

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get statistics',
            'details': str(e)
        }), 500


@lm_admin_bp.route('/<string:method_id>/activate', methods=['POST'])
@admin_required
def activate_learning_method(method_id: str):
    """
    Activate learning method (admin only)

    Path Parameters:
        method_id: Learning method ID

    Response:
        200: Method activated
        404: Method not found
    """
    try:
        method = LearningMethodRepository.find_by_id(method_id)

        if not method:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        updated_method = LearningMethodRepository.activate(method_id)

        return jsonify({
            'success': True,
            'message': 'Learning method activated successfully',
            'method': updated_method
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to activate learning method',
            'details': str(e)
        }), 500


@lm_admin_bp.route('/<string:method_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_learning_method(method_id: str):
    """
    Deactivate learning method (admin only)

    Path Parameters:
        method_id: Learning method ID

    Response:
        200: Method deactivated
        404: Method not found
    """
    try:
        method = LearningMethodRepository.find_by_id(method_id)

        if not method:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        updated_method = LearningMethodRepository.deactivate(method_id)

        return jsonify({
            'success': True,
            'message': 'Learning method deactivated successfully',
            'method': updated_method
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to deactivate learning method',
            'details': str(e)
        }), 500
