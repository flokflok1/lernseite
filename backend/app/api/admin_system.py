"""
LernsystemX Admin System API

System administration endpoints for version info, deprecation reports, and system health:
- GET /api/v1/admin/system/version - System and API version information
- GET /api/v1/admin/system/deprecated-endpoints - List of deprecated endpoints
- GET /api/v1/admin/system/health/detailed - Detailed system health check
- GET /api/v1/admin/stats/users - User statistics (Phase 2.1)
- GET /api/v1/admin/stats/courses - Course statistics (Phase 2.1)
- GET /api/v1/admin/stats/system - System statistics (Phase 2.1)

Phase 22 - Versioning & Change Management
Phase 2.1 - Admin Dashboard Implementation
Based on Dok 33 (Versioning-Change-Management.md)
"""

from flask import request, jsonify, current_app, g
from datetime import datetime

from app.api import api_v1
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.gateway.versioning import get_version_info
from app.api.deprecation import list_deprecated_endpoints
from app.repositories.admin_repository import AdminRepository
from app.repositories.ai_provider_repository import AIProviderRepository
from app.models.admin import UserStatsResponse, CourseStatsResponse, SystemStatsResponse
from app.services.audit_service import AuditService
from app.database.connection import fetch_all, fetch_one


@api_v1.route('/admin/system/version', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_system_version():
    """
    Get comprehensive system and API version information.

    Returns detailed information about:
    - System version (SEMVER)
    - API versioning configuration
    - Supported API versions
    - Version detection strategy
    - Deprecation settings

    **Endpoint:** GET /api/v1/admin/system/version

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "system": {
                "version": "1.0.0",
                "environment": "production",
                "python_version": "3.12.0"
            },
            "api": {
                "current_version": 1,
                "supported_versions": [1],
                "default_version": 1,
                "support_window_months": 12,
                "deprecation_warning_months": 6
            },
            "detection": {
                "strategy": "url",
                "allow_header_override": false
            },
            "deprecation": {
                "enabled": true,
                "notice_url": "https://docs.lernsystemx.de/api/deprecation-notices"
            },
            "build": {
                "timestamp": "2025-01-15T10:30:00Z",
                "git_commit": "abc123def456"
            }
        }
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    """
    try:
        # Get version info from gateway
        version_info = get_version_info()

        # Add system-level information
        import sys
        import platform

        version_info['system'] = {
            'version': current_app.config.get('LSX_VERSION', '1.0.0'),
            'environment': current_app.config.get('LSX_ENV', 'production'),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'platform': platform.system(),
            'platform_version': platform.version()
        }

        # Add build information (if available)
        version_info['build'] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'git_commit': current_app.config.get('GIT_COMMIT', 'unknown')
        }

        return jsonify({
            'success': True,
            'data': version_info,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get version info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve version information',
            'message': str(e)
        }), 500


@api_v1.route('/admin/system/deprecated-endpoints', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_deprecated_endpoints():
    """
    List all deprecated API endpoints.

    Returns information about all endpoints marked as deprecated, including:
    - Endpoint path and methods
    - Deprecation date
    - Sunset date
    - Days until sunset
    - Replacement endpoint
    - Migration guide URL

    **Endpoint:** GET /api/v1/admin/system/deprecated-endpoints

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "total_deprecated": 2,
            "endpoints": [
                {
                    "endpoint": "old_users_endpoint",
                    "path": "/api/v1/users/old",
                    "methods": ["GET", "POST"],
                    "deprecation_date": "2025-06-01",
                    "sunset_date": "2026-06-01",
                    "days_until_sunset": 365,
                    "replacement": "/api/v2/users",
                    "migration_guide": "https://docs.lernsystemx.de/api/v1-to-v2/users",
                    "reason": "Replaced by improved v2 implementation"
                }
            ]
        }
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    """
    try:
        # Get list of deprecated endpoints
        deprecated = list_deprecated_endpoints(current_app)

        # Calculate days until sunset for each
        for endpoint in deprecated:
            if endpoint.get('sunset_date'):
                try:
                    sunset = datetime.fromisoformat(endpoint['sunset_date'])
                    delta = sunset - datetime.utcnow()
                    endpoint['days_until_sunset'] = delta.days
                except (ValueError, TypeError):
                    endpoint['days_until_sunset'] = None

        # Sort by days until sunset (most urgent first)
        deprecated_sorted = sorted(
            deprecated,
            key=lambda x: x.get('days_until_sunset', 9999) if x.get('days_until_sunset') is not None else 9999
        )

        return jsonify({
            'success': True,
            'data': {
                'total_deprecated': len(deprecated_sorted),
                'endpoints': deprecated_sorted
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get deprecated endpoints: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve deprecated endpoints',
            'message': str(e)
        }), 500


@api_v1.route('/admin/system/health/detailed', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_detailed_health():
    """
    Get detailed system health information.

    Includes version info, component status, and system metrics.

    **Endpoint:** GET /api/v1/admin/system/health/detailed

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "status": "healthy",
            "version": {
                "system": "1.0.0",
                "api": 1
            },
            "components": {
                "database": "healthy",
                "redis": "healthy",
                "celery": "healthy"
            },
            "metrics": {
                "uptime_seconds": 123456,
                "total_requests": 1000000,
                "deprecated_endpoint_calls": 150
            }
        }
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    """
    try:
        # Get version info
        version_info = get_version_info()

        # Get health status from existing health check
        from app.api.health import health_check_detailed
        health_response = health_check_detailed()

        # Combine with version info
        health_data = health_response[0].get_json()

        # Add version information
        if 'data' in health_data:
            health_data['data']['version'] = {
                'system': version_info.get('system_version'),
                'api_current': version_info.get('api', {}).get('current_version'),
                'api_supported': version_info.get('api', {}).get('supported_versions')
            }

            # Add deprecation metrics if available
            deprecated_endpoints = list_deprecated_endpoints(current_app)
            health_data['data']['deprecation'] = {
                'total_deprecated_endpoints': len(deprecated_endpoints),
                'deprecation_enabled': version_info.get('deprecation', {}).get('enabled')
            }

        return jsonify(health_data), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get detailed health: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve system health',
            'message': str(e)
        }), 500


# ============================================================================
# Phase 2.1 - Admin Dashboard Stats Endpoints
# ============================================================================

@api_v1.route('/admin/stats/users', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_admin_dashboard_user_stats():
    """
    Get user statistics for admin dashboard.

    Returns metrics about total, active, banned, and new users.

    **Endpoint:** GET /api/v1/admin/stats/users

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "total_users": 1250,
            "active_users": 450,
            "banned_users": 12,
            "new_users_30d": 87
        }
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    - 500: Server error
    """
    try:
        # Get user statistics from repository
        stats = AdminRepository.get_user_stats()

        # Validate response with Pydantic model
        response_data = UserStatsResponse(**stats)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='view_stats',
            resource_type='admin_stats',
            severity='info',
            details={'stats_type': 'users'}
        )

        return jsonify({
            'success': True,
            'data': response_data.dict(),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get user stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve user statistics',
            'message': str(e)
        }), 500


@api_v1.route('/admin/stats/courses', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_admin_dashboard_course_stats():
    """
    Get course statistics for admin dashboard.

    Returns metrics about total, published, pending, and rejected courses.

    **Endpoint:** GET /api/v1/admin/stats/courses

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "total_courses": 342,
            "published": 298,
            "pending_review": 32,
            "rejected": 12
        }
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    - 500: Server error
    """
    try:
        # Get course statistics from repository
        stats = AdminRepository.get_course_stats()

        # Validate response with Pydantic model
        response_data = CourseStatsResponse(**stats)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='view_stats',
            resource_type='admin_stats',
            severity='info',
            details={'stats_type': 'courses'}
        )

        return jsonify({
            'success': True,
            'data': response_data.dict(),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get course stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve course statistics',
            'message': str(e)
        }), 500


@api_v1.route('/admin/stats/system', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_admin_dashboard_system_stats():
    """
    Get system statistics for admin dashboard.

    Returns metrics about uptime, database latency, requests, and error rate.

    **Endpoint:** GET /api/v1/admin/stats/system

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "uptime": 123456.78,
            "db_latency": 12.34,
            "request_count_24h": 45678,
            "error_rate": 0.12
        }
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    - 500: Server error
    """
    try:
        # Get application start time for uptime calculation
        app_start_time = current_app.config.get('APP_START_TIME', datetime.utcnow())

        # Get system statistics from repository
        stats = AdminRepository.get_system_stats(app_start_time)

        # Validate response with Pydantic model
        response_data = SystemStatsResponse(**stats)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='view_stats',
            resource_type='admin_stats',
            severity='info',
            details={'stats_type': 'system'}
        )

        return jsonify({
            'success': True,
            'data': response_data.dict(),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get system stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve system statistics',
            'message': str(e)
        }), 500


@api_v1.route('/admin/audit-logs', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_admin_audit_logs():
    """
    Get audit logs for admin dashboard.

    Query Parameters:
        page: Page number (default: 1)
        limit: Items per page (default: 20, max: 100)
        user_id: Filter by user ID (optional)
        action: Filter by action (optional)
        severity: Filter by severity (optional)

    Returns:
        Paginated list of audit logs

    **Endpoint:** GET /api/v1/admin/audit-logs

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "logs": [...],
        "total": 1234,
        "page": 1,
        "limit": 20,
        "total_pages": 62
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    - 500: Server error
    """
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        user_id = request.args.get('user_id')
        action = request.args.get('action')
        severity = request.args.get('severity')

        # Build WHERE clause
        where_conditions = []
        params = []

        if user_id:
            where_conditions.append("user_id = %s")
            params.append(user_id)

        if action:
            where_conditions.append("action ILIKE %s")
            params.append(f"%{action}%")

        if severity:
            where_conditions.append("severity = %s")
            params.append(severity)

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # Count total
        count_query = f"SELECT COUNT(*) as total FROM audit_logs WHERE {where_clause}"
        total_result = fetch_one(count_query, tuple(params))
        total = total_result['total'] if total_result else 0

        # Calculate pagination
        total_pages = (total + limit - 1) // limit
        offset = (page - 1) * limit

        # Get logs
        logs_query = f"""
            SELECT
                log_id,
                user_id,
                action,
                resource_type,
                resource_id,
                description,
                metadata,
                severity,
                ip_address,
                user_agent,
                created_at
            FROM audit_logs
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """

        logs = fetch_all(logs_query, tuple(params + [limit, offset]))

        # Convert UUIDs/timestamps/IPs to strings
        for log in logs:
            if 'log_id' in log and log['log_id']:
                log['log_id'] = str(log['log_id'])
            if 'user_id' in log and log['user_id']:
                log['user_id'] = str(log['user_id'])
            if 'resource_id' in log and log['resource_id']:
                log['resource_id'] = str(log['resource_id'])
            if 'ip_address' in log and log['ip_address']:
                log['ip_address'] = str(log['ip_address'])
            if 'created_at' in log:
                log['created_at'] = log['created_at'].isoformat() if log['created_at'] else None

        # Audit log (meta - logging that we viewed logs)
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='view_audit_logs',
            resource_type='audit_logs',
            severity='info',
            details={'filters': {'user_id': user_id, 'action': action, 'severity': severity}}
        )

        return jsonify({
            'success': True,
            'logs': logs,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': total_pages
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get audit logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve audit logs',
            'message': str(e)
        }), 500


# ============================================================================
# Phase B24-05 - AI Provider Management Endpoints
# ============================================================================

@api_v1.route('/admin/ai/providers', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_providers():
    """
    Get all AI providers.

    Returns list of configured AI providers with their status.
    API keys are NOT returned, only whether they are configured.

    **Endpoint:** GET /api/v1/admin/ai/providers

    **Authentication:** Required (Admin only)

    **Response:**
    ```json
    {
        "success": true,
        "data": [
            {
                "provider_id": 1,
                "name": "openai",
                "display_name": "OpenAI",
                "provider_type": "openai",
                "active": true,
                "has_api_key": true,
                "priority": 100
            }
        ]
    }
    ```
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        providers = AIProviderRepository.get_all(include_inactive=include_inactive)

        # Convert timestamps to ISO format
        for provider in providers:
            if provider.get('created_at'):
                provider['created_at'] = provider['created_at'].isoformat()
            if provider.get('updated_at'):
                provider['updated_at'] = provider['updated_at'].isoformat()
            if provider.get('last_validated'):
                provider['last_validated'] = provider['last_validated'].isoformat()

        return jsonify({
            'success': True,
            'data': providers,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get AI providers: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI providers',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_provider(provider_id: int):
    """
    Get single AI provider details.

    **Endpoint:** GET /api/v1/admin/ai/providers/<provider_id>
    """
    try:
        provider = AIProviderRepository.get_by_id(provider_id)

        if not provider:
            return jsonify({
                'success': False,
                'error': 'Provider not found'
            }), 404

        # Convert timestamps
        if provider.get('created_at'):
            provider['created_at'] = provider['created_at'].isoformat()
        if provider.get('updated_at'):
            provider['updated_at'] = provider['updated_at'].isoformat()
        if provider.get('last_validated'):
            provider['last_validated'] = provider['last_validated'].isoformat()

        return jsonify({
            'success': True,
            'data': provider
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get AI provider: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI provider',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>/api-key', methods=['PUT'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_ai_provider_api_key(provider_id: int):
    """
    Update AI provider API key.

    The API key is encrypted before storage.

    **Endpoint:** PUT /api/v1/admin/ai/providers/<provider_id>/api-key

    **Body:**
    ```json
    {
        "api_key": "sk-..."
    }
    ```
    """
    try:
        data = request.get_json()

        if not data or 'api_key' not in data:
            return jsonify({
                'success': False,
                'error': 'API key is required'
            }), 400

        api_key = data['api_key'].strip()

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key cannot be empty'
            }), 400

        # Update API key (encrypted)
        result = AIProviderRepository.update_api_key(provider_id, api_key)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Provider not found'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='update_api_key',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            severity='warning',
            details={'provider_name': result.get('name')}
        )

        current_app.logger.info(f"AI provider API key updated: {result.get('name')} by user {g.current_user['user_id']}")

        return jsonify({
            'success': True,
            'message': 'API key updated successfully',
            'data': result
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to update AI provider API key: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update API key',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>/api-key', methods=['DELETE'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def delete_ai_provider_api_key(provider_id: int):
    """
    Remove API key from provider (deactivates provider).

    **Endpoint:** DELETE /api/v1/admin/ai/providers/<provider_id>/api-key
    """
    try:
        result = AIProviderRepository.clear_api_key(provider_id)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Provider not found'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='delete_api_key',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            severity='warning',
            details={'provider_name': result.get('name')}
        )

        return jsonify({
            'success': True,
            'message': 'API key removed successfully',
            'data': result
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to delete AI provider API key: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete API key',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_ai_provider(provider_id: int):
    """
    Update AI provider settings.

    **Endpoint:** PATCH /api/v1/admin/ai/providers/<provider_id>

    **Body:**
    ```json
    {
        "active": true,
        "priority": 100,
        "rate_limit_per_minute": 60
    }
    ```
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        result = AIProviderRepository.update_provider(provider_id, data)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Provider not found'
            }), 404

        # Convert timestamps
        if result.get('created_at'):
            result['created_at'] = result['created_at'].isoformat() if hasattr(result['created_at'], 'isoformat') else result['created_at']
        if result.get('updated_at'):
            result['updated_at'] = result['updated_at'].isoformat() if hasattr(result['updated_at'], 'isoformat') else result['updated_at']

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='update_provider',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            severity='info',
            details={'changes': list(data.keys())}
        )

        return jsonify({
            'success': True,
            'message': 'Provider updated successfully',
            'data': result
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to update AI provider: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update provider',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/providers/<int:provider_id>/test', methods=['POST'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def test_ai_provider(provider_id: int):
    """
    Test AI provider connection.

    Validates the API key by making a simple API call.

    **Endpoint:** POST /api/v1/admin/ai/providers/<provider_id>/test
    """
    try:
        provider = AIProviderRepository.get_by_name_by_id(provider_id) if hasattr(AIProviderRepository, 'get_by_name_by_id') else AIProviderRepository.get_by_id(provider_id)

        if not provider:
            return jsonify({
                'success': False,
                'error': 'Provider not found'
            }), 404

        # Get decrypted API key
        provider_full = AIProviderRepository.get_by_name(provider.get('name'))
        if not provider_full or not provider_full.get('encrypted_api_key'):
            return jsonify({
                'success': False,
                'error': 'No API key configured for this provider'
            }), 400

        api_key = AIProviderRepository._decrypt_api_key(
            provider_full.get('encrypted_api_key'),
            provider_full.get('encryption_salt')
        )

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Failed to decrypt API key'
            }), 500

        # Test based on provider type
        provider_type = provider.get('provider_type')
        test_result = {'valid': False, 'message': 'Unknown provider type'}

        import time
        start_time = time.time()

        if provider_type == 'openai':
            test_result = _test_openai_key(api_key)
        elif provider_type == 'anthropic':
            test_result = _test_anthropic_key(api_key)
        elif provider_type == 'google':
            test_result = _test_google_key(api_key)
        else:
            test_result = {'valid': False, 'message': f'Testing not implemented for {provider_type}'}

        response_time_ms = int((time.time() - start_time) * 1000)

        # Log health check
        status = 'healthy' if test_result['valid'] else 'down'
        AIProviderRepository.log_health_check(
            provider_id,
            status,
            response_time_ms,
            None if test_result['valid'] else test_result.get('message')
        )

        # Update validation timestamp
        if test_result['valid']:
            AIProviderRepository.validate_api_key(provider_id, True)

        return jsonify({
            'success': True,
            'data': {
                'valid': test_result['valid'],
                'message': test_result.get('message', 'OK'),
                'response_time_ms': response_time_ms
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to test AI provider: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to test provider',
            'message': str(e)
        }), 500


def _test_openai_key(api_key: str) -> dict:
    """Test OpenAI API key validity"""
    try:
        import requests
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        if response.status_code == 200:
            return {'valid': True, 'message': 'API key is valid'}
        elif response.status_code == 401:
            return {'valid': False, 'message': 'Invalid API key'}
        else:
            return {'valid': False, 'message': f'API error: {response.status_code}'}
    except Exception as e:
        return {'valid': False, 'message': str(e)}


def _test_anthropic_key(api_key: str) -> dict:
    """Test Anthropic API key validity"""
    try:
        import requests
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            json={
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 10,
                'messages': [{'role': 'user', 'content': 'Hi'}]
            },
            timeout=15
        )
        if response.status_code == 200:
            return {'valid': True, 'message': 'API key is valid'}
        elif response.status_code == 401:
            return {'valid': False, 'message': 'Invalid API key'}
        else:
            error_detail = response.json().get('error', {}).get('message', 'Unknown error')
            return {'valid': False, 'message': f'API error: {error_detail}'}
    except Exception as e:
        return {'valid': False, 'message': str(e)}


def _test_google_key(api_key: str) -> dict:
    """Test Google AI API key validity"""
    try:
        import requests
        response = requests.get(
            f'https://generativelanguage.googleapis.com/v1/models?key={api_key}',
            timeout=10
        )
        if response.status_code == 200:
            return {'valid': True, 'message': 'API key is valid'}
        elif response.status_code == 400 or response.status_code == 403:
            return {'valid': False, 'message': 'Invalid API key'}
        else:
            return {'valid': False, 'message': f'API error: {response.status_code}'}
    except Exception as e:
        return {'valid': False, 'message': str(e)}


# ============================================================================
# Phase C3.0 - AI Model Selector System
# ============================================================================

@api_v1.route('/admin/ai/models/grouped', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_models_grouped():
    """
    Get AI models grouped by provider (Legacy format for AdminAISettingsPage).

    This endpoint returns models in the provider-grouped format that
    AdminAISettingsPage.vue expects.

    **Endpoint:** GET /api/v1/admin/ai/models/grouped

    **Authentication:** Required (Admin only)

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "openai": {
                "display_name": "OpenAI",
                "models": [
                    {"name": "gpt-4o", "input_price": 0.005, "output_price": 0.015}
                ]
            },
            "anthropic": {
                "display_name": "Anthropic",
                "models": [...]
            }
        }
    }
    ```
    """
    try:
        # Query models from database grouped by provider
        query = """
            SELECT
                m.model_name,
                m.display_name,
                m.input_price_per_1k,
                m.output_price_per_1k,
                m.max_output_tokens,
                m.context_window,
                p.name as provider_name,
                p.display_name as provider_display_name
            FROM ai_models m
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.active = TRUE
            ORDER BY p.name ASC, m.model_name ASC
        """
        models = fetch_all(query, ())

        # Build provider-grouped response format
        result = {}
        for model in models:
            provider_name = model.get('provider_name') or 'unknown'
            if provider_name not in result:
                result[provider_name] = {
                    'display_name': model.get('provider_display_name') or provider_name.title(),
                    'models': []
                }
            result[provider_name]['models'].append({
                'name': model.get('model_name'),
                'input_price': model.get('input_price_per_1k') or 0,
                'output_price': model.get('output_price_per_1k') or 0,
                'max_tokens': model.get('max_output_tokens') or 4096,
                'context_window': model.get('context_window') or 128000
            })

        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get AI models (grouped): {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI models',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/models/registry', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_models_registry():
    """
    Get all available AI models for Model Selector Window (Phase C3.0).

    Returns flat list of all AI models with category, cost, speed info.
    Falls back to AIAdapter.PROVIDERS if database table is empty.
    Used by AdminModelSelectorWindow.vue.

    **Endpoint:** GET /api/v1/admin/ai/models/registry

    **Authentication:** Required (Admin only)

    **Query Parameters:**
        category: Filter by category (reasoning, chat, realtime, audio, image, embedding, moderation)
        active_only: Only show active models (default: true)
        search: Search in model name or description
        provider: Filter by provider name (openai, anthropic, etc.)
        configured_only: Only show models from providers with API keys (default: false)

    **Response:**
    ```json
    {
        "success": true,
        "data": [
            {
                "model_id": 1,
                "model_name": "gpt-4o",
                "display_name": "GPT-4o",
                "category": "chat",
                "description": "Most capable GPT-4 model with vision",
                "cost_level": "high",
                "speed": "fast",
                "context_window": 128000,
                "supports_vision": true,
                "is_default": true,
                "active": true
            }
        ],
        "categories": [
            {"id": "chat", "label": "Chat/Reasoning"},
            {"id": "image", "label": "Image Generation"},
            ...
        ]
    }
    ```
    """
    try:
        from app.services.ai_adapter import AIAdapter

        # Parse query parameters
        category_filter = request.args.get('category')
        search = request.args.get('search', '').lower()
        provider_filter = request.args.get('provider')
        configured_only = request.args.get('configured_only', 'false').lower() == 'true'

        # Get providers with API key status
        providers_data = []
        configured_provider_names = set()
        try:
            provider_query = """
                SELECT
                    provider_id,
                    name,
                    display_name,
                    CASE WHEN encrypted_api_key IS NOT NULL THEN TRUE ELSE FALSE END as has_api_key
                FROM ai_providers
                WHERE active = TRUE
                ORDER BY display_name ASC
            """
            providers_data = fetch_all(provider_query, ())
            configured_provider_names = {p['name'] for p in providers_data if p.get('has_api_key')}
        except Exception as prov_err:
            current_app.logger.warning(f"Failed to fetch providers: {prov_err}")

        # Try database first
        models = []
        try:
            query = """
                SELECT
                    m.model_id,
                    m.model_name,
                    m.display_name,
                    m.model_type,
                    m.category,
                    m.description,
                    m.cost_level,
                    m.speed,
                    m.context_window,
                    m.max_output_tokens,
                    m.supports_vision,
                    m.supports_functions,
                    m.supports_streaming,
                    m.is_default,
                    m.active,
                    m.input_price_per_1k,
                    m.output_price_per_1k,
                    p.name as provider
                FROM ai_models m
                LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
                WHERE m.active = TRUE
                ORDER BY m.model_name ASC
            """
            models = fetch_all(query, ())
        except Exception as db_err:
            current_app.logger.warning(f"Database query failed, using AIAdapter fallback: {db_err}")

        # Fallback disabled for testing - only show database models
        # To re-enable fallback, uncomment the block below
        # if not models:
        #     model_id = 1
        #     for provider_name, provider_data in AIAdapter.PROVIDERS.items():
        #         ... (fallback code)

        # Apply filters
        if category_filter:
            models = [m for m in models if m.get('category') == category_filter]

        if provider_filter:
            models = [m for m in models if m.get('provider') == provider_filter]

        if configured_only and configured_provider_names:
            models = [m for m in models if m.get('provider') in configured_provider_names]

        if search:
            models = [m for m in models if
                      search in m.get('model_name', '').lower() or
                      search in m.get('display_name', '').lower() or
                      search in (m.get('description') or '').lower()]

        # Sort by category priority, then default, then name
        category_order = {'chat': 1, 'reasoning': 2, 'coding': 3, 'search': 4, 'agent': 5,
                          'realtime': 6, 'audio': 7, 'video': 8, 'image': 9,
                          'embedding': 10, 'moderation': 11, 'open-source': 12, 'legacy': 13}
        models.sort(key=lambda m: (
            category_order.get(m.get('category', 'chat'), 99),
            0 if m.get('is_default') else 1,
            m.get('model_name', '')
        ))

        # Get unique categories from models
        unique_cats = sorted(set(m.get('category', 'chat') for m in models))
        category_labels = {
            'chat': 'Chat',
            'reasoning': 'Reasoning',
            'coding': 'Coding',
            'search': 'Web Search',
            'agent': 'Agentic',
            'realtime': 'Realtime',
            'audio': 'Audio',
            'video': 'Video',
            'image': 'Image',
            'embedding': 'Embedding',
            'moderation': 'Moderation',
            'open-source': 'Open Source',
            'legacy': 'Legacy'
        }
        categories = [{'id': c, 'label': category_labels.get(c, c.title())} for c in unique_cats]

        return jsonify({
            'success': True,
            'data': models,
            'categories': categories,
            'providers': providers_data,
            'total': len(models),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get AI models registry: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI models',
            'message': str(e)
        }), 500


# Note: POST /admin/ai/models/sync is now in admin_ai_models.py (sync_ai_models)
# This endpoint was removed to avoid route conflicts


@api_v1.route('/admin/ai/models/<int:model_id>/default', methods=['PATCH'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def set_ai_model_default(model_id: int):
    """
    Set an AI model as the default for its category (Phase C3.0).

    **Endpoint:** PATCH /api/v1/admin/ai/models/<model_id>/default

    **Authentication:** Required (Admin only)

    **Body:**
    ```json
    {
        "is_default": true
    }
    ```
    """
    try:
        data = request.get_json() or {}
        is_default = data.get('is_default', True)

        # Get model info
        model = fetch_one(
            "SELECT model_id, model_name, category FROM ai_models WHERE model_id = %s",
            (model_id,)
        )

        if not model:
            return jsonify({
                'success': False,
                'error': 'Model not found'
            }), 404

        from app.database.connection import execute_query

        if is_default:
            # First, unset default for all models in this category
            execute_query(
                "UPDATE ai_models SET is_default = FALSE WHERE category = %s",
                (model['category'],)
            )

        # Set/unset this model as default
        execute_query(
            "UPDATE ai_models SET is_default = %s, updated_at = NOW() WHERE model_id = %s",
            (is_default, model_id)
        )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='set_default_model',
            resource_type='ai_models',
            resource_id=str(model_id),
            severity='info',
            details={'model_name': model['model_name'], 'category': model['category'], 'is_default': is_default}
        )

        return jsonify({
            'success': True,
            'message': f"Model '{model['model_name']}' {'set as' if is_default else 'removed as'} default for {model['category']}",
            'data': {
                'model_id': model_id,
                'model_name': model['model_name'],
                'category': model['category'],
                'is_default': is_default
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to set default model: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to set default model',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/models/default', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_default_ai_model():
    """
    Get the current default AI model (for chat category).

    **Endpoint:** GET /api/v1/admin/ai/models/default

    **Query Parameters:**
        category: Category to get default for (default: 'chat')
    """
    try:
        category = request.args.get('category', 'chat')

        model = fetch_one("""
            SELECT model_id, model_name, display_name, category, cost_level, speed
            FROM ai_models
            WHERE category = %s AND is_default = TRUE AND active = TRUE
            LIMIT 1
        """, (category,))

        if not model:
            # Fallback to gpt-4o if no default set
            model = fetch_one("""
                SELECT model_id, model_name, display_name, category, cost_level, speed
                FROM ai_models
                WHERE model_name = 'gpt-4o' AND active = TRUE
                LIMIT 1
            """)

        return jsonify({
            'success': True,
            'data': model
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get default model: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get default model',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/settings', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_ai_settings():
    """
    Get global AI settings including default provider and model.

    **Endpoint:** GET /api/v1/admin/ai/settings
    """
    try:
        # Get current settings from config or database
        settings = {
            'default_provider': current_app.config.get('AI_DEFAULT_PROVIDER', 'openai'),
            'default_model': current_app.config.get('AI_DEFAULT_MODEL', 'gpt-4o-mini'),
            'max_tokens': current_app.config.get('AI_MAX_TOKENS', 4096),
            'temperature': current_app.config.get('AI_TEMPERATURE', 0.7)
        }

        return jsonify({
            'success': True,
            'data': settings,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get AI settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI settings',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/settings', methods=['PUT'])
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_ai_settings():
    """
    Update global AI settings.

    **Endpoint:** PUT /api/v1/admin/ai/settings

    **Body:**
    ```json
    {
        "default_provider": "openai",
        "default_model": "gpt-5-mini"
    }
    ```
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Validate provider and model
        from app.services.ai_adapter import AIAdapter

        if 'default_provider' in data:
            provider = data['default_provider']
            if provider not in AIAdapter.PROVIDERS:
                return jsonify({
                    'success': False,
                    'error': f'Invalid provider: {provider}'
                }), 400

        if 'default_model' in data and 'default_provider' in data:
            provider = data['default_provider']
            model = data['default_model']
            if model not in AIAdapter.PROVIDERS.get(provider, {}).get('models', {}):
                return jsonify({
                    'success': False,
                    'error': f'Invalid model: {model} for provider {provider}'
                }), 400

        # Update settings in database
        # For now, we'll just update the app config (in production this should be stored in DB)
        if 'default_provider' in data:
            current_app.config['AI_DEFAULT_PROVIDER'] = data['default_provider']
        if 'default_model' in data:
            current_app.config['AI_DEFAULT_MODEL'] = data['default_model']
        if 'max_tokens' in data:
            current_app.config['AI_MAX_TOKENS'] = int(data['max_tokens'])
        if 'temperature' in data:
            current_app.config['AI_TEMPERATURE'] = float(data['temperature'])

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='update_ai_settings',
            resource_type='ai_settings',
            severity='warning',
            details={'changes': list(data.keys())}
        )

        return jsonify({
            'success': True,
            'message': 'AI settings updated successfully',
            'data': {
                'default_provider': current_app.config.get('AI_DEFAULT_PROVIDER'),
                'default_model': current_app.config.get('AI_DEFAULT_MODEL'),
                'max_tokens': current_app.config.get('AI_MAX_TOKENS'),
                'temperature': current_app.config.get('AI_TEMPERATURE')
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to update AI settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update AI settings',
            'message': str(e)
        }), 500
