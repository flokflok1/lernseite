"""
AI Providers Connection Testing (DDD)

Endpoints for testing provider connections:
- POST /api/v1/admin/settings/ai/providers/<id>/test - Test provider connection

Uses:
- AIHealthMonitoringService for health checks
- Publishes AIProviderHealthChangedEvent on status changes
"""

from flask import Blueprint, jsonify, g
from typing import Dict, Any, Tuple
from datetime import datetime
import logging
import uuid
import time

from app.api.middleware.auth import permission_required
from app.infrastructure.persistence.repositories.ai.providers import AIProviderRepository
from app.application.services.system.audit.service import AuditService
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

# DDD Core Domain
from ..core.services import AIHealthMonitoringService
from ..core.events import (
    AIProviderHealthChangedEvent,
    EventPublisher,
    EventPriority
)
from ..core.value_objects import ProviderHealth

logger = logging.getLogger(__name__)

providers_testing_bp = Blueprint(
    'ai_providers_testing',
    __name__,
    url_prefix='/admin-panel/settings/ai/providers'
)


@providers_testing_bp.route('/<int:provider_id>/test', methods=['POST'])
@permission_required('admin.system:write')
def test_provider_connection(provider_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Test provider connection and update health status.

    Business Rules (enforced by AIHealthMonitoringService):
    1. Test actual API connectivity
    2. Validate API key works
    3. Check response time
    4. Update health status in DB

    Args:
        provider_id: The provider's database ID

    Returns:
        JSON response with test results and health status

    DDD:
    - Uses AIHealthMonitoringService to perform health check
    - Publishes AIProviderHealthChangedEvent if status changes
    """
    try:
        start_time = time.time()

        # Get provider
        provider = AIProviderRepository.get_by_id(provider_id)
        if not provider:
            return error_response(ErrorCode.AI_PROVIDER_NOT_FOUND, 404,
                details={'provider_id': provider_id})

        if not provider.get('has_api_key'):
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400,
                details={'message': 'Provider has no API key configured'})

        # Get previous health status
        previous_health = provider.get('health_status', 'unknown')

        # DDD: Use Health Monitoring Service to perform check
        health_result = AIHealthMonitoringService.check_provider_health(provider)

        # Calculate test duration
        test_duration = time.time() - start_time

        # Determine if health status changed
        new_health = health_result['health_status']
        health_changed = previous_health != new_health

        # Update provider health status in DB
        AIProviderRepository.update(
            provider_id,
            {
                'health_status': new_health,
                'last_health_check': datetime.utcnow()
            }
        )

        # DDD: Publish Domain Event if health changed
        if health_changed:
            event = AIProviderHealthChangedEvent(
                event_id=str(uuid.uuid4()),
                occurred_at=datetime.utcnow(),
                aggregate_id=str(provider_id),
                provider_id=str(provider_id),
                provider_name=provider.get('name'),
                previous_health=previous_health,
                new_health=new_health,
                response_time_ms=health_result.get('response_time_ms', 0),
                error_message=health_result.get('error_message'),
                priority=EventPriority.HIGH if new_health == 'unhealthy' else EventPriority.MEDIUM
            )
            EventPublisher.publish(event)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='test_provider_connection',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            details={
                'provider_name': provider.get('name'),
                'health_status': new_health,
                'health_changed': health_changed,
                'test_duration_seconds': round(test_duration, 2)
            }
        )

        return jsonify({
            'success': health_result['is_healthy'],
            'data': {
                'provider': {
                    'provider_id': provider.get('provider_id'),
                    'name': provider.get('name'),
                    'display_name': provider.get('display_name')
                },
                'health': {
                    'status': new_health,
                    'is_healthy': health_result['is_healthy'],
                    'previous_status': previous_health if health_changed else None,
                    'changed': health_changed
                },
                'test_results': {
                    'response_time_ms': health_result.get('response_time_ms'),
                    'api_accessible': health_result.get('api_accessible', False),
                    'models_available': health_result.get('models_available', 0),
                    'test_duration_seconds': round(test_duration, 2)
                },
                'error': health_result.get('error_message')
            },
            'message': (
                f'Provider {provider.get("display_name")} is {new_health}'
                if health_result['is_healthy']
                else f'Provider {provider.get("display_name")} failed health check'
            )
        }), 200 if health_result['is_healthy'] else 503

    except Exception as e:
        logger.error(f"Error testing provider {provider_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500,
            details={'error': str(e)})
