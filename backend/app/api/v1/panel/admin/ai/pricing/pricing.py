"""
AI Pricing Calculator

Endpoints for AI pricing calculations:
- POST /api/v1/admin/settings/ai/pricing/calculate - Calculate cost/price for operation
- POST /api/v1/admin/settings/ai/pricing/estimate - Estimate cost for planned operation

Uses:
- AIUsageService for cost/price calculations
- Repository Pattern for persistence
- DDD approach for domain logic

See also: pricing_part2.py for pricing plan management endpoints.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Tuple
import logging

from app.api.middleware.auth import permission_required
from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

# DDD Core Domain
from ..core.services import AIUsageService

logger = logging.getLogger(__name__)

# ============================================================================
# PRICING CALCULATOR BLUEPRINT
# ============================================================================

pricing_calculator_bp = Blueprint(
    'ai_pricing_calculator',
    __name__,
    url_prefix='/panel/settings/ai/pricing'
)


@pricing_calculator_bp.route('/calculate', methods=['POST'])
@permission_required('admin.system:read')
def calculate_pricing() -> Tuple[Dict[str, Any], int]:
    """
    Calculate cost and price for an AI operation.

    Request Body:
        model_id (int): AI model ID
        input_tokens (int): Number of input tokens
        output_tokens (int): Number of output tokens

    Returns:
        JSON response with cost/price breakdown

    DDD: Uses AIUsageService for calculations with business rules
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(ErrorCode.BAD_REQUEST, 400, details={'message': 'Request body required'})

        # Validate required fields
        required_fields = ['model_id', 'input_tokens', 'output_tokens']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return error_response(ErrorCode.MISSING_FIELDS, 400, details={'missing_fields': missing_fields})

        # Get model
        model = AIModelsRepository.get_by_id(data['model_id'])
        if not model:
            return error_response(ErrorCode.AI_MODEL_NOT_FOUND, 404, details={'model_id': data['model_id']})

        # Validate token counts
        input_tokens = int(data['input_tokens'])
        output_tokens = int(data['output_tokens'])

        if input_tokens < 0 or output_tokens < 0:
            return error_response(ErrorCode.INVALID_TOKEN_COUNT, 400, details={'message': 'Token counts must be non-negative'})

        # DDD: Use AIUsageService for calculation
        result = AIUsageService.calculate_operation_cost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

        return jsonify({
            'success': True,
            'data': {
                'model': {
                    'model_id': model.get('model_id'),
                    'model_name': model.get('model_name'),
                    'category': model.get('category')
                },
                'tokens': {
                    'input': result['input_tokens'],
                    'output': result['output_tokens'],
                    'total': result['total_tokens']
                },
                'pricing': {
                    'input_cost_per_1k': float(model.get('input_cost_per_1k', 0)),
                    'output_cost_per_1k': float(model.get('output_cost_per_1k', 0)),
                    'margin_percent': float(model.get('margin_percent', 0)),
                    'input_price_per_1k': float(model.get('input_price_per_1k', 0)),
                    'output_price_per_1k': float(model.get('output_price_per_1k', 0))
                },
                'totals': {
                    'total_cost': float(result['total_cost']),
                    'total_price': float(result['total_price']),
                    'margin': float(result['margin'])
                }
            }
        }), 200

    except ValueError as ve:
        logger.error(f"Validation error in calculate_pricing: {ve}")
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'message': str(ve)})
    except Exception as e:
        logger.error(f"Error calculating pricing: {e}")
        return error_response(ErrorCode.CALCULATE_PRICING_ERROR, 500, details={'message': str(e)})


@pricing_calculator_bp.route('/estimate', methods=['POST'])
@permission_required('admin.system:read')
def estimate_operation_cost() -> Tuple[Dict[str, Any], int]:
    """
    Estimate cost for a planned AI operation.

    Request Body:
        operation_type (str): Type of operation (module_gen, exam_gen, etc.)
        model_id (int, optional): Specific model to use (uses default if not provided)
        complexity (str, optional): Complexity level (simple, medium, complex)

    Returns:
        JSON response with cost estimation

    Business Rules:
    - Uses historical averages for token estimation
    - Provides min/max/average estimates
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(ErrorCode.BAD_REQUEST, 400, details={'message': 'Request body required'})

        operation_type = data.get('operation_type')
        if not operation_type:
            return error_response(ErrorCode.MISSING_OPERATION_TYPE, 400, details={'message': 'operation_type is required'})

        # Get model (use default if not specified)
        model_id = data.get('model_id')
        if model_id:
            model = AIModelsRepository.get_by_id(model_id)
            if not model:
                return error_response(ErrorCode.AI_MODEL_NOT_FOUND, 404, details={'model_id': model_id})
        else:
            # Use default chat model
            model = AIModelsRepository.get_default_model('chat')
            if not model:
                return error_response(ErrorCode.NO_DEFAULT_MODEL, 400, details={'message': 'No default model configured for chat category'})

        # Get token estimates based on operation type
        complexity = data.get('complexity', 'medium')
        token_estimates = _get_token_estimates(operation_type, complexity)

        # Calculate costs for min/avg/max scenarios
        scenarios = {}
        for scenario, tokens in token_estimates.items():
            result = AIUsageService.calculate_operation_cost(
                model=model,
                input_tokens=tokens['input'],
                output_tokens=tokens['output']
            )
            scenarios[scenario] = {
                'input_tokens': tokens['input'],
                'output_tokens': tokens['output'],
                'total_tokens': result['total_tokens'],
                'total_cost': float(result['total_cost']),
                'total_price': float(result['total_price']),
                'margin': float(result['margin'])
            }

        return jsonify({
            'success': True,
            'data': {
                'operation_type': operation_type,
                'complexity': complexity,
                'model': {
                    'model_id': model.get('model_id'),
                    'model_name': model.get('model_name'),
                    'category': model.get('category')
                },
                'estimates': scenarios,
                'recommendation': (
                    f'For {operation_type} ({complexity} complexity), '
                    f'expect ~{scenarios["average"]["total_tokens"]:,} tokens '
                    f'(cost: ${scenarios["average"]["total_cost"]:.4f}, '
                    f'price: ${scenarios["average"]["total_price"]:.4f})'
                )
            }
        }), 200

    except Exception as e:
        logger.error(f"Error estimating operation cost: {e}")
        return error_response(ErrorCode.ESTIMATE_COST_ERROR, 500, details={'message': str(e)})


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_token_estimates(operation_type: str, complexity: str) -> Dict[str, Dict[str, int]]:
    """
    Get token estimates based on operation type and complexity.

    Args:
        operation_type: Type of AI operation
        complexity: Complexity level (simple, medium, complex)

    Returns:
        Dictionary with min/average/max token estimates
    """
    # Base estimates (can be refined with historical data)
    base_estimates = {
        'module_gen': {
            'simple': {'input': 2000, 'output': 3000},
            'medium': {'input': 4000, 'output': 6000},
            'complex': {'input': 8000, 'output': 12000}
        },
        'exam_gen': {
            'simple': {'input': 1500, 'output': 2000},
            'medium': {'input': 3000, 'output': 4000},
            'complex': {'input': 6000, 'output': 8000}
        },
        'method_gen': {
            'simple': {'input': 1000, 'output': 1500},
            'medium': {'input': 2000, 'output': 3000},
            'complex': {'input': 4000, 'output': 6000}
        },
        'translation': {
            'simple': {'input': 500, 'output': 600},
            'medium': {'input': 2000, 'output': 2400},
            'complex': {'input': 5000, 'output': 6000}
        },
        'summary': {
            'simple': {'input': 1000, 'output': 300},
            'medium': {'input': 3000, 'output': 800},
            'complex': {'input': 8000, 'output': 2000}
        }
    }

    # Get base estimate for operation type (default to module_gen)
    operation_base = base_estimates.get(operation_type, base_estimates['module_gen'])
    complexity_base = operation_base.get(complexity, operation_base['medium'])

    # Generate min/average/max scenarios
    return {
        'minimum': {
            'input': int(complexity_base['input'] * 0.7),
            'output': int(complexity_base['output'] * 0.7)
        },
        'average': complexity_base,
        'maximum': {
            'input': int(complexity_base['input'] * 1.5),
            'output': int(complexity_base['output'] * 1.5)
        }
    }
