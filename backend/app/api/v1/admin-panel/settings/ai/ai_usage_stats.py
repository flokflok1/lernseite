"""
AI System Usage Statistics (Admin)

Endpoints for system-wide AI usage analytics:
- GET /api/v1/admin/ai/usage-stats - Get overall AI usage statistics

Returns:
- total_requests: Total number of AI requests
- total_tokens: Total tokens used
- total_cost: Total cost in USD
- total_generations: Count of generation-type requests
- by_provider: Breakdown by AI provider
- by_model: Breakdown by AI model
- by_request_type: Breakdown by request type
"""

from flask import request
import logging
from typing import Dict, Any, Tuple

from app.api.v1 import api_v1
from app.api.middleware.auth import token_required
from app.infrastructure.security.permissions import require_permission, Permissions
from app.infrastructure.persistence.repositories.ai.usage import AIUsageRepository
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

logger = logging.getLogger(__name__)


@api_v1.route('/admin/ai/usage-stats', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_usage_stats() -> Tuple[Dict[str, Any], int]:
    """
    Get system-wide AI usage statistics.

    Query Parameters:
        period (str): Time period ('day', 'week', 'month', 'year')
                     default: 'month'

    Returns:
        JSON response with:
        - total_requests: Total number of AI requests
        - total_tokens: Total tokens used
        - total_cost: Total cost in USD
        - total_generations: Count of generation-type requests
        - successful_requests: Count of successful requests
        - failed_requests: Count of failed requests
        - by_provider: List of usage by provider
        - by_model: List of usage by model
        - by_request_type: List of usage by request type

    Status Codes:
        200: Success
        401: Unauthorized
        403: Forbidden (insufficient permissions)
        500: Internal server error
    """
    try:
        period = request.args.get('period', 'month', type=str)

        # Validate period
        valid_periods = ['day', 'week', 'month', 'year']
        if period not in valid_periods:
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400,
                details={'field': 'period', 'valid_values': valid_periods})

        # Get usage statistics from repository
        stats = AIUsageRepository.get_usage_stats(period=period)

        # Count generation-type requests (typically 'module_gen', 'method_gen', 'exam_gen', etc.)
        total_generations = sum(
            item.get('request_count', 0)
            for item in stats.get('by_request_type', [])
            if 'gen' in item.get('request_type', '').lower() or 'generation' in item.get('request_type', '').lower()
        )

        # Build response
        response_data = {
            'success': True,
            'data': {
                'period': stats['period'],
                'start_date': stats['start_date'],
                'end_date': stats['end_date'],
                'total_requests': stats['total_requests'],
                'total_tokens': stats['total_tokens'],
                'total_cost': stats['total_cost'],
                'total_generations': total_generations,
                'successful_requests': stats['successful_requests'],
                'failed_requests': stats['failed_requests'],
                'avg_processing_time_ms': stats['avg_processing_time_ms'],
                'by_provider': stats['by_provider'],
                'by_model': stats['by_model'],
                'by_request_type': stats['by_request_type']
            }
        }

        return response_data, 200

    except Exception as e:
        logger.error(f"Error fetching AI usage stats: {str(e)}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500,
            details={'error': str(e)})
