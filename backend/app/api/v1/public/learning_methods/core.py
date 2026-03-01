"""
LernsystemX Learning Methods API - Consolidated

Learning method type management and public catalog.

Public Endpoints (No Auth):
- GET /learning-methods - List all methods
- GET /learning-methods/:id - Get method details
- GET /learning-methods/:id/examples - Get usage examples
- GET /learning-methods/:id/feedback - Get method feedback

Admin Endpoints (Auth Required):
- POST /learning-methods - Create method
- PUT /learning-methods/:id - Update method
- DELETE /learning-methods/:id - Delete method
- GET /learning-methods/stats - Get statistics
- POST /learning-methods/:id/activate - Activate method
- POST /learning-methods/:id/deactivate - Deactivate method

Note: Learning method instances (chapter-specific) are managed separately.

All routes: /api/v1/learning-methods/*
ISO 27001:2013 compliant - AI execution security and token management
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from typing import Dict, Any

from app.domain.models.content.learning_method import (
    LearningMethodResponse,
    LearningMethodCreate,
    LearningMethodUpdate
)
from app.infrastructure.persistence.repositories.learning_method import LearningMethodRepository
from app.infrastructure.persistence.repositories.learning_method.execution.instances import LearningMethodInstanceRepository
from app.api.middleware.auth import permission_required, token_required, get_current_user
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

# Blueprint
learning_methods_bp = Blueprint(
    'learning_methods',
    __name__,
    url_prefix='/learning-methods'
)

__all__ = ['learning_methods_bp']


# =============================================================================
# AUTHENTICATED ENDPOINTS - TASK EXECUTION
# =============================================================================

import logging
logger = logging.getLogger(__name__)


@learning_methods_bp.route('/<string:method_id>/execute', methods=['POST'])
@token_required
def execute_learning_method(method_id: str):
    """
    Execute/open a learning method instance for practice.

    Returns the task data (content, instructions, solution) so the
    student can work on it. Also logs an execution record for tracking.

    Path Parameters:
        method_id: Learning method instance ID (UUID)

    Request Body (optional):
        {
            "lesson_id": "uuid",
            "user_input": "optional user answer"
        }

    Response:
        200: Task data for execution
        404: Method not found
    """
    try:
        user = get_current_user()
        data = request.get_json() or {}

        # Fetch the method instance
        instance = LearningMethodInstanceRepository.find_by_id(method_id)
        if not instance:
            return jsonify({'success': False, 'error': 'Method not found'}), 404

        # Transform raw_text into structured data if needed
        raw_data = instance.get('data', {})
        method_type = instance.get('method_type')
        if isinstance(raw_data, dict) and 'raw_text' in raw_data and method_type is not None:
            from app.application.services.ai.plan.plan_execution import _transform_data_for_method
            structured_data = _transform_data_for_method(
                method_type, raw_data, instance.get('title', '')
            )
        else:
            structured_data = raw_data

        # Build execution response from instance data
        execution = {
            'execution_id': method_id,
            'method_id': method_id,
            'method_type': method_type,
            'title': instance.get('title'),
            'instructions': instance.get('instructions'),
            'data': structured_data,
            'solution': instance.get('solution'),
            'difficulty': instance.get('difficulty'),
            'ui_schema': instance.get('ui_schema'),
            'output_text': instance.get('instructions') or instance.get('title', ''),
            'result': structured_data,
        }

        return jsonify({
            'success': True,
            'execution': execution,
        }), 200

    except Exception as e:
        logger.error(f"Error executing learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to execute method',
        }), 500


# =============================================================================
# PUBLIC ENDPOINTS - NO AUTHENTICATION
# =============================================================================

@learning_methods_bp.route('', methods=['GET'])
def list_learning_methods():
    """
    List all learning methods

    Query Parameters:
        active_only: Only return active methods (default: true)
        tier: Filter by tier (basic, premium, pro)

    Response:
        200: List of learning methods
        {
            "success": true,
            "methods": [
                {
                    "method_id": 1,
                    "name": "Flashcards",
                    "description": "Classic flashcards with Q&A",
                    "tier": "basic",
                    "config": {...},
                    "active": true,
                    "usage_count": 1234
                }
            ],
            "total": 21
        }
    """
    try:
        # Get query parameters
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        tier_filter = request.args.get('tier')

        # Get all methods
        methods = LearningMethodRepository.get_all(active_only)

        # Filter by tier if specified
        if tier_filter:
            methods = [m for m in methods if m['tier'] == tier_filter]

        # Convert to response models
        method_responses = [LearningMethodResponse(**method) for method in methods]

        return jsonify({
            'success': True,
            'methods': [m.model_dump() for m in method_responses],
            'total': len(methods)
        }), 200

    except Exception as e:
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@learning_methods_bp.route('/<string:method_id>', methods=['GET'])
def get_learning_method(method_id: str):
    """
    Get learning method details

    Path Parameters:
        method_id: Learning method ID

    Response:
        200: Method details
        404: Method not found
    """
    try:
        method = LearningMethodRepository.find_by_id(method_id)

        if not method:
            return error_response(ErrorCode.LM_NOT_FOUND, 404)

        # Get feedback stats
        feedback_stats = LearningMethodRepository.get_feedback_stats(method_id)

        # Convert to response model
        method_response = LearningMethodResponse(**method)
        method_dict = method_response.model_dump()
        method_dict['feedback_stats'] = feedback_stats

        return jsonify({
            'success': True,
            'method': method_dict
        }), 200

    except Exception as e:
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@learning_methods_bp.route('/<string:method_id>/examples', methods=['GET'])
def get_method_examples(method_id: str):
    """
    Get usage examples for learning method

    Path Parameters:
        method_id: Learning method ID

    Response:
        200: Usage examples based on method type
    """
    try:
        method = LearningMethodRepository.find_by_id(method_id)

        if not method:
            return error_response(ErrorCode.LM_NOT_FOUND, 404)

        # Example prompts by method type
        examples = {
            'KI-Tutor': [
                {
                    'prompt': 'Erkläre mir Polymorphismus in Python',
                    'context': 'Wir sind bei Lektion 3: OOP Konzepte',
                    'difficulty': 'intermediate'
                },
                {
                    'prompt': 'Was sind Decorators und wann verwende ich sie?',
                    'context': 'Python Advanced Concepts',
                    'difficulty': 'advanced'
                }
            ],
            'KI-Glossar': [
                {
                    'prompt': 'Rekursion',
                    'context': 'Informatik Grundlagen',
                    'difficulty': 'beginner'
                },
                {
                    'prompt': 'Algorithmus',
                    'context': None,
                    'difficulty': 'beginner'
                }
            ],
            'Braindump': [
                {
                    'prompt': 'Fasse die wichtigsten Konzepte von SQL zusammen',
                    'context': 'Nach Abschluss von Modul 2: Datenbanken',
                    'difficulty': 'intermediate'
                }
            ],
            'Deep Praxis': [
                {
                    'prompt': 'Erstelle eine REST API für eine Bibliotheksverwaltung',
                    'context': 'Projekt: Library Management System',
                    'difficulty': 'advanced'
                }
            ]
        }

        method_examples = examples.get(method['name'], [
            {
                'prompt': f'Beispiel für {method["name"]}',
                'context': 'Allgemeiner Kontext',
                'difficulty': 'intermediate'
            }
        ])

        return jsonify({
            'success': True,
            'method_id': method_id,
            'method_name': method['name'],
            'examples': method_examples
        }), 200

    except Exception as e:
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@learning_methods_bp.route('/<string:method_id>/feedback', methods=['GET'])
def get_method_feedback(method_id: str):
    """
    Get feedback for learning method

    Path Parameters:
        method_id: Learning method ID

    Query Parameters:
        limit: Maximum results (default: 50)

    Response:
        200: List of feedback
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 200)

        feedback_list = LearningMethodRepository.get_method_feedback(method_id, limit)
        feedback_stats = LearningMethodRepository.get_feedback_stats(method_id)

        return jsonify({
            'success': True,
            'feedback': feedback_list,
            'stats': feedback_stats,
            'total': len(feedback_list)
        }), 200

    except Exception as e:
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


# =============================================================================
# ADMIN ENDPOINTS - LEARNING METHOD TYPE MANAGEMENT
# =============================================================================

@learning_methods_bp.route('', methods=['POST'])
@permission_required('admin.courses:write')
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
            return error_response(ErrorCode.LM_ALREADY_EXISTS, 409, details={'message': f'A method named "{method_data.name}" already exists'})

        # Create method
        method = LearningMethodRepository.create(method_data.model_dump())

        return jsonify({
            'success': True,
            'message': 'Learning method created successfully',
            'method': method
        }), 201

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})

    except Exception as e:
        return error_response(ErrorCode.LM_CREATE_FAILED, 500, details={'details': str(e)})


@learning_methods_bp.route('/<string:method_id>', methods=['PUT'])
@permission_required('admin.courses:write')
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
            return error_response(ErrorCode.LM_NOT_FOUND, 404)

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
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})

    except Exception as e:
        return error_response(ErrorCode.LM_UPDATE_FAILED, 500, details={'details': str(e)})


@learning_methods_bp.route('/<string:method_id>', methods=['DELETE'])
@permission_required('admin.courses:write')
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
            return error_response(ErrorCode.LM_NOT_FOUND, 404)

        # Delete method
        LearningMethodRepository.delete(method_id)

        return jsonify({
            'success': True,
            'message': 'Learning method deleted successfully'
        }), 200

    except Exception as e:
        return error_response(ErrorCode.LM_DELETE_FAILED, 500, details={'details': str(e)})


@learning_methods_bp.route('/stats', methods=['GET'])
@permission_required('admin.courses:write')
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
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@learning_methods_bp.route('/<string:method_id>/activate', methods=['POST'])
@permission_required('admin.courses:write')
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
            return error_response(ErrorCode.LM_NOT_FOUND, 404)

        updated_method = LearningMethodRepository.activate(method_id)

        return jsonify({
            'success': True,
            'message': 'Learning method activated successfully',
            'method': updated_method
        }), 200

    except Exception as e:
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@learning_methods_bp.route('/<string:method_id>/deactivate', methods=['POST'])
@permission_required('admin.courses:write')
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
            return error_response(ErrorCode.LM_NOT_FOUND, 404)

        updated_method = LearningMethodRepository.deactivate(method_id)

        return jsonify({
            'success': True,
            'message': 'Learning method deactivated successfully',
            'method': updated_method
        }), 200

    except Exception as e:
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})
