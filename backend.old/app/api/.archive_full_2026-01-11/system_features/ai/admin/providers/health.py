"""
AI Providers Health Monitoring (DDD)

Endpoints for provider health monitoring:
- GET /api/v1/admin/ai/providers/<id>/health - Get current health status
- GET /api/v1/admin/ai/providers/<id>/health/history - Get health history
- GET /api/v1/admin/ai/providers/health - Get health overview for all providers

Uses:
- AIHealthMonitoringService for health checks
- ProviderHealth Value Object for health status representation
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.ai.providers import AIProviderRepository

# DDD Core Domain
from app.api.system_features.ai.core.services import AIHealthMonitoringService

logger = logging.getLogger(__name__)

providers_health_bp = Blueprint(
    'ai_providers_health',
    __name__,
    url_prefix='/api/v1/admin/ai/providers'
)


@providers_health_bp.route('/<int:provider_id>/health', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_provider_health(provider_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get current health status for a provider.

    Args:
        provider_id: The provider's database ID

    Returns:
        JSON response with current health status

    DDD: Uses AIHealthMonitoringService for health representation
    """
    try:
        provider = AIProviderRepository.get_by_id(provider_id)
        if not provider:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PROVIDER_NOT_FOUND',
                    'message': f'Provider {provider_id} not found'
                }
            }), 404

        # Get current health status
        health_status = provider.get('health_status', 'unknown')
        last_check = provider.get('last_health_check')

        # Calculate time since last check
        time_since_check = None
        if last_check:
            delta = datetime.utcnow() - last_check
            time_since_check = {
                'seconds': int(delta.total_seconds()),
                'minutes': int(delta.total_seconds() / 60),
                'hours': int(delta.total_seconds() / 3600),
                'last_check': last_check.isoformat()
            }

        return jsonify({
            'success': True,
            'data': {
                'provider': {
                    'provider_id': provider.get('provider_id'),
                    'name': provider.get('name'),
                    'display_name': provider.get('display_name')
                },
                'health': {
                    'status': health_status,
                    'is_healthy': health_status == 'healthy',
                    'has_api_key': provider.get('has_api_key', False),
                    'last_check': last_check.isoformat() if last_check else None,
                    'time_since_check': time_since_check,
                    'needs_check': (
                        not last_check or
                        (datetime.utcnow() - last_check) > timedelta(hours=1)
                    )
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting health for provider {provider_id}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_HEALTH_ERROR',
                'message': str(e)
            }
        }), 500


@providers_health_bp.route('/<int:provider_id>/health/history', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_provider_health_history(provider_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get health check history for a provider.

    Query Parameters:
        days (int): Number of days to look back (default: 7, max: 90)

    Args:
        provider_id: The provider's database ID

    Returns:
        JSON response with health check history
    """
    try:
        provider = AIProviderRepository.get_by_id(provider_id)
        if not provider:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PROVIDER_NOT_FOUND',
                    'message': f'Provider {provider_id} not found'
                }
            }), 404

        # Get time range
        days = min(int(request.args.get('days', 7)), 90)
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get health history from repository
        health_history = AIProviderRepository.get_health_history(
            provider_id,
            start_date
        )

        # Calculate statistics
        total_checks = len(health_history)
        healthy_checks = sum(1 for h in health_history if h.get('health_status') == 'healthy')
        unhealthy_checks = sum(1 for h in health_history if h.get('health_status') == 'unhealthy')
        degraded_checks = sum(1 for h in health_history if h.get('health_status') == 'degraded')

        uptime_percentage = (healthy_checks / total_checks * 100) if total_checks > 0 else 0

        # Calculate average response time
        response_times = [h.get('response_time_ms', 0) for h in health_history if h.get('response_time_ms')]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return jsonify({
            'success': True,
            'data': {
                'provider': {
                    'provider_id': provider.get('provider_id'),
                    'name': provider.get('name'),
                    'display_name': provider.get('display_name')
                },
                'period': {
                    'days': days,
                    'start_date': start_date.isoformat(),
                    'end_date': datetime.utcnow().isoformat()
                },
                'statistics': {
                    'total_checks': total_checks,
                    'healthy_checks': healthy_checks,
                    'unhealthy_checks': unhealthy_checks,
                    'degraded_checks': degraded_checks,
                    'uptime_percentage': round(uptime_percentage, 2),
                    'average_response_time_ms': round(avg_response_time, 2)
                },
                'history': health_history
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting health history for provider {provider_id}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_HEALTH_HISTORY_ERROR',
                'message': str(e)
            }
        }), 500


@providers_health_bp.route('/health', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_all_providers_health() -> Tuple[Dict[str, Any], int]:
    """
    Get health overview for all providers.

    Query Parameters:
        include_inactive (bool): Include inactive providers (default: false)

    Returns:
        JSON response with health status for all providers
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

        # Get all providers
        providers = AIProviderRepository.get_all(include_inactive=include_inactive)

        # Build health overview
        health_overview = []
        total_healthy = 0
        total_unhealthy = 0
        total_degraded = 0
        total_unknown = 0

        for provider in providers:
            health_status = provider.get('health_status', 'unknown')
            last_check = provider.get('last_health_check')

            # Count by status
            if health_status == 'healthy':
                total_healthy += 1
            elif health_status == 'unhealthy':
                total_unhealthy += 1
            elif health_status == 'degraded':
                total_degraded += 1
            else:
                total_unknown += 1

            # Calculate time since last check
            needs_check = False
            if last_check:
                time_since_check = datetime.utcnow() - last_check
                needs_check = time_since_check > timedelta(hours=1)
            else:
                needs_check = True

            health_overview.append({
                'provider_id': provider.get('provider_id'),
                'name': provider.get('name'),
                'display_name': provider.get('display_name'),
                'health_status': health_status,
                'is_healthy': health_status == 'healthy',
                'has_api_key': provider.get('has_api_key', False),
                'active': provider.get('active', True),
                'last_health_check': last_check.isoformat() if last_check else None,
                'needs_check': needs_check
            })

        # Overall system health
        total_providers = len(providers)
        system_health = 'healthy'
        if total_unhealthy > 0:
            system_health = 'degraded' if total_healthy > total_unhealthy else 'unhealthy'
        elif total_degraded > 0:
            system_health = 'degraded'
        elif total_unknown == total_providers:
            system_health = 'unknown'

        return jsonify({
            'success': True,
            'data': {
                'system_health': {
                    'overall_status': system_health,
                    'total_providers': total_providers,
                    'healthy': total_healthy,
                    'unhealthy': total_unhealthy,
                    'degraded': total_degraded,
                    'unknown': total_unknown
                },
                'providers': health_overview,
                'recommendations': _get_health_recommendations(
                    total_unhealthy,
                    total_degraded,
                    total_unknown
                )
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting all providers health: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_ALL_HEALTH_ERROR',
                'message': str(e)
            }
        }), 500


def _get_health_recommendations(
    unhealthy_count: int,
    degraded_count: int,
    unknown_count: int
) -> list:
    """
    Get health recommendations based on current status.

    Args:
        unhealthy_count: Number of unhealthy providers
        degraded_count: Number of degraded providers
        unknown_count: Number of providers with unknown health

    Returns:
        List of recommendation strings
    """
    recommendations = []

    if unhealthy_count > 0:
        recommendations.append(
            f'{unhealthy_count} provider(s) are unhealthy. '
            'Check API keys and connectivity.'
        )

    if degraded_count > 0:
        recommendations.append(
            f'{degraded_count} provider(s) have degraded performance. '
            'Consider switching default models.'
        )

    if unknown_count > 0:
        recommendations.append(
            f'{unknown_count} provider(s) have not been checked. '
            'Run health checks to verify status.'
        )

    if not recommendations:
        recommendations.append('All providers are healthy.')

    return recommendations
