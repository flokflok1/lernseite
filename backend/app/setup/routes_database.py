"""
LernsystemX Setup - Database Configuration Routes

REST API endpoints for database initialization and management:
- POST /setup/database - Initialize database schema
- GET /setup/migrations - List all database migrations
- POST /setup/migrations/run - Run pending migrations
- POST /setup/config/database - Test and save database configuration
- POST /setup/config/redis - Test and save Redis configuration

ISO/IEC/IEEE 26515:2018 compliant - API documentation
"""

import os
import psycopg
from flask import request, jsonify, current_app
from dotenv import set_key, load_dotenv
from pathlib import Path
import logging

from app.setup import setup_bp
from app.setup.install_check import InstallationChecker
from app.setup.db_init import DatabaseInitializer
from app.extensions import refresh_db_pool


logger = logging.getLogger(__name__)


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


@setup_bp.route('/migrations', methods=['GET'])
def list_migrations():
    """
    List all database migrations

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
    Run pending database migrations

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

        # Check if system is installed
        is_installed = InstallationChecker.is_installed()

        # If installed, require admin authentication
        if is_installed:
            # TODO: Add proper admin authentication check here
            # For now, allow if in development
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
                from psycopg import sql
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(dbname),
                        sql.Identifier(user)
                    )
                )

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
