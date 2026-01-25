"""
AI Models Usage Statistics (DDD)

Endpoints for AI model usage analytics:
- GET /api/v1/admin/settings/ai/models/<id>/usage - Get usage stats for specific model
- GET /api/v1/admin/settings/ai/models/usage - Get usage stats for all models

Uses:
- AIUsageService for cost/price calculations
- Repository Pattern for usage data
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from app.api.middleware.auth import permission_required
from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

# DDD Core Domain
from .core.services import AIUsageService

logger = logging.getLogger(__name__)

models_usage_bp = Blueprint(
    'ai_models_usage',
    __name__,
    url_prefix='/admin-panel/settings/ai/models'
)


@models_usage_bp.route('/<int:model_id>/usage', methods=['GET'])
@permission_required('admin.system:read')
def get_model_usage(model_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get usage statistics for a specific AI model.

    Query Parameters:
        days (int): Number of days to look back (default: 30, max: 365)

    Args:
        model_id: The model's database ID

    Returns:
        JSON response with usage statistics including:
        - Total requests
        - Total tokens (input + output)
        - Total cost and price
        - Average tokens per request
        - Usage by day

    DDD: Uses AIUsageService for cost calculations
    """
    try:
        # Get model
        model = AIModelsRepository.get_by_id(model_id)
        if not model:
            return error_response(ErrorCode.AI_MODEL_NOT_FOUND, 404,
                details={'model_id': model_id})

        # Get time range
        days = min(int(request.args.get('days', 30)), 365)
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get usage stats from repository
        usage_stats = AIModelsRepository.get_usage_stats(model_id, start_date)

        # Calculate totals using DDD Service
        if usage_stats:
            total_result = AIUsageService.calculate_operation_cost(
                model=model,
                input_tokens=usage_stats.get('total_input_tokens', 0),
                output_tokens=usage_stats.get('total_output_tokens', 0)
            )
        else:
            total_result = {
                'total_cost': 0,
                'total_price': 0,
                'margin': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0
            }

        return jsonify({
            'success': True,
            'data': {
                'model': {
                    'model_id': model.get('model_id'),
                    'model_name': model.get('model_name'),
                    'category': model.get('category')
                },
                'period': {
                    'days': days,
                    'start_date': start_date.isoformat(),
                    'end_date': datetime.utcnow().isoformat()
                },
                'totals': {
                    'requests': usage_stats.get('total_requests', 0),
                    'input_tokens': total_result['input_tokens'],
                    'output_tokens': total_result['output_tokens'],
                    'total_tokens': total_result['total_tokens'],
                    'total_cost': float(total_result['total_cost']),
                    'total_price': float(total_result['total_price']),
                    'margin': float(total_result['margin'])
                },
                'averages': {
                    'tokens_per_request': (
                        total_result['total_tokens'] / usage_stats.get('total_requests', 1)
                        if usage_stats.get('total_requests', 0) > 0
                        else 0
                    ),
                    'cost_per_request': (
                        float(total_result['total_cost']) / usage_stats.get('total_requests', 1)
                        if usage_stats.get('total_requests', 0) > 0
                        else 0
                    )
                },
                'by_day': usage_stats.get('by_day', [])
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting usage for model {model_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500,
            details={'error': str(e)})


@models_usage_bp.route('/usage', methods=['GET'])
@permission_required('admin.system:read')
def get_all_models_usage() -> Tuple[Dict[str, Any], int]:
    """
    Get usage statistics for all AI models.

    Query Parameters:
        days (int): Number of days to look back (default: 30, max: 365)
        category (str): Filter by category (chat, reasoning, etc.)
        sort_by (str): Sort by field (requests, tokens, cost, price) (default: requests)

    Returns:
        JSON response with usage statistics for all models

    DDD: Uses AIUsageService for cost calculations
    """
    try:
        # Get parameters
        days = min(int(request.args.get('days', 30)), 365)
        category = request.args.get('category')
        sort_by = request.args.get('sort_by', 'requests')

        start_date = datetime.utcnow() - timedelta(days=days)

        # Get all models with usage
        models_usage = AIModelsRepository.get_all_usage_stats(
            start_date=start_date,
            category=category
        )

        # Calculate costs and prices using DDD Service
        for model_usage in models_usage:
            model = model_usage['model']
            stats = model_usage['stats']

            if stats.get('total_input_tokens', 0) > 0 or stats.get('total_output_tokens', 0) > 0:
                result = AIUsageService.calculate_operation_cost(
                    model=model,
                    input_tokens=stats.get('total_input_tokens', 0),
                    output_tokens=stats.get('total_output_tokens', 0)
                )
                model_usage['calculated'] = {
                    'total_cost': float(result['total_cost']),
                    'total_price': float(result['total_price']),
                    'margin': float(result['margin'])
                }
            else:
                model_usage['calculated'] = {
                    'total_cost': 0,
                    'total_price': 0,
                    'margin': 0
                }

        # Sort by requested field
        sort_field_map = {
            'requests': lambda x: x['stats'].get('total_requests', 0),
            'tokens': lambda x: x['stats'].get('total_tokens', 0),
            'cost': lambda x: x['calculated']['total_cost'],
            'price': lambda x: x['calculated']['total_price']
        }
        sort_key = sort_field_map.get(sort_by, sort_field_map['requests'])
        models_usage.sort(key=sort_key, reverse=True)

        # Calculate grand totals
        grand_totals = {
            'requests': sum(m['stats'].get('total_requests', 0) for m in models_usage),
            'total_tokens': sum(m['stats'].get('total_tokens', 0) for m in models_usage),
            'total_cost': sum(m['calculated']['total_cost'] for m in models_usage),
            'total_price': sum(m['calculated']['total_price'] for m in models_usage),
            'total_margin': sum(m['calculated']['margin'] for m in models_usage)
        }

        return jsonify({
            'success': True,
            'data': {
                'period': {
                    'days': days,
                    'start_date': start_date.isoformat(),
                    'end_date': datetime.utcnow().isoformat()
                },
                'filters': {
                    'category': category,
                    'sort_by': sort_by
                },
                'grand_totals': grand_totals,
                'models': models_usage,
                'count': len(models_usage)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting all models usage: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500,
            details={'error': str(e)})
