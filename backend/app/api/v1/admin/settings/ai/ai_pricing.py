"""
AI Pricing Management (Consolidated)

Consolidated from:
- pricing_calculator.py - Pricing calculations
- pricing_plans.py - Pricing plan management

Endpoints for AI pricing calculations and plan management:
- POST /api/v1/admin/settings/ai/pricing/calculate - Calculate cost/price for operation
- POST /api/v1/admin/settings/ai/pricing/estimate - Estimate cost for planned operation
- GET /api/v1/admin/settings/ai/pricing/plans - List all pricing plans
- GET /api/v1/admin/settings/ai/pricing/plans/<id> - Get plan details
- PUT /api/v1/admin/settings/ai/pricing/plans/<id> - Update plan
- POST /api/v1/admin/settings/ai/pricing/plans/<id>/calculate - Calculate plan costs

Uses:
- AIUsageService for cost/price calculations
- Repository Pattern for persistence
- DDD approach for domain logic
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
from decimal import Decimal
import logging

from app.api.middleware.auth import permission_required
from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
from app.infrastructure.persistence.repositories.subscription import PlanRepository
from app.application.services.audit_service import AuditService
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

# DDD Core Domain
from .core.services import AIUsageService
from .core.value_objects import Margin

logger = logging.getLogger(__name__)

# ============================================================================
# PRICING CALCULATOR BLUEPRINT
# ============================================================================

pricing_calculator_bp = Blueprint(
    'ai_pricing_calculator',
    __name__,
    url_prefix='/admin-panel/settings/ai/pricing'
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
# PRICING PLANS BLUEPRINT
# ============================================================================

pricing_plans_bp = Blueprint(
    'ai_pricing_plans',
    __name__,
    url_prefix='/admin-panel/settings/ai/pricing/plans'
)


@pricing_plans_bp.route('', methods=['GET'])
@permission_required('admin.system:read')
def list_pricing_plans() -> Tuple[Dict[str, Any], int]:
    """
    List all pricing plans.

    Query Parameters:
        include_inactive (bool): Include inactive plans (default: false)
        tier (str): Filter by tier (free, basic, premium, school, company)

    Returns:
        JSON response with plans list
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        tier = request.args.get('tier')

        # Get plans
        plans = PlanRepository.get_all(
            include_inactive=include_inactive,
            tier=tier
        )

        return jsonify({
            'success': True,
            'data': {
                'plans': plans,
                'count': len(plans)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing pricing plans: {e}")
        return error_response(ErrorCode.LIST_PLANS_ERROR, 500, details={'message': str(e)})


@pricing_plans_bp.route('/<plan_id>', methods=['GET'])
@permission_required('admin.system:read')
def get_pricing_plan(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get pricing plan details.

    Args:
        plan_id: The plan's UUID

    Returns:
        JSON response with plan details including:
        - Plan metadata
        - Token allowances
        - Pricing
        - Features
    """
    try:
        plan = PlanRepository.get_by_id(plan_id)

        if not plan:
            return error_response(ErrorCode.PLAN_NOT_FOUND, 404, details={'plan_id': plan_id})

        return jsonify({
            'success': True,
            'data': plan
        }), 200

    except Exception as e:
        logger.error(f"Error getting pricing plan {plan_id}: {e}")
        return error_response(ErrorCode.GET_PLAN_ERROR, 500, details={'message': str(e)})


@pricing_plans_bp.route('/<plan_id>', methods=['PUT'])
@permission_required('admin.system:write')
def update_pricing_plan(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Update pricing plan.

    Args:
        plan_id: The plan's UUID

    Request Body:
        name (str, optional): Plan name
        description (str, optional): Plan description
        monthly_price (float, optional): Monthly price
        yearly_price (float, optional): Yearly price
        token_allowance (int, optional): Monthly token allowance
        features (dict, optional): Plan features
        active (bool, optional): Active status

    Returns:
        JSON response with updated plan

    Business Rules:
    - Price changes don't affect existing subscriptions
    - Can't make plan inactive if it has active subscriptions
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(ErrorCode.BAD_REQUEST, 400, details={'message': 'Request body required'})

        # Get plan
        plan = PlanRepository.get_by_id(plan_id)
        if not plan:
            return error_response(ErrorCode.PLAN_NOT_FOUND, 404, details={'plan_id': plan_id})

        # Business Rule: Check if plan can be deactivated
        if data.get('active') is False and plan.get('active'):
            # Check for active subscriptions
            active_subscriptions = PlanRepository.get_active_subscription_count(plan_id)
            if active_subscriptions > 0:
                return error_response(ErrorCode.PLAN_HAS_ACTIVE_SUBSCRIPTIONS, 400, details={'active_subscriptions': active_subscriptions})

        # Update plan
        updated_plan = PlanRepository.update(plan_id, data)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='update_pricing_plan',
            resource_type='pricing_plan',
            resource_id=plan_id,
            details={'changes': data}
        )

        return jsonify({
            'success': True,
            'data': updated_plan,
            'message': f'Plan {updated_plan.get("name")} updated'
        }), 200

    except Exception as e:
        logger.error(f"Error updating pricing plan {plan_id}: {e}")
        return error_response(ErrorCode.UPDATE_PLAN_ERROR, 500, details={'message': str(e)})


@pricing_plans_bp.route('/<plan_id>/calculate', methods=['POST'])
@permission_required('admin.system:read')
def calculate_plan_costs(plan_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Calculate estimated costs for a pricing plan.

    Calculates the expected cost based on average token usage patterns.

    Args:
        plan_id: The plan's UUID

    Request Body:
        usage_percentage (float, optional): Expected usage percentage of allowance (default: 80)
        operation_mix (dict, optional): Mix of operation types

    Returns:
        JSON response with cost breakdown
    """
    try:
        data = request.get_json() or {}

        # Get plan
        plan = PlanRepository.get_by_id(plan_id)
        if not plan:
            return error_response(ErrorCode.PLAN_NOT_FOUND, 404, details={'plan_id': plan_id})

        # Get parameters
        usage_percentage = min(float(data.get('usage_percentage', 80)), 100)
        token_allowance = plan.get('token_allowance', 10000)

        # Calculate expected token usage
        expected_tokens = int(token_allowance * (usage_percentage / 100))

        # Default operation mix (can be customized)
        operation_mix = data.get('operation_mix', {
            'module_gen': 40,      # 40% of usage
            'method_gen': 30,      # 30%
            'exam_gen': 20,        # 20%
            'summary': 10          # 10%
        })

        # Calculate costs per operation type
        # This is simplified - in production would use actual model costs
        estimated_cost = Decimal('0')
        operation_breakdown = {}

        # Simplified cost calculation
        # In production, this would query actual models and use AIUsageService
        avg_cost_per_1k_tokens = Decimal('0.01')  # $0.01 per 1k tokens average

        for operation_type, percentage in operation_mix.items():
            tokens_for_operation = int(expected_tokens * (percentage / 100))
            cost_for_operation = (Decimal(tokens_for_operation) / 1000) * avg_cost_per_1k_tokens

            operation_breakdown[operation_type] = {
                'percentage': percentage,
                'tokens': tokens_for_operation,
                'estimated_cost': float(cost_for_operation)
            }

            estimated_cost += cost_for_operation

        # Calculate margin
        monthly_price = Decimal(str(plan.get('monthly_price', 0)))
        margin = monthly_price - estimated_cost
        margin_percentage = (margin / monthly_price * 100) if monthly_price > 0 else 0

        return jsonify({
            'success': True,
            'data': {
                'plan': {
                    'plan_id': plan_id,
                    'name': plan.get('name'),
                    'tier': plan.get('tier')
                },
                'assumptions': {
                    'usage_percentage': usage_percentage,
                    'token_allowance': token_allowance,
                    'expected_tokens': expected_tokens,
                    'operation_mix': operation_mix
                },
                'calculations': {
                    'operation_breakdown': operation_breakdown,
                    'total_estimated_cost': float(estimated_cost),
                    'monthly_price': float(monthly_price),
                    'margin': float(margin),
                    'margin_percentage': float(margin_percentage)
                },
                'recommendation': (
                    f'Healthy margin ({margin_percentage:.1f}%)'
                    if margin_percentage > 30
                    else f'Low margin ({margin_percentage:.1f}%) - consider price adjustment'
                )
            }
        }), 200

    except Exception as e:
        logger.error(f"Error calculating plan costs for {plan_id}: {e}")
        return error_response(ErrorCode.CALCULATE_PLAN_COSTS_ERROR, 500, details={'message': str(e)})


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
