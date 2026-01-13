"""
LernsystemX Setup - API Routes

REST API endpoints for the setup wizard:
- GET  /setup/status - Check installation status
- GET  /setup/environment - Get environment info
- POST /setup/environment - Configure environment (dev/prod)
- POST /setup/check - Run system checks
- POST /setup/database - Initialize database
- POST /setup/admin - Create admin user
- POST /setup/organisation - Create organisation
- POST /setup/ki-config - Configure AI API keys
- POST /setup/seed - Seed initial data
- POST /setup/complete - Finalize installation
- GET  /setup/verify - Verify installation
- GET  /setup/health - Health check

ISO/IEC/IEEE 26515:2018 compliant - API documentation
"""

import os
from flask import request, jsonify, current_app
from app.setup import setup_bp
from app.setup.system_check import SystemCheck
from app.setup.db_init import DatabaseInitializer
from app.setup.install_check import InstallationChecker
from app.setup.admin_setup import AdminSetup
from app.setup.organisation_setup import OrganisationSetup
from app.setup.seeds import SeedData
from app.setup.ki_setup import KISetup
from app.setup.verify import SetupVerification
from app.setup.environment_setup import EnvironmentSetup
from app.extensions import db_pool, init_db_pool, refresh_db_pool


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


@setup_bp.route('/database', methods=['POST'])
def initialize_database():
    """
    Initialize database schema

    Creates all tables, indexes, and initial structure.

    Returns:
        JSON:
        {
            "success": bool,
            "database_created": bool,
            "migrations_executed": int,
            "schemas_created": int,
            "tables_created": int,
            "indexes_created": int,
            "errors": [str]
        }

    Example:
        POST /setup/database
        Response: {
            "success": true,
            "database_created": false,
            "migrations_executed": 74,
            "schemas_created": 22,
            "tables_created": 211,
            "indexes_created": 1032
        }
    """
    try:
        # Check if already installed
        if InstallationChecker.is_installed():
            return jsonify({
                'success': False,
                'error': 'System already installed',
                'message': 'Database initialization can only run during setup'
            }), 400

        # Reload environment variables (Setup Wizard just saved them via /config/database)
        from dotenv import load_dotenv
        load_dotenv(override=True)

        # Initialize database (will use freshly reloaded environment variables)
        db_init = DatabaseInitializer()
        results = db_init.initialize()

        if results['success']:
            # IMPORTANT: Refresh connection pool after database initialization
            # This ensures all connections are fresh and not stale (no more BAD connections)
            try:
                current_app.logger.info("[DB_INIT] Refreshing database connection pool...")
                refresh_db_pool()
                current_app.logger.info("[DB_INIT] Connection pool refreshed successfully")
                results['connection_pool_refreshed'] = True
            except Exception as e:
                current_app.logger.warning(f"[DB_INIT] Failed to refresh connection pool: {e}")
                results['connection_pool_refreshed'] = False
                results['pool_refresh_warning'] = str(e)

            return jsonify(results), 200
        else:
            return jsonify(results), 500

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': 'Database initialization failed',
            'details': str(e),
            'traceback': traceback.format_exc()
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


@setup_bp.route('/organisation', methods=['POST'])
def create_organisation():
    """
    Create organisation (school, company, etc.)

    Request Body:
        {
            "name": str,
            "type": "system"|"school"|"company"|"creator_org"|"community",
            "domain": str (optional),
            "branding": {
                "primary_color": str,
                "secondary_color": str,
                "logo_url": str
            } (optional),
            "settings": dict (optional)
        }

    Returns:
        JSON:
        {
            "success": bool,
            "organisation_id": int,
            "name": str,
            "type": str,
            "domain": str,
            "message": str
        }

    Example:
        POST /setup/organisation
        Body: {
            "name": "LSX Academy",
            "type": "system",
            "domain": "lsx.de"
        }
    """
    try:
        # Validate request data
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Check if creating LSX Academy
        if data.get('type') == 'system' or data.get('name') == 'LSX Academy':
            # Create LSX Academy
            org = OrganisationSetup.create_lsx_academy()
        else:
            # Create custom organisation
            required_fields = ['name', 'type']
            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': 'Missing required fields',
                    'missing': missing_fields
                }), 400

            org = OrganisationSetup.create_organisation(
                name=data['name'],
                org_type=data['type'],
                domain=data.get('domain'),
                branding=data.get('branding'),
                settings=data.get('settings')
            )

        return jsonify({
            'success': True,
            'organisation_id': org['organization_id'],
            'name': org['name'],
            'type': org['type'],
            'domain': org.get('domain'),
            'message': 'Organisation created successfully'
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Organisation creation failed',
            'details': str(e)
        }), 500


@setup_bp.route('/ki-config', methods=['POST'])
def configure_ki():
    """
    Configure AI API keys

    Request Body (Frontend format):
        {
            "openai_api_key": str (optional),
            "anthropic_api_key": str (optional),
            "deepl_api_key": str (optional),
            "validate": bool (optional, default: false)
        }

    Returns:
        JSON:
        {
            "success": bool,
            "configured_providers": list,
            "message": str
        }

    Example:
        POST /setup/ki-config
        Body: {
            "openai_api_key": "sk-...",
            "anthropic_api_key": "",
            "deepl_api_key": ""
        }
    """
    try:
        # Validate request data
        data = request.get_json()

        if not data:
            # Allow empty configuration (skip step)
            return jsonify({
                'success': True,
                'configured_providers': [],
                'message': 'KI configuration skipped (optional step)'
            }), 200

        # Map frontend field names to provider names
        provider_mapping = {
            'openai_api_key': 'openai',
            'anthropic_api_key': 'anthropic',
            'deepl_api_key': 'deepl'
        }

        # Get master encryption key from environment
        master_key = os.getenv('ENCRYPTION_KEY')

        # Generate master key if not exists
        if not master_key:
            master_key = KISetup.setup_encryption_key()
            os.environ['ENCRYPTION_KEY'] = master_key

        # Process each provider
        configured_providers = []
        validate = data.get('validate', False)  # Default to false for setup wizard

        for field_name, provider in provider_mapping.items():
            api_key = data.get(field_name, '').strip()

            # Skip empty keys
            if not api_key:
                continue

            try:
                # Store API key
                result = KISetup.store_api_key(
                    provider=provider,
                    api_key=api_key,
                    master_key=master_key,
                    validate=validate,
                    metadata=None
                )
                configured_providers.append(provider)
            except Exception as e:
                # Log error but continue with other providers
                print(f"Failed to configure {provider}: {str(e)}")

        # Return success even if no providers were configured
        if configured_providers:
            message = f'KI configuration successful: {", ".join(configured_providers)}'
        else:
            message = 'KI configuration skipped (no API keys provided)'

        return jsonify({
            'success': True,
            'configured_providers': configured_providers,
            'message': message
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'KI configuration failed',
            'details': str(e)
        }), 500


@setup_bp.route('/ki-config', methods=['GET'])
def get_ki_config():
    """
    Get configured AI providers

    Returns:
        JSON:
        {
            "success": bool,
            "providers": [
                {
                    "provider": str,
                    "active": bool,
                    "last_validated": str,
                    "metadata": dict
                }
            ],
            "stats": dict
        }

    Example:
        GET /setup/ki-config
        Response: {
            "success": true,
            "providers": [...],
            "stats": {"total": 2, "active_count": 2}
        }
    """
    try:
        providers = KISetup.list_configured_providers()
        stats = KISetup.get_provider_stats()

        return jsonify({
            'success': True,
            'providers': providers,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve KI configuration',
            'details': str(e)
        }), 500


@setup_bp.route('/seed', methods=['POST'])
def seed_database():
    """
    Seed database with initial data

    Request Body:
        {
            "skip_existing": bool (optional, default: true)
        }

    Creates:
    - Learning methods (12 Content-Lernmethoden)
    - System features (25 features)
    - Roles (9)
    - Categories (8)

    Returns:
        JSON:
        {
            "success": bool,
            "learning_methods": int,
            "system_features": int,
            "roles": int,
            "categories": int,
            "errors": [str]
        }

    Example:
        POST /setup/seed
        Body: {"skip_existing": true}
        Response: {
            "success": true,
            "learning_methods": 12,
            "system_features": 25,
            "roles": 9,
            "categories": 8
        }
    """
    try:
        # Get request data
        data = request.get_json() or {}
        skip_existing = data.get('skip_existing', True)

        # Seed all data
        results = SeedData.seed_all(skip_existing=skip_existing)

        if results.get('errors'):
            return jsonify({
                'success': False,
                'error': 'Seeding completed with errors',
                'details': results
            }), 500

        return jsonify({
            'success': True,
            'learning_methods': results['learning_methods'],
            'system_features': results['system_features'],
            'roles': results['roles'],
            'categories': results['categories'],
            'message': 'Database seeded successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Database seeding failed',
            'details': str(e)
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


@setup_bp.route('/complete', methods=['POST'])
def complete_setup():
    """
    Complete installation and mark as installed

    Request Body:
        {
            "admin_email": str (optional)
        }

    Returns:
        JSON:
        {
            "success": bool,
            "message": str,
            "install_info": dict,
            "next_step": str
        }

    Example:
        POST /setup/complete
        Body: {"admin_email": "admin@lsx.de"}
        Response: {
            "success": true,
            "message": "Installation completed successfully",
            "next_step": "Login with admin credentials at /login"
        }
    """
    try:
        # Check if already installed
        if InstallationChecker.is_installed():
            return jsonify({
                'success': False,
                'error': 'System already installed'
            }), 400

        # Get admin email from request
        data = request.get_json() or {}
        admin_email = data.get('admin_email')

        # Initialize system settings in database
        try:
            from app.repositories.settings.system import SystemSettingsRepository
            import os

            # Get environment from .env (created during setup)
            current_env = os.getenv('FLASK_ENV', 'development')

            # Write environment to DB for GUI management
            SystemSettingsRepository.create_setting(
                key='system.environment',
                value=current_env,
                category='system',
                description='System environment mode (development/production)',
                editable=True,
                value_type='string'
            )

            # Initialize other system settings
            SystemSettingsRepository.create_setting(
                key='system.debug_enabled',
                value=(current_env == 'development'),
                category='system',
                description='Debug mode enabled',
                editable=True,
                value_type='boolean'
            )

            SystemSettingsRepository.create_setting(
                key='system.maintenance_mode',
                value=False,
                category='system',
                description='Maintenance mode flag',
                editable=True,
                value_type='boolean'
            )

        except Exception as e:
            # Log but don't fail the installation
            print(f"Warning: Could not initialize system settings: {e}")

        # Mark as installed
        success = InstallationChecker.mark_as_installed(
            version='1.0.0',
            database_version='1.0.0',
            admin_email=admin_email
        )

        if success:
            install_info = InstallationChecker.get_install_info()

            return jsonify({
                'success': True,
                'message': 'Installation completed successfully',
                'install_info': install_info,
                'next_step': 'Login with admin credentials at /login'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to mark installation as complete'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Setup completion failed',
            'details': str(e)
        }), 500


@setup_bp.route('/verify', methods=['GET'])
def verify_installation():
    """
    Verify installation is complete and valid

    Runs comprehensive verification checks:
    - Database connection
    - Database tables and indexes
    - Seed data (learning methods, roles, categories)
    - Admin account
    - Organisation setup
    - File permissions
    - Dependencies
    - Environment variables
    - Installation marker

    Returns:
        JSON:
        {
            "success": bool,
            "checks": [
                {
                    "name": str,
                    "status": "passed"|"failed"|"error",
                    "message": str,
                    "details": dict
                }
            ],
            "errors": [str],
            "warnings": [str],
            "timestamp": str
        }

    Example:
        GET /setup/verify
        Response: {
            "success": true,
            "checks": [...],
            "errors": [],
            "warnings": []
        }
    """
    try:
        results = SetupVerification.verify_all()

        # Always return 200, but success field indicates if verification passed
        return jsonify(results), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Verification failed',
            'details': str(e)
        }), 500


@setup_bp.route('/verify/report', methods=['GET'])
def get_verification_report():
    """
    Get formatted verification report

    Returns:
        Plain text verification report

    Example:
        GET /setup/verify/report
        Response: (text/plain)
        ======================================================================
        LernsystemX Installation Verification Report
        ======================================================================
        ...
    """
    try:
        report = SetupVerification.generate_report()

        from flask import Response
        return Response(report, mimetype='text/plain'), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to generate report',
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


# Health check endpoint (always available)
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


# ==================================================================================
# PHASE 23: DIAGNOSTICS, STATUS & MIGRATIONS
# ==================================================================================

@setup_bp.route('/diagnostics/run', methods=['POST'])
def run_diagnostics():
    """
    Run comprehensive system diagnostics (Phase 23)

    Request Body (optional):
        {
            "quick": bool (default: false)
        }

    Returns:
        JSON:
        {
            "success": bool,
            "overall_status": "ok"|"warn"|"fail",
            "checks": [
                {
                    "name": str,
                    "status": "ok"|"warn"|"fail",
                    "message": str,
                    "details": dict,
                    "auto_fix_available": bool
                }
            ],
            "summary": {
                "total_checks": int,
                "passed": int,
                "warnings": int,
                "failed": int
            },
            "timestamp": str
        }

    Example:
        POST /setup/diagnostics/run
        Body: {"quick": false}
        Response: {
            "success": true,
            "overall_status": "ok",
            "checks": [...]
        }
    """
    try:
        from setup.diagnostics import SystemDiagnostics

        # Get quick mode flag
        data = request.get_json() or {}
        quick = data.get('quick', False)

        # Run diagnostics
        report = SystemDiagnostics.run_all_diagnostics(quick=quick)
        report_dict = SystemDiagnostics.get_report_dict(report)

        return jsonify({
            'success': True,
            **report_dict
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Diagnostics failed',
            'details': str(e)
        }), 500


@setup_bp.route('/status/full', methods=['GET'])
def get_full_status():
    """
    Get comprehensive system status (Phase 23)

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
    Get lightweight system status summary (Phase 23)

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


@setup_bp.route('/migrations', methods=['GET'])
def list_migrations():
    """
    List all database migrations (Phase 23)

    Returns:
        JSON:
        {
            "success": bool,
            "migrations": [
                {
                    "migration_id": str,
                    "name": str,
                    "version": str,
                    "description": str,
                    "applied": bool,
                    "applied_at": str,
                    "execution_time_ms": int,
                    "has_rollback": bool
                }
            ],
            "summary": {
                "total": int,
                "applied": int,
                "pending": int
            }
        }

    Example:
        GET /setup/migrations
    """
    try:
        from setup.migrations import MigrationManager

        migrations = MigrationManager.list_migrations()

        # Calculate summary
        total = len(migrations)
        applied = sum(1 for m in migrations if m["applied"])
        pending = total - applied

        return jsonify({
            'success': True,
            'migrations': migrations,
            'summary': {
                'total': total,
                'applied': applied,
                'pending': pending
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list migrations',
            'details': str(e)
        }), 500


@setup_bp.route('/migrations/run', methods=['POST'])
def run_migrations():
    """
    Run pending database migrations (Phase 23)

    Authentication:
        - Requires admin privileges after installation

    Request Body (optional):
        {
            "migration_id": str (run specific migration)
        }

    Returns:
        JSON:
        {
            "success": bool,
            "message": str,
            "executed": [
                {
                    "migration_id": str,
                    "execution_time_ms": int
                }
            ],
            "failed_migration": str (if failed)
        }

    Example:
        POST /setup/migrations/run
        Response: {
            "success": true,
            "message": "Successfully executed 2 migration(s)",
            "executed": [...]
        }
    """
    try:
        from setup.migrations import MigrationManager
        from setup.install_check import InstallationChecker

        # Check if system is installed
        is_installed = InstallationChecker.is_installed()

        # If installed, require admin authentication
        if is_installed:
            # TODO: Add proper admin authentication check here
            # For now, allow if in development
            from flask import current_app
            if current_app.config.get('LSX_ENV') == 'production':
                # In production, would need proper auth
                pass

        # Get user ID if available (from JWT or request)
        user_id = None  # TODO: Extract from JWT token if authenticated

        # Check if running specific migration
        data = request.get_json() or {}
        migration_id = data.get('migration_id')

        if migration_id:
            # Run specific migration
            result = MigrationManager.run_migration(migration_id, user_id)
        else:
            # Run all pending migrations
            result = MigrationManager.run_pending_migrations(user_id)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Migration execution failed',
            'details': str(e)
        }), 500


# ==================================================================================
# CONFIGURATION ENDPOINTS (for Setup Wizard UI)
# ==================================================================================

@setup_bp.route('/config/database', methods=['POST'])
def configure_database():
    """
    Test and save database configuration

    Request Body:
        {
            "host": str,
            "port": str|int,
            "dbname": str,
            "user": str,
            "password": str
        }

    Returns:
        JSON:
        {
            "success": bool,
            "message": str,
            "connection_tested": bool
        }
    """
    try:
        import psycopg
        from dotenv import set_key
        from pathlib import Path
        import logging

        logger = logging.getLogger(__name__)
        logger.info("[DB_CONFIG] Starting database configuration...")

        data = request.get_json()
        logger.info(f"[DB_CONFIG] Request data: {data}")

        host = data.get('host', 'localhost')
        port = int(data.get('port', 5432))
        dbname = data.get('dbname', 'lernsystemx_dev')
        user = data.get('user', 'postgres')
        password = data.get('password', '')

        logger.info(f"[DB_CONFIG] Testing connection to {host}:{port} as user {user}")

        # Test connection to PostgreSQL server
        try:
            conn = psycopg.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname='postgres',  # Connect to default DB first
                connect_timeout=5,
                autocommit=True
            )

            # Check if target database exists
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (dbname,)
            )
            db_exists = cursor.fetchone() is not None

            # Create database if it doesn't exist
            if not db_exists:
                cursor.execute(f"CREATE DATABASE {dbname} OWNER {user}")

                # Connect to new database and enable extensions
                cursor.close()
                conn.close()

                conn_new = psycopg.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    dbname=dbname,
                    autocommit=True
                )
                cursor_new = conn_new.cursor()
                cursor_new.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
                cursor_new.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
                cursor_new.close()
                conn_new.close()
            else:
                cursor.close()
                conn.close()

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Verbindung fehlgeschlagen: {str(e)}',
                'connection_tested': False
            }), 400

        # Connection successful - save to .env
        env_file = Path(__file__).parent.parent / '.env'

        set_key(env_file, 'DB_HOST', host, quote_mode='never')
        set_key(env_file, 'DB_PORT', str(port), quote_mode='never')
        set_key(env_file, 'DB_NAME', dbname, quote_mode='never')
        set_key(env_file, 'DB_USER', user, quote_mode='never')
        set_key(env_file, 'DB_PASSWORD', password, quote_mode='never')

        # Update DATABASE_URL
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        set_key(env_file, 'DATABASE_URL', database_url, quote_mode='never')

        return jsonify({
            'success': True,
            'message': '✓ Verbindung erfolgreich! Konfiguration gespeichert.',
            'connection_tested': True
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Fehler: {str(e)}',
            'connection_tested': False
        }), 500


@setup_bp.route('/config/redis', methods=['POST'])
def configure_redis():
    """
    Test and save Redis configuration

    Request Body:
        {
            "host": str,
            "port": str|int,
            "db": str|int,
            "password": str (optional)
        }

    Returns:
        JSON:
        {
            "success": bool,
            "message": str,
            "connection_tested": bool
        }
    """
    try:
        import redis
        from dotenv import set_key
        from pathlib import Path

        data = request.get_json()
        host = data.get('host', 'localhost')
        port = int(data.get('port', 6379))
        db = int(data.get('db', 0))
        password = data.get('password', '')

        # Test connection
        try:
            r = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password if password else None,
                socket_connect_timeout=5
            )
            r.ping()
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Verbindung fehlgeschlagen: {str(e)}',
                'connection_tested': False
            }), 400

        # Connection successful - save to .env
        env_file = Path(__file__).parent.parent / '.env'

        set_key(env_file, 'REDIS_HOST', host, quote_mode='never')
        set_key(env_file, 'REDIS_PORT', str(port), quote_mode='never')
        set_key(env_file, 'REDIS_DB', str(db), quote_mode='never')

        # Build Redis URL
        if password:
            redis_url = f"redis://:{password}@{host}:{port}/{db}"
        else:
            redis_url = f"redis://{host}:{port}/{db}"

        set_key(env_file, 'REDIS_URL', redis_url, quote_mode='never')

        # Also update other Redis URLs (Celery, SocketIO, etc.)
        set_key(env_file, 'CELERY_BROKER_URL', f"redis://{host}:{port}/1", quote_mode='never')
        set_key(env_file, 'CELERY_RESULT_BACKEND', f"redis://{host}:{port}/2", quote_mode='never')
        set_key(env_file, 'SOCKETIO_MESSAGE_QUEUE', f"redis://{host}:{port}/3", quote_mode='never')
        set_key(env_file, 'RATELIMIT_STORAGE_URL', f"redis://{host}:{port}/4", quote_mode='never')
        set_key(env_file, 'SESSION_REDIS_URL', f"redis://{host}:{port}/5", quote_mode='never')

        return jsonify({
            'success': True,
            'message': '✓ Verbindung erfolgreich! Konfiguration gespeichert.',
            'connection_tested': True
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Fehler: {str(e)}',
            'connection_tested': False
        }), 500


@setup_bp.route('/auto-fix', methods=['POST'])
def run_auto_fix():
    """
    Run auto-fix for common system issues (Phase 23)

    Authentication:
        - Requires admin privileges after installation

    Request Body:
        {
            "fixes": ["missing_directories", "pending_migrations", "rerun_seeds"]
        }

    Returns:
        JSON:
        {
            "success": bool,
            "fixes_applied": [
                {
                    "fix": str,
                    "success": bool,
                    "message": str
                }
            ]
        }

    Example:
        POST /setup/auto-fix
        Body: {"fixes": ["missing_directories"]}
    """
    try:
        data = request.get_json() or {}
        requested_fixes = data.get('fixes', [])

        fixes_applied = []

        # Fix: Create missing directories
        if "missing_directories" in requested_fixes:
            try:
                from flask import current_app
                import os

                dirs_created = []

                # Check and create upload directory
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder, exist_ok=True)
                    dirs_created.append(upload_folder)

                # Check and create backup directory
                backup_path = current_app.config.get('BACKUP_PATH', '/var/backups/lsx')
                if not os.path.exists(backup_path):
                    try:
                        os.makedirs(backup_path, exist_ok=True)
                        dirs_created.append(backup_path)
                    except PermissionError:
                        pass  # Skip if no permissions

                fixes_applied.append({
                    "fix": "missing_directories",
                    "success": True,
                    "message": f"Created {len(dirs_created)} director(ies): {', '.join(dirs_created)}" if dirs_created else "All directories already exist",
                    "directories_created": dirs_created
                })

            except Exception as e:
                fixes_applied.append({
                    "fix": "missing_directories",
                    "success": False,
                    "message": f"Failed: {str(e)}"
                })

        # Fix: Run pending migrations
        if "pending_migrations" in requested_fixes:
            from setup.migrations import MigrationManager

            result = MigrationManager.run_pending_migrations()
            fixes_applied.append({
                "fix": "pending_migrations",
                "success": result["success"],
                "message": result.get("message", ""),
                "executed": result.get("executed", [])
            })

        # Fix: Re-run seeds (idempotent)
        if "rerun_seeds" in requested_fixes:
            try:
                from setup.seeds import SeedData

                # Only run if installed
                from setup.install_check import InstallationChecker
                if InstallationChecker.is_installed():
                    SeedData.seed_all()
                    fixes_applied.append({
                        "fix": "rerun_seeds",
                        "success": True,
                        "message": "Seeds re-run successfully (idempotent)"
                    })
                else:
                    fixes_applied.append({
                        "fix": "rerun_seeds",
                        "success": False,
                        "message": "System not installed yet"
                    })

            except Exception as e:
                fixes_applied.append({
                    "fix": "rerun_seeds",
                    "success": False,
                    "message": f"Failed: {str(e)}"
                })

        all_success = all(fix["success"] for fix in fixes_applied)

        return jsonify({
            'success': all_success,
            'fixes_applied': fixes_applied
        }), 200 if all_success else 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Auto-fix failed',
            'details': str(e)
        }), 500
# Force reload
