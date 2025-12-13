"""
LernsystemX Learning Methods API

AI-powered learning method endpoints:
- GET    /api/v1/learning-methods - List all methods (public)
- GET    /api/v1/learning-methods/:id - Get method details (public)
- POST   /api/v1/learning-methods/:id/execute - Execute AI method (authenticated, premium+)
- GET    /api/v1/learning-methods/:id/examples - Get usage examples (public)
- GET    /api/v1/learning-methods/:id/feedback - Get method feedback (public)
- POST   /api/v1/learning-methods/:id/feedback - Submit feedback (authenticated)
- GET    /api/v1/learning-methods/stats - Get statistics (admin only)
- POST   /api/v1/learning-methods - Create method (admin only)
- PUT    /api/v1/learning-methods/:id - Update method (admin only)
- DELETE /api/v1/learning-methods/:id - Delete method (admin only)

ISO 27001:2013 compliant - AI execution security and token management
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import request, jsonify, current_app
from pydantic import ValidationError

from app.api import api_v1
from app.models.learning_method import (
    LearningMethodCreate,
    LearningMethodUpdate,
    LearningMethodResponse,
    LearningMethodExecutionRequest,
    LearningMethodExecutionResponse,
    AIFeedbackCreate,
    AIFeedbackResponse,
    get_required_tier,
    check_tier_access
)
from app.repositories.learning_method_repository import LearningMethodRepository
from app.repositories.user_repository import UserRepository
from app.middleware.auth import token_required, admin_required, get_current_user
from app.services.ai_adapter import AIProviderError
from app.services.billing_service import BillingService


# ============================================================================
# PUBLIC LEARNING METHOD ENDPOINTS
# ============================================================================

@api_v1.route('/learning-methods', methods=['GET'])
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
        return jsonify({
            'success': False,
            'error': 'Failed to list learning methods',
            'details': str(e)
        }), 500


@api_v1.route('/learning-methods/<string:method_id>', methods=['GET'])
def get_learning_method(method_id):
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
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

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
        return jsonify({
            'success': False,
            'error': 'Failed to get learning method',
            'details': str(e)
        }), 500


@api_v1.route('/learning-methods/<string:method_id>/examples', methods=['GET'])
def get_method_examples(method_id):
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
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

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
        return jsonify({
            'success': False,
            'error': 'Failed to get examples',
            'details': str(e)
        }), 500


@api_v1.route('/learning-methods/<string:method_id>/feedback', methods=['GET'])
def get_method_feedback(method_id):
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
        return jsonify({
            'success': False,
            'error': 'Failed to get feedback',
            'details': str(e)
        }), 500


# ============================================================================
# AUTHENTICATED LEARNING METHOD ENDPOINTS
# ============================================================================

@api_v1.route('/learning-methods/<string:method_id>/execute', methods=['POST'])
@token_required
def execute_learning_method(method_id):
    """
    Execute AI-powered learning method (Premium+ only)

    Path Parameters:
        method_id: Learning method ID

    Request Body:
        {
            "user_input": "Erkläre mir Polymorphismus",
            "context": "OOP Grundlagen",
            "language": "de",
            "difficulty": "intermediate",
            "course_id": "550e8400-e29b-41d4-a716-446655440000",
            "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
            "lesson_id": "550e8400-e29b-41d4-a716-446655440002",
            "conversation_history": [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }

    Response:
        200: AI execution response
        400: Validation error
        401: Unauthorized
        403: Insufficient tier (upgrade required)
        429: Token quota exceeded
        500: AI execution failed
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Get learning method
        method = LearningMethodRepository.find_by_id(method_id)

        if not method:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        if not method['active']:
            return jsonify({
                'success': False,
                'error': 'This learning method is currently not active'
            }), 403

        # Validate request with Pydantic
        execution_request = LearningMethodExecutionRequest(
            method_id=method_id,
            **data
        )

        # Estimate token cost
        complexity = execution_request.difficulty if execution_request.difficulty else 'medium'
        estimated_tokens = BillingService.estimate_ai_cost(method['name'], complexity)

        # BILLING CHECK: Ensure user can use AI
        access_check = BillingService.ensure_user_can_use_ai(
            user_id=user['user_id'],
            method_id=method_id,
            estimated_tokens=estimated_tokens
        )
        
        # Debug logging
        current_app.logger.info(f'[DEBUG] User {user["user_id"]} access_check: {access_check}')

        if not access_check['allowed']:
            # Determine appropriate HTTP status code
            if 'AI access not included' in access_check.get('reason', ''):
                # Plan doesn't include AI access
                status_code = 403
            elif 'Insufficient tokens' in access_check.get('reason', ''):
                # Not enough tokens
                status_code = 402  # Payment Required
            else:
                # Other reasons (subscription status, etc.)
                status_code = 403

            return jsonify({
                'success': False,
                'error': 'Access denied',
                'reason': access_check.get('reason'),
                'required_tier': access_check.get('required_tier'),
                'user_tier': access_check.get('user_tier'),
                'estimated_cost': estimated_tokens,
                'shortage': access_check.get('shortage'),
                'upgrade_url': '/api/v1/subscriptions/plans'
            }), status_code

        # Execute AI method
        try:
            execution_result = LearningMethodRepository.execute_ai_method(
                user_id=user['user_id'],
                method_id=method_id,
                user_input=execution_request.user_input,
                context=execution_request.context,
                language=execution_request.language,
                difficulty=execution_request.difficulty,
                conversation_history=execution_request.conversation_history,
                course_id=execution_request.course_id,
                chapter_id=execution_request.chapter_id,
                lesson_id=execution_request.lesson_id
            )

            # BILLING: Charge for AI usage
            # Extract actual tokens used from execution result
            # Note: execute_ai_method returns 'total_tokens', not 'tokens_used'
            tokens_used = execution_result.get('total_tokens', execution_result.get('tokens_used', estimated_tokens))
            provider = execution_result.get('provider', 'openai')

            billing_result = BillingService.charge_ai_usage(
                user_id=user['user_id'],
                organisation_id=user.get('organization_id'),
                method_id=method_id,
                tokens_used=tokens_used,
                provider=provider,
                meta={
                    'execution_id': execution_result.get('execution_id'),
                    'model': execution_result.get('model'),
                    'ai_module': method['name'],
                    'input_tokens': execution_result.get('input_tokens', 0),
                    'output_tokens': execution_result.get('output_tokens', 0),
                    'cost_eur': execution_result.get('cost_eur', 0)
                }
            )

            # Add billing info to response
            execution_result['billing'] = {
                'tokens_charged': tokens_used,
                'new_balance': billing_result['new_balance'],
                'transaction_id': str(billing_result['transaction']['transaction_id'])
            }

            # Convert UUIDs to strings for Pydantic
            execution_result['execution_id'] = str(execution_result['execution_id'])
            execution_result['method_id'] = str(execution_result.get('method_id', method_id))

            # Convert to response model
            execution_response = LearningMethodExecutionResponse(**execution_result)

            return jsonify({
                'success': True,
                'execution': execution_response.model_dump()
            }), 200

        except AIProviderError as e:
            return jsonify({
                'success': False,
                'error': 'AI execution failed',
                'message': str(e)
            }), 500

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except Exception as e:
        import traceback
        current_app.logger.error(f'[ERROR] Learning method execution failed: {str(e)}')
        current_app.logger.error(f'[TRACEBACK] {traceback.format_exc()}')
        return jsonify({
            'success': False,
            'error': 'Execution failed',
            'details': str(e)
        }), 500


@api_v1.route('/learning-methods/<string:method_id>/feedback', methods=['POST'])
@token_required
def submit_method_feedback(method_id):
    """
    Submit feedback for AI execution

    Path Parameters:
        method_id: Learning method ID

    Request Body:
        {
            "execution_id": "550e8400-e29b-41d4-a716-446655440000",
            "rating": 4,
            "feedback_text": "Gute Erklärung, aber könnte detaillierter sein",
            "is_helpful": true,
            "course_id": "550e8400-e29b-41d4-a716-446655440001",
            "chapter_id": "550e8400-e29b-41d4-a716-446655440002"
        }

    Response:
        201: Feedback created
        400: Validation error
        401: Unauthorized
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate with Pydantic
        feedback_data = AIFeedbackCreate(**data)

        # Create feedback
        feedback = LearningMethodRepository.create_feedback(
            user_id=user['user_id'],
            execution_id=feedback_data.execution_id,
            rating=feedback_data.rating,
            feedback_text=feedback_data.feedback_text,
            is_helpful=feedback_data.is_helpful,
            ai_generated=feedback_data.ai_generated,
            course_id=feedback_data.course_id,
            chapter_id=feedback_data.chapter_id,
            lesson_id=feedback_data.lesson_id
        )

        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback': feedback
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to submit feedback',
            'details': str(e)
        }), 500


@api_v1.route('/lessons/<string:lesson_id>/executions', methods=['GET'])
@token_required
def get_lesson_executions(lesson_id):
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


@api_v1.route('/executions/<string:execution_id>', methods=['DELETE'])
@token_required
def delete_execution(execution_id):
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


@api_v1.route('/learning-methods/my-usage', methods=['GET'])
@token_required
def get_my_token_usage():
    """
    Get current user's AI token usage statistics

    Query Parameters:
        period_days: Period in days (default: 30)

    Response:
        200: Token usage statistics
        {
            "success": true,
            "usage": {
                "total_tokens": 125000,
                "total_cost_eur": 12.50,
                "total_requests": 267,
                "by_method": {...},
                "by_provider": {...},
                "by_model": {...}
            }
        }
    """
    try:
        user = get_current_user()
        period_days = min(int(request.args.get('period_days', 30)), 365)

        usage_stats = LearningMethodRepository.get_user_token_usage(
            user_id=user['user_id'],
            period_days=period_days
        )

        return jsonify({
            'success': True,
            'usage': usage_stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get token usage',
            'details': str(e)
        }), 500


# ============================================================================
# ADMIN LEARNING METHOD ENDPOINTS
# ============================================================================

@api_v1.route('/learning-methods', methods=['POST'])
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


@api_v1.route('/learning-methods/<string:method_id>', methods=['PUT'])
@admin_required
def update_learning_method(method_id):
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


@api_v1.route('/learning-methods/<string:method_id>', methods=['DELETE'])
@admin_required
def delete_learning_method(method_id):
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


@api_v1.route('/learning-methods/stats', methods=['GET'])
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


@api_v1.route('/learning-methods/<string:method_id>/activate', methods=['POST'])
@admin_required
def activate_learning_method(method_id):
    """Activate learning method (admin only)"""
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


@api_v1.route('/learning-methods/<string:method_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_learning_method(method_id):
    """Deactivate learning method (admin only)"""
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
