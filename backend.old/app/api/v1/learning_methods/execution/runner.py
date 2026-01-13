"""
LernsystemX Learning Methods API - Execution Runner

AI execution, feedback submission, and usage tracking endpoints.

Endpoints:
- POST /api/v1/learning-methods/:id/execute  - Execute AI method (premium+)
- POST /api/v1/learning-methods/:id/feedback - Submit feedback
- GET  /api/v1/learning-methods/my-usage     - Get user's token usage

ISO 27001:2013 compliant - AI execution security and token management
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from typing import Dict, Any, Tuple
import traceback

from app.models.learning_method import (
    LearningMethodExecutionRequest,
    LearningMethodExecutionResponse,
    AIFeedbackCreate
)
from app.repositories.learning_method import LearningMethodRepository
from app.middleware.auth import token_required, get_current_user
from app.services.billing_service import BillingService
from app.services.ai_adapter import AIProviderError

# Blueprint for execution endpoints
lm_execution_bp = Blueprint(
    'learning_methods_execution',
    __name__,
    url_prefix='/api/v1/learning-methods'
)


@lm_execution_bp.route('/<string:method_id>/execute', methods=['POST'])
@token_required
def execute_learning_method(method_id: str):
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
            tokens_used = execution_result.get(
                'total_tokens',
                execution_result.get('tokens_used', estimated_tokens)
            )
            provider = execution_result.get('provider', 'openai')

            billing_result = BillingService.charge_ai_usage(
                user_id=user['user_id'],
                organization_id=user.get('organization_id'),
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
        current_app.logger.error(f'[ERROR] Learning method execution failed: {str(e)}')
        current_app.logger.error(f'[TRACEBACK] {traceback.format_exc()}')
        return jsonify({
            'success': False,
            'error': 'Execution failed',
            'details': str(e)
        }), 500


@lm_execution_bp.route('/<string:method_id>/feedback', methods=['POST'])
@token_required
def submit_method_feedback(method_id: str):
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


@lm_execution_bp.route('/my-usage', methods=['GET'])
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
