"""
LernsystemX Learning Methods API - Execution Validator

Endpoints for managing and validating saved executions.

Endpoints:
- GET  /api/v1/lessons/:id/executions        - Get lesson executions
- DELETE /api/v1/executions/:id              - Delete execution

ISO 27001:2013 compliant - Data access control
"""

from flask import Blueprint

from .._helpers import (
    request,
    jsonify,
    LearningMethodRepository,
    token_required,
    get_current_user,
)

# Additional blueprint for executions routes (different prefix)
lm_executions_bp = Blueprint(
    'learning_methods_executions',
    __name__
)


@lm_executions_bp.route('/lessons/<string:lesson_id>/executions', methods=['GET'])
@token_required
def get_lesson_executions(lesson_id: str):
    """
    Get saved task executions for a lesson

    Path Parameters:
        lesson_id: Lesson UUID

    Query Parameters:
        method_id: Filter by method ID (optional)
        limit: Maximum results (default: 50)

    Response:
        200: List of task executions
        {
            "success": true,
            "executions": [...],
            "total": 10
        }
    """
    try:
        user = get_current_user()
        method_id = request.args.get('method_id')
        limit = min(int(request.args.get('limit', 50)), 200)

        executions = LearningMethodRepository.get_lesson_executions(
            user_id=user['user_id'],
            lesson_id=lesson_id,
            method_id=method_id,
            limit=limit
        )

        return jsonify({
            'success': True,
            'executions': executions,
            'total': len(executions)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get executions',
            'details': str(e)
        }), 500


@lm_executions_bp.route('/executions/<string:execution_id>', methods=['DELETE'])
@token_required
def delete_execution(execution_id: str):
    """
    Delete a task execution

    Path Parameters:
        execution_id: Execution UUID

    Response:
        200: Execution deleted successfully
        404: Execution not found or not owned by user
    """
    try:
        user = get_current_user()

        success = LearningMethodRepository.delete_execution(
            execution_id=execution_id,
            user_id=user['user_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Execution not found or not owned by you'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Execution deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete execution',
            'details': str(e)
        }), 500
