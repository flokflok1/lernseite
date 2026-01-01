"""
LernsystemX Backend - Application Entry Point

This module serves as the main entry point for the Flask application.
Supports both development and production deployment.

ISO/IEC/IEEE 26515:2018 compliant - Developer documentation maintained
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from app import create_app, socketio
from app.extensions import db_pool, celery


# Create Flask application instance
app = create_app()


def setup_logging():
    """
    Configure application logging

    Implements structured logging according to ISO 9001 quality standards.
    Logs are rotated to prevent disk space issues.
    """
    if not app.debug:
        # Ensure logs directory exists
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # File handler with rotation
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )

        # Set log format
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        file_handler.setFormatter(formatter)

        # Set log level from config
        log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(log_level)
        app.logger.info('LernsystemX Backend startup')


# Setup logging
setup_logging()


@app.shell_context_processor
def make_shell_context():
    """
    Add variables to Flask shell context for easier debugging

    Returns:
        dict: Context variables for Flask shell
    """
    return {
        'db_pool': db_pool,
        'app': app,
        'celery': celery
        # Repositories and Models will be added in future phases
    }


@app.cli.command()
def init_db():
    """
    Initialize database with tables

    Usage: flask init-db

    Note: Using pure psycopg - database schema is managed via SQL migration scripts
    Run the Setup Wizard at /setup instead
    """
    print("Database initialization is handled by the Setup Wizard")
    print("Navigate to http://localhost:5000/setup/status to begin installation")
    print("\nFor manual database initialization, run SQL scripts in:")
    print("  - backend/database/schema/")
    print("  - backend/database/seeds/")


@app.cli.command()
def seed_db():
    """
    Seed database with initial data

    Usage: flask seed-db
    """
    from datetime import datetime

    # This will be implemented when models are created
    print("Database seeding will be implemented with models")
    print("Run this command after Phase 3 (Database Models)")


@app.cli.command()
def create_admin():
    """
    Create an admin user

    Usage: flask create-admin
    """
    # This will be implemented when User model is created
    print("Admin user creation will be implemented with User model")
    print("Run this command after Phase 3 (Database Models)")


@app.cli.command()
def test():
    """
    Run unit tests

    Usage: flask test
    """
    import pytest
    result = pytest.main(['-v', 'tests/'])
    sys.exit(result)


@app.cli.command()
def routes():
    """
    Display all registered routes

    Usage: flask routes
    """
    print("\nRegistered Routes:")
    print("-" * 80)
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        print(f"{rule.endpoint:50s} {methods:20s} {rule.rule}")
    print("-" * 80)


if __name__ == '__main__':
    """
    Application entry point

    For Development:
        python run.py

    For Production (use Gunicorn):
        gunicorn -w 4 -b 0.0.0.0:5000 --worker-class eventlet run:app

    For WebSocket Support (Production):
        gunicorn -w 1 -b 0.0.0.0:5000 --worker-class eventlet -k eventlet run:app
    """
    # Get configuration
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'

    app.logger.info(f'Starting LernsystemX Backend on port {port}')
    app.logger.info(f'Debug mode: {debug}')

    # Run with SocketIO support
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=debug,
        log_output=debug,
        allow_unsafe_werkzeug=True  # Allow Werkzeug in development
    )
