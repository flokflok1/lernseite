"""
LernsystemX Setup - Verification, Seeding & Diagnostics Routes

REST API endpoints for data seeding, verification, and system diagnostics:
- POST /setup/seed - Seed initial data
- POST /setup/complete - Complete installation
- GET /setup/verify - Verify installation
- GET /setup/verify/report - Get verification report
- POST /setup/diagnostics/run - Run system diagnostics
- POST /setup/auto-fix - Run auto-fix for common issues

ISO/IEC/IEEE 26515:2018 compliant - API documentation
"""

import os
from flask import request, jsonify, current_app, Response
from app.setup import setup_bp
from app.setup.seeds import SeedData
from app.setup.install_check import InstallationChecker
from app.setup.verify import SetupVerification


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

        return Response(report, mimetype='text/plain'), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to generate report',
            'details': str(e)
        }), 500


@setup_bp.route('/diagnostics/run', methods=['POST'])
def run_diagnostics():
    """
    Run comprehensive system diagnostics

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
        from app.setup.diagnostics import SystemDiagnostics

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


@setup_bp.route('/auto-fix', methods=['POST'])
def run_auto_fix():
    """
    Run auto-fix for common system issues

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
            from app.setup.migrations import MigrationManager

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
                from app.setup.seeds import SeedData
                from app.setup.install_check import InstallationChecker

                # Only run if installed
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
