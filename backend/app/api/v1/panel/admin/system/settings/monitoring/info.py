"""
LernsystemX Admin System API - System Information Module

Endpoints:
- GET /api/v1/admin/system/version - System and API version information
- GET /api/v1/admin/system/deprecated-endpoints - List of deprecated endpoints
- GET /api/v1/admin/system/health/detailed - Detailed system health check

Phase 22 - Versioning & Change Management
Based on Dok 33 (Versioning-Change-Management.md)
"""

from flask import jsonify, current_app
from datetime import datetime

from .system_operations import api_v1
from app.api.middleware.auth import permission_required
from app.api.gateway.versioning import get_version_info
from app.api.v1.public.deprecation import list_deprecated_endpoints


@api_v1.route('/admin/settings/system/version', methods=['GET'])
@permission_required('admin.system:read')
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


@api_v1.route('/admin/settings/system/deprecated-endpoints', methods=['GET'])
@permission_required('admin.system:read')
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


@api_v1.route('/admin/settings/system/health/detailed', methods=['GET'])
@permission_required('admin.system:read')
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
        from app.api.v1.public.health import health_check_detailed
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
