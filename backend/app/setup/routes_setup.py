"""
LernsystemX Setup - Admin User & Environment Setup Routes

REST API endpoints for initial system setup:
- POST /setup/environment - Configure environment (dev/prod)
- POST /setup/check - Run system checks
- POST /setup/admin - Create admin user

Organization and AI configuration endpoints are in routes_setup_config.py

ISO/IEC/IEEE 26515:2018 compliant - API documentation
"""

import os
from flask import request, jsonify, current_app
from app.setup import setup_bp
from app.setup.system_check import SystemCheck
from app.setup.install_check import InstallationChecker
from app.setup.admin_setup import AdminSetup
from app.setup.environment_setup import EnvironmentSetup
from app.extensions import db_pool, init_db_pool


@setup_bp.route('/environment', methods=['POST'])
def configure_environment():
    """
    Configure environment and create .env file

    Request Body:
        {
            "environment": "development"|"production",
            "overwrite": bool (optional, default false),
            "custom_values": dict (optional)
        }

    Returns:
        JSON:
        {
            "success": bool,
            "message": str,
            "environment": str
        }

    Example:
        POST /setup/environment
        Body: {"environment": "development"}
        Response: {
            "success": true,
            "message": "Environment configured successfully for development",
            "environment": "development"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        environment = data.get('environment')
        if not environment:
            return jsonify({
                'success': False,
                'error': 'Environment parameter is required (development or production)'
            }), 400

        if environment not in ['development', 'production']:
            return jsonify({
                'success': False,
                'error': f'Invalid environment: {environment}. Must be "development" or "production"'
            }), 400

        # Always overwrite .env during setup wizard - if user is running setup, they want a fresh install
        overwrite = data.get('overwrite', True)
        custom_values = data.get('custom_values', {})

        # Setup environment
        success, message = EnvironmentSetup.setup_environment(
            environment=environment,
            custom_values=custom_values,
            overwrite=overwrite
        )

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'environment': environment
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@setup_bp.route('/check', methods=['POST'])
def run_system_check():
    """
    Run comprehensive system checks

    Returns:
        JSON:
        {
            "success": bool,
            "can_proceed": bool,
            "checks": [
                {
                    "name": str,
                    "status": "ok"|"error"|"warning",
                    "message": str,
                    "details": str
                }
            ]
        }

    Example:
        POST /setup/check
        Response: {
            "success": true,
            "can_proceed": true,
            "checks": [...]
        }
    """
    try:
        all_passed, checks = SystemCheck.check_all()

        return jsonify({
            'success': True,
            'can_proceed': all_passed,
            'checks': checks
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'System check failed',
            'details': str(e)
        }), 500


@setup_bp.route('/admin', methods=['POST'])
def create_admin():
    """
    Create superadmin user with 2FA support

    Request Body:
        {
            "email": str,
            "password": str,
            "first_name": str,
            "last_name": str,
            "enable_2fa": bool (optional, default: false)
        }

    Returns:
        JSON:
        {
            "success": bool,
            "user_id": int,
            "email": str,
            "recovery_codes": [str],
            "totp_secret": str (if 2FA enabled),
            "qr_code": str (if 2FA enabled),
            "message": str
        }

    Example:
        POST /setup/admin
        Body: {
            "email": "admin@lsx.de",
            "password": "SecurePass123!",
            "first_name": "Admin",
            "last_name": "User",
            "enable_2fa": true
        }
    """
    try:
        current_app.logger.info("=== Admin creation endpoint called ===")

        # Check if already installed
        is_already_installed = InstallationChecker.is_installed()
        current_app.logger.info(f"Installation check: {is_already_installed}")
        if is_already_installed:
            current_app.logger.warning("Admin creation blocked - system already installed")
            return jsonify({
                'success': False,
                'error': 'System already installed',
                'message': 'Admin creation can only run during setup'
            }), 400

        # Ensure database pool is initialized
        current_app.logger.info(f"Database pool initialized: {db_pool is not None}")
        if db_pool is None:
            database_url = os.getenv('DATABASE_URL')
            current_app.logger.info(f"DATABASE_URL from env: {'set' if database_url else 'not set'}")
            if not database_url:
                return jsonify({
                    'success': False,
                    'error': 'Database not configured'
                }), 500

            init_db_pool(database_url)
            current_app.logger.info("Database pool initialized successfully")

        # Validate request data
        data = request.get_json()
        current_app.logger.info(f"Request data received: {data is not None}")
        if data:
            current_app.logger.info(f"Request data keys: {list(data.keys())}")

        if not data:
            current_app.logger.error("No data provided in request")
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        required_fields = ['email', 'password', 'first_name', 'last_name']
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({
                'success': False,
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400

        # Validate password
        valid_password, password_msg = AdminSetup.validate_password(data['password'])
        if not valid_password:
            return jsonify({
                'success': False,
                'error': 'Password validation failed',
                'details': password_msg
            }), 400

        # Validate email
        valid_email, email_msg = AdminSetup.validate_email(data['email'])
        if not valid_email:
            return jsonify({
                'success': False,
                'error': 'Email validation failed',
                'details': email_msg
            }), 400

        # Create admin user
        enable_2fa = data.get('enable_2fa', False)
        admin_result = AdminSetup.create_admin(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            enable_2fa=enable_2fa
        )

        response = {
            'success': True,
            'user_id': admin_result['user_id'],
            'email': admin_result['email'],
            'first_name': admin_result['first_name'],
            'last_name': admin_result['last_name'],
            'recovery_codes': admin_result['recovery_codes'],
            'message': 'Admin user created successfully'
        }

        # Add 2FA info if enabled
        if enable_2fa and admin_result['totp_secret']:
            response['totp_secret'] = admin_result['totp_secret']
            response['two_factor_enabled'] = True

            # Generate QR code
            qr_code = AdminSetup.generate_qr_code(
                admin_result['email'],
                admin_result['totp_secret']
            )
            if qr_code:
                response['qr_code'] = qr_code

        return jsonify(response), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Admin creation failed',
            'details': str(e)
        }), 500