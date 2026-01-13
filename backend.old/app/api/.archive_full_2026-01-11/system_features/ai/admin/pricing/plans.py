"""
AI Pricing Plans (DDD)

Endpoints for pricing plan management:
- GET /api/v1/admin/ai/pricing/plans - List all pricing plans
- GET /api/v1/admin/ai/pricing/plans/<id> - Get plan details
- PUT /api/v1/admin/ai/pricing/plans/<id> - Update plan
- POST /api/v1/admin/ai/pricing/plans/<id>/calculate - Calculate plan costs

Uses:
- Repository Pattern for persistence
- Business rules for plan management
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
from decimal import Decimal
import logging

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.subscription import PlanRepository
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

pricing_plans_bp = Blueprint(
    'ai_pricing_plans',
    __name__,
    url_prefix='/api/v1/admin/ai/pricing/plans'
)


@pricing_plans_bp.route('', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
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
        return jsonify({
            'success': False,
            'error': {
                'code': 'LIST_PLANS_ERROR',
                'message': str(e)
            }
        }), 500


@pricing_plans_bp.route('/<plan_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PLAN_NOT_FOUND',
                    'message': f'Plan {plan_id} not found'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': plan
        }), 200

    except Exception as e:
        logger.error(f"Error getting pricing plan {plan_id}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_PLAN_ERROR',
                'message': str(e)
            }
        }), 500


@pricing_plans_bp.route('/<plan_id>', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Request body required'
                }
            }), 400

        # Get plan
        plan = PlanRepository.get_by_id(plan_id)
        if not plan:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PLAN_NOT_FOUND',
                    'message': f'Plan {plan_id} not found'
                }
            }), 404

        # Business Rule: Check if plan can be deactivated
        if data.get('active') is False and plan.get('active'):
            # Check for active subscriptions
            active_subscriptions = PlanRepository.get_active_subscription_count(plan_id)
            if active_subscriptions > 0:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'PLAN_HAS_ACTIVE_SUBSCRIPTIONS',
                        'message': f'Plan has {active_subscriptions} active subscriptions. Cannot deactivate.'
                    }
                }), 400

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
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_PLAN_ERROR',
                'message': str(e)
            }
        }), 500


@pricing_plans_bp.route('/<plan_id>/calculate', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
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
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PLAN_NOT_FOUND',
                    'message': f'Plan {plan_id} not found'
                }
            }), 404

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
        return jsonify({
            'success': False,
            'error': {
                'code': 'CALCULATE_PLAN_COSTS_ERROR',
                'message': str(e)
            }
        }), 500
