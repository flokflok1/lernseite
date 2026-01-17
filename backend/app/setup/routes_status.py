"""
LernsystemX Setup - Status & Health Check Routes

REST API endpoints for installation status monitoring:
- GET /setup/status - Check installation status
- GET /setup/environment - Get environment info
- GET /setup/system-info - Get system information
- GET /setup/health - Health check
- GET /setup/status/full - Comprehensive system status
- GET /setup/status/summary - Lightweight status summary
- GET /setup/seed/status - Get seeding status

ISO/IEC/IEEE 26515:2018 compliant - API documentation
"""

from flask import request, jsonify, current_app
from app.setup import setup_bp
from app.setup.install_check import InstallationChecker
from app.setup.seeds import SeedData
from app.setup.verify import SetupVerification


@setup_bp.route('/status', methods=['GET'])
def get_status():
    """
    Get installation status

    Returns:
        JSON:
        {
            "installed": bool,
            "version": str or null,
            "requires_setup": bool,
            "install_info": dict or null
        }

    Example:
        GET /setup/status
        Response: {"installed": false, "requires_setup": true}
    """
    is_installed = InstallationChecker.is_installed()
    install_info = InstallationChecker.get_install_info() if is_installed else None

    return jsonify({
        'installed': is_installed,
        'version': install_info.get('version') if install_info else None,
        'requires_setup': not is_installed,
        'install_info': install_info
    }), 200


@setup_bp.route('/environment', methods=['GET'])
def get_environment_info():
    """
    Get environment configuration information

    Returns:
        JSON:
        {
            "success": bool,
            "env_file_exists": bool,
            "env_file_path": str,
            "is_valid": bool,
            "issues": list,
            "templates_available": {
                "development": bool,
                "production": bool
            }
        }

    Example:
        GET /setup/environment
        Response: {
            "success": true,
            "env_file_exists": false,
            "templates_available": {"development": true, "production": true}
        }
    """
    try:
        from app.setup.environment_setup import EnvironmentSetup

        info = EnvironmentSetup.get_environment_info()

        return jsonify({
            'success': True,
            **info
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@setup_bp.route('/seed/status', methods=['GET'])
def get_seed_status():
    """
    Get seeding status

    Returns:
        JSON:
        {
            "success": bool,
            "learning_methods": int,
            "roles": int,
            "categories": int,
            "expected": dict
        }

    Example:
        GET /setup/seed/status
        Response: {
            "success": true,
            "learning_methods": 21,
            "roles": 10,
            "categories": 8,
            "expected": {...}
        }
    """
    try:
        status = SeedData.get_seeding_status()

        return jsonify({
            'success': True,
            **status
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get seeding status',
            'details': str(e)
        }), 500


@setup_bp.route('/system-info', methods=['GET'])
def get_system_info():
    """
    Get system information

    Returns:
        JSON:
        {
            "success": bool,
            "python_version": str,
            "platform": str,
            "database_version": str,
            "table_counts": dict,
            "environment": str
        }

    Example:
        GET /setup/system-info
        Response: {
            "success": true,
            "python_version": "3.12.0",
            "platform": "Windows-10",
            "database_version": "PostgreSQL 16.0",
            "table_counts": {...}
        }
    """
    try:
        info = SetupVerification.get_system_info()

        return jsonify({
            'success': True,
            **info
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get system info',
            'details': str(e)
        }), 500


@setup_bp.route('/health', methods=['GET'])
def health_check():
    """
    Setup system health check

    Returns:
        JSON: {
            "status": "healthy",
            "service": str,
            "version": str
        }

    Example:
        GET /setup/health
        Response: {"status": "healthy", "service": "LernsystemX Setup Wizard"}
    """
    return jsonify({
        'status': 'healthy',
        'service': 'LernsystemX Setup Wizard',
        'version': '1.0.0'
    }), 200


@setup_bp.route('/status/full', methods=['GET'])
def get_full_status():
    """
    Get comprehensive system status

    Authentication:
        - Before installation: Public
        - After installation: Admin only

    Returns:
        JSON:
        {
            "success": bool,
            "installed": bool,
            "installation_completed_at": str,
            "environment": str,
            "system_version": str,
            "api_version": int,
            "api_versions_supported": [int],
            "db_schema_version": str,
            "last_migration": str,
            "last_migration_at": str,
            "has_pending_migrations": bool,
            "pending_migrations_count": int,
            "overall_health": "ok"|"warn"|"fail",
            "health_summary": {
                "passed": int,
                "warnings": int,
                "failed": int
            },
            "components": {
                "database": "ok"|"warn"|"fail",
                "redis": "ok"|"warn"|"fail",
                "security": "ok"|"warn"|"fail"
            },
            "timestamp": str
        }

    Example:
        GET /setup/status/full
    """
    try:
        from setup.status import SystemStatus

        status = SystemStatus.get_system_status()

        return jsonify({
            'success': True,
            **status
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get system status',
            'details': str(e)
        }), 500


@setup_bp.route('/status/summary', methods=['GET'])
def get_status_summary():
    """
    Get lightweight system status summary

    Returns:
        JSON:
        {
            "success": bool,
            "installed": bool,
            "system_version": str,
            "environment": str,
            "has_pending_migrations": bool,
            "timestamp": str
        }

    Example:
        GET /setup/status/summary
    """
    try:
        from setup.status import SystemStatus

        summary = SystemStatus.get_status_summary()

        return jsonify({
            'success': True,
            **summary
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get status summary',
            'details': str(e)
        }), 500
